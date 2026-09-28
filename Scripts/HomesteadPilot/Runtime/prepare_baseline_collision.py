"""Clone selected baseline meshes into the pilot before changing their collision.

Root sets baseline_collision_meshes (exact asset paths) in runtime-config.json.
All current-level instances of those assets switch to the pilot duplicate. Shared
source meshes remain untouched. Use this for retained ground/path/stair surfaces.
"""
import hashlib
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'
config = json.loads((OUT / 'runtime-config.json').read_text())
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
assert not editor.get_game_world()
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
replacements = {}
records = []
for source_path in config['baseline_collision_meshes']:
    source = unreal.load_asset(source_path)
    assert isinstance(source, unreal.StaticMesh), source_path
    source_path = source.get_path_name().split('.')[0]
    assert source_path.startswith('/Game/Terrarium/') and '/HomesteadPilot/' not in source_path
    name = source.get_name() + '_' + hashlib.sha256(source_path.encode()).hexdigest()[:8]
    destination = '/Game/Terrarium/HomesteadPilot/Runtime/Collision/' + name
    mesh = unreal.load_asset(destination)
    if not mesh:
        mesh = unreal.EditorAssetLibrary.duplicate_asset(source_path, destination)
    assert isinstance(mesh, unreal.StaticMesh), destination
    sub.remove_collisions(mesh)
    body = mesh.get_editor_property('body_setup')
    body.modify()
    body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    body.set_editor_property('double_sided_geometry', True)
    mesh.set_editor_property('lod_for_collision', 0)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    replacements[source_path] = mesh
    replacements[destination] = mesh
    records.append({'source': source_path, 'pilot_duplicate': destination,
                    'collision': str(body.get_editor_property('collision_trace_flag')), 'components': []})
by_dest = {r['pilot_duplicate']: r for r in records}
for actor in actors.get_all_level_actors():
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        old = comp.get_editor_property('static_mesh')
        key = old.get_path_name().split('.')[0] if old else ''
        if key in replacements:
            mesh = replacements[key]
            comp.set_static_mesh(mesh)
            comp.set_collision_profile_name('BlockAll')
            comp.set_editor_property('generate_overlap_events', False)
            by_dest[mesh.get_path_name().split('.')[0]]['components'].append(comp.get_path_name())
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(OUT / 'baseline-collision-receipt.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
