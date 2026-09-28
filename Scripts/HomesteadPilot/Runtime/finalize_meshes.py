"""Read back existing pilot LODs and finalize component collision, without rebuilding.

Use after configure_meshes created/saved the meshes but a later component step
failed. Reimported LOD0 assets still require configure_meshes before this verifier.
"""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'
PLAN = json.loads((OUT / 'mesh-plan.json').read_text())
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
rows = []
policies = {}
for spec in PLAN['meshes']:
    path = spec['asset']
    assert path.startswith('/Game/Terrarium/HomesteadPilot/')
    mesh = unreal.load_asset(path)
    assert isinstance(mesh, unreal.StaticMesh)
    assert sub.get_lod_count(mesh) == 3, path
    counts = [mesh.get_num_triangles(i) for i in range(3)]
    assert counts[0] > counts[1] > counts[2] > 0, (path, counts)
    sizes = list(sub.get_lod_screen_sizes(mesh))
    assert all(abs(a-b)<.0001 for a,b in zip(sizes,spec.get('screen_sizes',[1.,.30,.10]))), (path,sizes)
    assert not mesh.is_lod_screen_size_auto_computed()
    assert not sub.get_nanite_settings(mesh).get_editor_property('enabled')
    collision = spec.get('collision','complex_as_simple')
    body = mesh.get_editor_property('body_setup')
    flag = body.get_editor_property('collision_trace_flag')
    if collision == 'complex_as_simple':
        assert flag == unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE, (path,flag)
    materials = [s.get_editor_property('material_interface') for s in mesh.static_materials]
    assert all(materials), path
    custom = any(int(lod['level'])>0 for lod in spec.get('lods',[]))
    rows.append({'asset':path,'method':'authored FBX LODs imported in Unreal' if custom else 'Unreal static mesh reduction',
        'lod_count':3,'triangles':counts,'screen_sizes':sizes,'auto_screen_sizes':False,'nanite_enabled':False,
        'material_slots':[str(s.get_editor_property('material_slot_name')) for s in mesh.static_materials],
        'materials':[m.get_path_name() for m in materials],'collision':collision,'collision_flag':str(flag)})
    policies[mesh.get_path_name().split('.')[0]] = collision
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = comp.get_editor_property('static_mesh')
        path = mesh.get_path_name().split('.')[0] if mesh else ''
        if path in policies:
            comp.set_collision_profile_name('NoCollision' if policies[path]=='none' else 'BlockAll')
            comp.set_editor_property('generate_overlap_events',False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(OUT/'mesh-runtime-receipt.json').write_text(json.dumps({'meshes':rows,
    'visual_transition_validation':'Not provided by asset readback; inspect forced LODs and approach/retreat',
    'static_collision_policy':'LOD0 per-triangle, no enclosing doorway box; pilot static meshes only'},indent=2),encoding='utf-8')
unreal.log('Homestead existing mesh LOD/collision receipt saved without rebuilding.')
