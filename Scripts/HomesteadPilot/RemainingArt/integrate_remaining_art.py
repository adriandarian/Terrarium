"""Coordinator-only Unreal import, LOD readback and transform-preserving admission.

Run through the verified Terrarium editor with StartingHome loaded and PIE stopped.
No source/baseline assets are modified. Only isolated RemainingArt assets and the
current working level are saved. Progress receipts allow recovery after a failure.
"""
import unreal, json, hashlib
from pathlib import Path

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
DOC = ROOT / 'Docs/HomesteadPilot/RemainingArt'
DEST = '/Game/Terrarium/HomesteadPilot/RemainingArt'
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
at = unreal.AssetToolsHelpers.get_asset_tools()
manifest = json.loads((DOC / 'manifest.json').read_text())
assert manifest['assets'], 'At least one completed source required'
specs = list(manifest['assets'])
for key in ['BlueShed', 'Tower']:
    specs.append({'name': key, 'baseline_mesh': '/Game/Terrarium/Environment/Meshes/SM_Env_' + key,
        'collision': 'complex_as_simple', 'screen_sizes': [1., .20, .065], 'unreal_reduction': [1., .72, .42]})

def vec(v): return [v.x, v.y, v.z]
def transform(actor):
    t = actor.get_actor_transform()
    return {'location': vec(t.translation), 'scale': vec(t.scale3d),
            'quaternion': [t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w]}

