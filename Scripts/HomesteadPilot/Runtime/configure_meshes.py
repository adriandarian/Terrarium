"""Install actual custom/generated LODs and accurate static collision in editor.

Root writes mesh-plan.json after import. This deliberately refuses shared baseline
assets. Every custom LOD source is imported, then all counts and thresholds are read
back from Unreal; source manifest counts are not treated as runtime evidence.
"""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'
plan_path = OUT / 'mesh-plan.json'
if plan_path.exists():
    PLAN = json.loads(plan_path.read_text())
else:
    imports = json.loads((OUT.parent / 'imports.json').read_text())
    PLAN = {'meshes': []}
    for family in imports:
        for row in family['meshes']:
            thin = any(x in row['name'].lower() for x in ['fence', 'tree'])
            decorative = any(x in row['name'].lower() for x in ['water', 'flower', 'grassclump', 'groundcover'])
            PLAN['meshes'].append({'asset': row['mesh'], 'lods': row.get('lod_sources', []),
                'screen_sizes': [1., .18, .06] if thin else [1., .30, .10],
                'retained_triangles': [1., .75, .50] if thin else [1., .55, .25],
                'collision': 'none' if decorative else 'complex_as_simple'})
    plan_path.write_text(json.dumps(PLAN, indent=2), encoding='utf-8')
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
filter_path = OUT / 'configure-only.json'
only = {path.split('.')[0] for path in json.loads(filter_path.read_text())} if filter_path.exists() else None
if only is not None:
    assert only and only.issubset({row['asset'].split('.')[0] for row in PLAN['meshes']}), 'Unknown configure-only mesh'
rows = []
for spec in PLAN['meshes']:
    path = spec['asset']
    if only is not None and path.split('.')[0] not in only:
        continue
    assert path.startswith('/Game/Terrarium/HomesteadPilot/'), path
    mesh = unreal.load_asset(path)
    assert isinstance(mesh, unreal.StaticMesh), path
    nanite = sub.get_nanite_settings(mesh)
    nanite.set_editor_property('enabled', False)
    sub.set_nanite_settings(mesh, nanite, True)
    sizes = spec.get('screen_sizes', [1., .30, .10])
    assert len(sizes) == 3 and sizes[0] > sizes[1] > sizes[2] > 0
    custom = spec.get('lods', [])
    custom_levels = {int(lod['level']) for lod in custom if int(lod['level']) > 0}
    if custom_levels:
        assert custom_levels == {1, 2}, ('Custom chain must include LOD1 and LOD2', path, custom_levels)
        sub.remove_lods(mesh)
        for lod in sorted(custom, key=lambda x: x['level']):
            if lod['level'] == 0:
                continue
            source = Path(lod['fbx'])
            if not source.is_absolute():
                source = ROOT / source
            source = source.resolve()
            assert source.is_relative_to(ROOT / 'SourceAssets'), source
            assert source.is_file(), source
            assert sub.import_lod(mesh, lod['level'], str(source)) == lod['level']
        method = 'authored FBX LODs imported in Unreal'
    else:
        fractions = spec.get('retained_triangles', [1., .55, .25])
        options = unreal.StaticMeshReductionOptions()
        options.set_editor_property('auto_compute_lod_screen_size', False)
        options.set_editor_property('reduction_settings', [
            unreal.StaticMeshReductionSettings(percent_triangles=f, screen_size=s)
            for f, s in zip(fractions, sizes)])
        assert sub.set_lods(mesh, options) == 3, path
        method = 'Unreal static mesh reduction'
    assert sub.get_lod_count(mesh) == 3, path
    assert sub.set_lod_screen_sizes(mesh, sizes), path
    assert not mesh.is_lod_screen_size_auto_computed(), ('Explicit screen thresholds required', path)
    actual_sizes = list(sub.get_lod_screen_sizes(mesh))
    assert all(abs(a-b) < .0001 for a,b in zip(actual_sizes, sizes)), (path, actual_sizes)
    counts = [mesh.get_num_triangles(i) for i in range(3)]
    assert counts[0] > 0 and all(0 < n <= counts[0] for n in counts), (path, counts)
    assert counts[0] > counts[1] > counts[2], ('LODs must reduce actual runtime geometry', path, counts)
    collision = spec.get('collision', 'complex_as_simple')
    assert collision in ['complex_as_simple', 'none']
    sub.remove_collisions(mesh)
    body = mesh.get_editor_property('body_setup')
    assert body, path
    body.modify()
    if collision == 'complex_as_simple':
        body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        body.set_editor_property('double_sided_geometry', True)
        mesh.set_editor_property('lod_for_collision', 0)
    else:
        body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh), path
    rows.append({'asset': path, 'method': method, 'lod_count': sub.get_lod_count(mesh),
                 'triangles': counts, 'screen_sizes': actual_sizes,
                 'material_slots': [str(s.get_editor_property('material_slot_name')) for s in mesh.static_materials],
                 'materials': [s.get_editor_property('material_interface').get_path_name() if s.get_editor_property('material_interface') else None for s in mesh.static_materials],
                 'auto_screen_sizes': mesh.is_lod_screen_size_auto_computed(),
                 'nanite_enabled': sub.get_nanite_settings(mesh).get_editor_property('enabled'),
                 'collision': collision, 'collision_flag': str(body.get_editor_property('collision_trace_flag'))})

# Apply no-collision only on pilot mesh instances, never baseline shared assets.
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
collision_by_path = {x['asset'].split('.')[0]: x.get('collision', 'complex_as_simple') for x in PLAN['meshes']}
for actor in actors.get_all_level_actors():
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = comp.get_editor_property('static_mesh')
        if mesh and mesh.get_path_name().split('.')[0] in collision_by_path:
            policy = collision_by_path[mesh.get_path_name().split('.')[0]]
            comp.set_collision_profile_name('NoCollision' if policy == 'none' else 'BlockAll')
            comp.set_editor_property('generate_overlap_events', False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(OUT / ('mesh-runtime-partial-receipt.json' if only is not None else 'mesh-runtime-receipt.json')).write_text(json.dumps({'meshes': rows,
    'scope': 'Filtered rebuild only; run finalize_meshes.py for complete receipt' if only is not None else 'All planned meshes',
    'visual_transition_validation': 'Not provided by asset setup; inspect in motion and forced LOD views',
    'static_collision_policy': 'LOD0 per-triangle, no enclosing doorway box; pilot static meshes only',
}, indent=2), encoding='utf-8')
unreal.log('Homestead static mesh LOD/collision receipt saved.')
