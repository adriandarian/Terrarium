"""Verify the latest civic hall and update only its architecture gallery entry."""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir())
assert Path(unreal.Paths.get_project_file_path()).name == 'Terrarium.uproject'
sys.path.insert(0, str(root / 'Scripts/Reconstruction'))
import build_galleries as g

rows = [json.loads(p.read_text()) for p in (root / 'Docs/Reconstruction/Builds').glob('SM_Recon_CivicHall_R*.json')]
row = max(rows, key=lambda r: r['revision'])
revision = row['revision']


def inspect_mesh(path, check_normals=False):
    asset = unreal.load_asset(path)
    mesh = unreal.DynamicMesh()
    _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(
        asset, mesh, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD())
    assert outcome == unreal.GeometryScriptOutcomePins.SUCCESS
    positions = hashlib.sha256()
    invalid = 0
    for i in range(mesh.get_triangle_count()):
        valid, a, b, c = mesh.get_triangle_positions(i)
        assert valid
        positions.update(struct.pack('<9d', *[v for p in (a, b, c) for v in (p.x, p.y, p.z)]))
        if check_normals:
            ab = (c.x-a.x, c.y-a.y, c.z-a.z)
            ac = (b.x-a.x, b.y-a.y, b.z-a.z)
            n = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
            length = math.sqrt(sum(x*x for x in n))
            _, n1, n2, n3, valid_normals = mesh.get_triangle_normals(i)
            if not valid_normals or length == 0 or any(sum(x*y for x,y in zip(n,(v.x,v.y,v.z)))/length < .99 for v in (n1,n2,n3)):
                invalid += 1
    _, colors, valid, gaps = unreal.GeometryScript_VertexColors.get_mesh_per_vertex_colors(mesh)
    assert valid and not gaps
    palette = hashlib.sha256()
    for c in unreal.GeometryScript_List.convert_color_list_to_array(colors):
        palette.update(struct.pack('<4d', c.r, c.g, c.b, c.a))
    return {'triangles': mesh.get_triangle_count(), 'triangle_positions_sha256': positions.hexdigest(),
            'vertex_colors_sha256': palette.hexdigest(), 'normal_errors': invalid if check_normals else None}


candidate = inspect_mesh(row['asset'], True)
assert candidate['normal_errors'] == 0
assert candidate['triangles'] == row['triangles']
assert g.material_paths(unreal.load_asset(row['asset'])) == [row['material']]
if revision == 4:
    original = inspect_mesh(row['source_geometry_asset'])
    for field in ('triangles', 'triangle_positions_sha256', 'vertex_colors_sha256'):
        assert original[field] == candidate[field], field
    assert g.material_paths(unreal.load_asset(row['source_geometry_asset'])) != [row['material']]
else:
    assert row['added_rear_center_windows'] == 4
    assert row['geometry_and_colors_outside_rear_facade_unchanged'] if revision==5 else row['geometry_and_colors_outside_entrance_foundation_unchanged']
    assert g.material_paths(unreal.load_asset(g.PKG + '/Meshes/SM_Recon_CivicHall_R4')) == [row['material']]

assert g.current_is(g.REVIEW) or g.current_is(g.PKG + '/Maps/Architecture')
path = g.PKG + '/Maps/Architecture'
assert g.LEVELS.load_level(path)
scene = {a.get_actor_label(): a for a in g.ACTORS.get_all_level_actors()}
before = {name: g.package_path(a.static_mesh_component.static_mesh) for name,a in scene.items() if name.startswith('Model_')}
assert len(before) == 7
report_path = g.OUT / 'Architecture.json'
report = json.loads(report_path.read_text())
record = next(r for r in report['models'] if r['key'] == 'civic_hall')
old_label = record['label']
a = scene[old_label]
old_bounds = g.actor_bounds(a)
old_transform = str(a.get_actor_transform())
a.static_mesh_component.set_static_mesh(unreal.load_asset(row['asset']))
label = 'Model_civic_hall_R' + str(revision)
a.set_actor_label(label)
caption = 'civic hall  |  R' + str(revision)
scene[record['text_actor']].text_render.set_text(caption)
new_bounds=g.actor_bounds(a)
if revision<6:
    assert new_bounds == old_bounds
else:
    assert abs(new_bounds['min'][2])<.02
    assert all(abs(new_bounds[side][i]-old_bounds[side][i])<12 for side in ('min','max') for i in range(3))
record.update(label=label, text=caption, mesh=row['asset'], revision=revision, triangles=row['triangles'],
              receipt='Docs/Reconstruction/Builds/' + row['name'] + '.json',
              materials=[row['material']],world_bounds_cm=new_bounds)
assert g.LEVELS.save_current_level()
assert g.LEVELS.load_level(path)
scene = {a.get_actor_label(): a for a in g.ACTORS.get_all_level_actors()}
for name, asset in before.items():
    assert g.package_path(scene[label if name == old_label else name].static_mesh_component.static_mesh) == (row['asset'] if name == old_label else asset)
assert str(scene[label].get_actor_transform()) == old_transform
assert g.actor_bounds(scene[label]) == new_bounds
assert g.material_paths(scene[label].static_mesh_component.static_mesh) == [row['material']]
report_path.write_text(json.dumps(report, indent=2))
g.ACTORS.set_selected_level_actors([scene[label]])
verification = {'project': unreal.Paths.get_project_file_path(), 'asset': row['asset'],
                'material': row['material'], 'saved_candidate': candidate,
                'saved_and_reopened_gallery': True,
                'other_six_gallery_mesh_bindings_unchanged': True, 'transform_unchanged': True,
                'saved_bounds_match_candidate': True, 'world_bounds_cm':new_bounds,
                'native_front_and_back_captures': 'Docs/Reconstruction/Renders/CivicHall-R' + str(revision) + '-capture.json',
                'user_acceptance': 'pending', 'gameplay_tested': False}
if revision == 4:
    verification.update(source_geometry=original, geometry_and_vertex_colors_identical=True)
else:
    verification.update(added_rear_center_windows=4, warm_R4_material_preserved=True)
    if revision==5:verification['geometry_and_colors_outside_rear_facade_unchanged']=True
    else:
        verification['geometry_and_colors_outside_entrance_foundation_unchanged']=True
        verification['entrance_foundation_details']=row['entrance_foundation_details']
suffix = 'color' if revision == 4 else 'windows' if revision==5 else 'entrance'
(root / ('Docs/Reconstruction/civic-hall-' + suffix + '-verification.json')).write_text(json.dumps(verification, indent=2))
unreal.log('CIVIC_HALL_VERIFIED_AND_GALLERY_SAVED R' + str(revision))