rows = []
for spec in specs:
    key = spec['name']; name = 'SM_HP_' + key
    baseline = unreal.load_asset(spec['baseline_mesh']); assert isinstance(baseline, unreal.StaticMesh)
    path = DEST + '/Meshes/' + name
    if spec.get('unreal_reduction'):
        mesh = unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset(spec['baseline_mesh'], path)
    else:
        source = ROOT / spec['lods'][0]['fbx']
        assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == spec['lods'][0]['sha256']
        opts = unreal.FbxImportUI(); opts.import_mesh = True; opts.import_materials = False
        opts.import_textures = False; opts.import_as_skeletal = False; opts.import_animations = False
        opts.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        d = opts.static_mesh_import_data
        d.combine_meshes = True; d.generate_lightmap_u_vs = False; d.auto_generate_collision = False
        d.convert_scene = True; d.convert_scene_unit = True
        d.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        task = unreal.AssetImportTask(); task.filename = str(source); task.destination_path = DEST + '/Meshes'
        task.destination_name = name; task.automated = True; task.replace_existing = True; task.save = False
        task.options = opts; task.factory = unreal.FbxFactory(); at.import_asset_tasks([task])
        mesh = unreal.load_asset(path)
    assert isinstance(mesh, unreal.StaticMesh), path
    # Slot order is retained by all exported LODs; preserve the already-reviewed UE
    # shaders, including collectible metal/glass/emission settings, in private copies.
    assert len(mesh.static_materials) == len(baseline.static_materials), key
    material_rows = []
    for index, oldslot in enumerate(baseline.static_materials):
        old = oldslot.get_editor_property('material_interface'); assert old
        material_path = DEST + '/Materials/' + key + '_' + str(index) + '_' + old.get_name()
        material = unreal.load_asset(material_path) or unreal.EditorAssetLibrary.duplicate_asset(old.get_path_name().split('.')[0], material_path)
        assert material
        mesh.set_material(index, material)
        assert unreal.EditorAssetLibrary.save_loaded_asset(material)
        material_rows.append({'index': index, 'source': old.get_path_name(), 'pilot': material.get_path_name()})
    before = baseline.get_bounding_box(); after = mesh.get_bounding_box()
    bounds_error = max(abs(a-b) for a,b in zip(vec(before.min)+vec(before.max), vec(after.min)+vec(after.max)))
    assert bounds_error < .15, (key, 'Original footprint/pivot changed', bounds_error)
    sub.remove_lods(mesh)
    if spec.get('unreal_reduction'):
        options = unreal.StaticMeshReductionOptions()
        options.set_editor_property('auto_compute_lod_screen_size', False)
        options.set_editor_property('reduction_settings', [unreal.StaticMeshReductionSettings(percent_triangles=f, screen_size=s)
            for f,s in zip(spec['unreal_reduction'], spec['screen_sizes'])])
        assert sub.set_lods(mesh, options) == 3
    else:
        for lod in spec['lods'][1:]:
            source = ROOT / lod['fbx']
            assert hashlib.sha256(source.read_bytes()).hexdigest() == lod['sha256']
            assert sub.import_lod(mesh, lod['level'], str(source)) == lod['level']
    assert sub.get_lod_count(mesh) == 3
    assert sub.set_lod_screen_sizes(mesh, spec['screen_sizes'])
    counts = [mesh.get_num_triangles(i) for i in range(3)]
    assert counts[0] > counts[1] > counts[2] > 0, (key, counts)
    nanite = sub.get_nanite_settings(mesh); nanite.set_editor_property('enabled', False)
    sub.set_nanite_settings(mesh, nanite, True)
    body = mesh.get_editor_property('body_setup'); assert body
    inherited_body = baseline.get_editor_property('body_setup'); assert inherited_body
    body.modify()
    # Collision is inherited behavior, independent of visual LOD or prop role.
    # Copy the baseline aggregate rather than infer simple/complex policy from a
    # family name. Unreal structs are copied by value into this private body.
    for property_name in ('collision_trace_flag', 'double_sided_geometry', 'agg_geom'):
        body.set_editor_property(property_name, inherited_body.get_editor_property(property_name))
    mesh.set_editor_property('lod_for_collision', baseline.get_editor_property('lod_for_collision'))
    assert sub.get_simple_collision_count(mesh) == sub.get_simple_collision_count(baseline)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    placements = []
    for actor in actors.get_all_level_actors():
        for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
            existing = comp.get_editor_property('static_mesh')
            if not existing or existing.get_path_name().split('.')[0] not in (spec['baseline_mesh'], path): continue
            assert not isinstance(comp, unreal.InstancedStaticMeshComponent), 'Unexpected instanced architecture requires deliberate migration'
            old_transform = transform(actor)
            inherited_profile = comp.get_collision_profile_name()
            inherited_enabled = comp.get_collision_enabled()
            inherited_overlaps = comp.get_editor_property('generate_overlap_events')
            comp.set_static_mesh(mesh)
            comp.set_editor_property('forced_lod_model', 0)
            comp.set_collision_profile_name(inherited_profile)
            comp.set_collision_enabled(inherited_enabled)
            comp.set_editor_property('generate_overlap_events', inherited_overlaps)
            assert transform(actor) == old_transform
            placements.append({'actor': actor.get_actor_label(), 'transform': old_transform})
    assert placements, (key, 'Expected inherited scene actor not found')
    rows.append({'name': key, 'mesh': mesh.get_path_name(), 'lod_count': sub.get_lod_count(mesh), 'triangles': counts,
        'screen_sizes': list(sub.get_lod_screen_sizes(mesh)), 'bounds_error_cm': bounds_error,
        'collision': str(body.get_editor_property('collision_trace_flag')), 'collision_policy': 'inherited baseline body and preserved component settings',
        'collision_lod': mesh.get_editor_property('lod_for_collision'), 'simple_collision_primitives': sub.get_simple_collision_count(mesh),
        'materials': material_rows, 'placements': placements,
        'lod_method': 'Unreal reduction of preserved source mesh' if spec.get('unreal_reduction') else 'Three actual Blender FBX meshes'})
    (DOC / 'unreal-integration-progress.json').write_text(json.dumps({'assets': rows}, indent=2))
    unreal.log('RemainingArt integrated %s: %s' % (key, counts))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(DOC / 'unreal-integration.json').write_text(json.dumps({'assets': rows, 'scene_actor_transforms_preserved': True,
    'baseline_assets_modified': False, 'forced_lod': 0,
    'validation_scope': 'Asset LOD/count/bounds/material/transform readback. Visual, traversal and saved-map verification are coordinator follow-ups.'}, indent=2))
