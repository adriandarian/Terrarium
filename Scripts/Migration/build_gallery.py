"""Create one isolated, labeled migration review level in the Unreal editor."""
import json
import math
from pathlib import Path
import unreal

assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
ROOT = Path(unreal.Paths.project_dir())
PKG = '/Game/Terrarium/Migration'
kind = (ROOT / 'Saved/migration-gallery.txt').read_text().strip()
assert kind in ['Architecture', 'Characters', 'Environment', 'References', 'Surfaces']
level_path = PKG + '/Maps/' + kind
existing = unreal.EditorAssetLibrary.does_asset_exist(level_path)
assert not (ROOT / 'Docs/AssetMigration' / (kind.lower() + '-gallery.json')).exists(), 'Completed gallery exists; inspect before replacing'
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not existing:
    assert levels.load_level('/Game/Terrarium/Maps/RenderBaseline')
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world, level_path)
# save_map writes a copy; explicitly load that copy before making any edits.
assert levels.load_level(level_path)
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
for label in ['Baseline_StoneCube', 'Baseline_ClaySphere']:
    actors.destroy_actor(scene[label])
records = []

def mesh(label, path, pos, scale=(1, 1, 1), material=None, rotation=None):
    asset = unreal.load_asset(path)
    assert isinstance(asset, unreal.StaticMesh), path
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*pos))
    a.set_actor_label(label)
    a.set_folder_path('Migration/' + kind)
    a.static_mesh_component.set_static_mesh(asset)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if rotation:
        a.set_actor_rotation(unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]), False)
    if material:
        mat = unreal.load_asset(material)
        assert mat, material
        a.static_mesh_component.set_material(0, mat)
    records.append({'label': label, 'mesh': path, 'material_override': material})
    return a

def label(text, pos, size):
    a = actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(*pos), unreal.Rotator(pitch=90, yaw=-90, roll=0))
    a.set_actor_label('Label_' + text)
    a.set_folder_path('Migration/Labels')
    a.text_render.set_text(text)
    a.text_render.set_world_size(size)
    a.text_render.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    a.text_render.set_text_render_color(unreal.Color(242, 232, 206, 255))

imports = json.loads((ROOT / 'Docs/AssetMigration/imported.json').read_text())
if kind in ['References', 'Surfaces']:
    rows = imports if kind == 'References' else [r for r in imports if r['surface_material']]
    cols = 7
    step_x, step_y = 480, 530
    for i, r in enumerate(rows):
        x, y = (i % cols) * step_x, (i // cols) * step_y
        # Original PNG proportions are preserved on the reference boards.
        import struct
        width, height = struct.unpack('>II', (ROOT / 'SourceAssets/Voxel' / r['source']).read_bytes()[16:24])
        ratio = width / height
        sx, sy = (3.8, 3.8 / ratio) if ratio >= 1 else (3.8 * ratio, 3.8)
        material = r['reference_material'] if kind == 'References' else r['surface_material']
        mesh(r['source'], '/Engine/BasicShapes/Plane', (x, y, 2), (sx, sy, 1), material)
        label(r['source'].removesuffix('.png'), (x, y-220, 3), 14)
elif kind in ['Architecture', 'Characters']:
    filename = 'structures-built.json' if kind == 'Architecture' else 'characters-built.json'
    rows = json.loads((ROOT / 'Docs/AssetMigration' / filename).read_text())
    cols, step_x, step_y = (3, 1550, 1700) if kind == 'Architecture' else (4, 410, 570)
    for i, r in enumerate(rows):
        x, y = (i % cols) * step_x, (i // cols) * step_y
        a = mesh(r['name'], r['asset'], (x, y, 0))
        origin, extent = a.get_actor_bounds(False)
        assert abs(origin.z - extent.z) < 1.0, (r['name'], 'ground pivot', origin.z - extent.z)
        label(r['source'], (x, y-step_y*.39, 3), 32 if kind == 'Architecture' else 15)
else:
    # Reuse inspected existing packages; these are counterparts, not claimed exact reconstructions.
    names = ['SM_Cottage_v6_Detail', 'SM_Tree_v3_Detail', 'SM_Bush_v2_Detail', 'SM_WheatPatch_v2_Detail',
             'SM_PlankBridge_v4_Detail', 'SM_RockCluster_Detail', 'SM_MeadowTile_v5_Detail2',
             'SM_PathTile_v4', 'SM_CliffColumn_v6A_Detail', 'SM_StoneStairs_v3_Detail',
             'SM_WaterTile_v4_Detail', 'SM_CliffMoss_v1_Detail', 'SM_GroundPlants_v2_Detail',
             'SM_GardenBed_v3_Detail', 'SM_GardenWell_v2_Detail', 'SM_Reeds_Detail']
    # Fail visibly if an expected counterpart is absent; no silent omissions.
    rows = names
    cols, step_x, step_y = 4, 1100, 1250
    for i, name in enumerate(names):
        x, y = (i % cols) * step_x, (i // cols) * step_y
        a = mesh(name, '/Game/Terrarium/Meshes/' + name, (x, y, 0))
        origin, extent = a.get_actor_bounds(False)
        a.set_actor_location(unreal.Vector(x, y, extent.z-origin.z), False, False)
        label(name.removeprefix('SM_'), (x, y-450, 3), 23)

row_count = math.ceil(len(rows) / cols)
cx, cy = (min(cols, len(rows))-1)*step_x/2, (row_count-1)*step_y/2
width, depth = cols*step_x+500, row_count*step_y+500
floor = scene['Baseline_Ground']
floor.set_actor_location(unreal.Vector(cx, cy, -50), False, False)
floor.set_actor_scale3d(unreal.Vector(width/100, depth/100, 1))
camera = scene['Baseline_Orthographic_Review']
pitch, yaw = (-88, 90) if kind in ['References', 'Surfaces'] else (-48, 90)
distance = max(width, depth)*1.6
forward = unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)), math.cos(math.radians(pitch))*math.sin(math.radians(yaw)), math.sin(math.radians(pitch)))
camera.set_actor_location(unreal.Vector(cx, cy, 100)-forward*distance, False, False)
camera.set_actor_rotation(unreal.Rotator(pitch=pitch, yaw=yaw, roll=0), False)
camera.camera_component.set_ortho_width(max(width, depth*1.6*.85))
camera.camera_component.set_editor_property('aspect_ratio', 1.6)
levels.pilot_level_actor(camera)
levels.set_exact_camera_view(True)
levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
# Reopen the saved package and check the actual references, rather than only spawn results.
assert levels.load_level(level_path)
loaded = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
for record in records:
    a = loaded[record['label']]
    assert a.static_mesh_component.static_mesh.get_path_name().split('.')[0] == record['mesh'], record
    material = a.static_mesh_component.get_material(0)
    assert material, record
    if record['material_override']:
        assert material.get_path_name().split('.')[0] == record['material_override'], record
camera = loaded['Baseline_Orthographic_Review']
levels.pilot_level_actor(camera)
levels.set_exact_camera_view(True)
levels.editor_set_game_view(True)
(ROOT / 'Docs/AssetMigration' / (kind.lower() + '-gallery.json')).write_text(json.dumps({'map': level_path, 'count': len(records), 'saved_and_reopened': True, 'records': records}, indent=2))
unreal.log('MIGRATION_GALLERY_VALIDATED ' + kind)
