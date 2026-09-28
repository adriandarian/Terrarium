"""Read-only reopened-level check of pawn/game mode, saved LODs and collision."""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world(), 'End PIE and reopen saved StartingHome first'
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'Save/reopen map before final verification'
game_mode = world.get_world_settings().get_editor_property('default_game_mode')
assert game_mode and 'BP_HomesteadGameMode' in game_mode.get_path_name()
pawn_class = unreal.get_default_object(game_mode).get_editor_property('default_pawn_class')
assert pawn_class and 'BP_HomesteadExplorer' in pawn_class.get_path_name()
config = json.loads((OUT / 'runtime-config.json').read_text())
starts = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.PlayerStart)
assert len(starts) == 1, 'Pilot must have one deliberate default PlayerStart'
start = starts[0]
start_position = start.get_actor_location()
assert all(abs(a-b)<.01 for a,b in zip([start_position.x,start_position.y,start_position.z],config['spawn_cm']))
assert not start.get_editor_property('is_editor_only_actor')
for camera in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.CameraActor):
    assert camera.get_auto_activate_player_index() == -1, ('Review camera must not override the player', camera.get_path_name())
pawn = unreal.get_default_object(pawn_class)
assert abs(pawn.capsule_component.get_unscaled_capsule_radius()-34) < .01
assert abs(pawn.capsule_component.get_unscaled_capsule_half_height()-90) < .01
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
plan = json.loads((OUT / 'mesh-plan.json').read_text())
meshes = []
for spec in plan['meshes']:
    mesh = unreal.load_asset(spec['asset'])
    assert mesh and sub.get_lod_count(mesh) == 3, spec['asset']
    counts = [mesh.get_num_triangles(i) for i in range(3)]
    assert counts[0] > counts[1] > counts[2] > 0, (spec['asset'], counts)
    sizes = list(sub.get_lod_screen_sizes(mesh))
    expected = spec.get('screen_sizes', [1., .30, .10])
    assert all(abs(a-b)<.0001 for a,b in zip(sizes,expected)), (spec['asset'],sizes)
    assert not sub.get_nanite_settings(mesh).get_editor_property('enabled')
    flag = mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')
    if spec.get('collision', 'complex_as_simple') == 'complex_as_simple':
        assert flag == unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
    assert all(s.get_editor_property('material_interface') for s in mesh.static_materials)
    package_file = ROOT / 'Content' / (spec['asset'].split('.')[0].removeprefix('/Game/') + '.uasset')
    meshes.append({'mesh': mesh.get_path_name(), 'triangles': counts, 'screen_sizes': sizes,
                   'collision': str(flag), 'uasset_disk_bytes': package_file.stat().st_size})
instances = []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = comp.get_editor_property('static_mesh')
        if mesh and mesh.get_path_name().startswith('/Game/Terrarium/HomesteadPilot/'):
            assert comp.get_editor_property('forced_lod_model') == 0, comp.get_path_name()
            instances.append({'actor': actor.get_actor_label(), 'mesh': mesh.get_path_name(),
                              'automatic_lod': True, 'collision_enabled': str(comp.get_collision_enabled())})
settings = unreal.InputSettings.get_input_settings()
mapping_counts = {name: len(settings.get_axis_mapping_by_name(name)) for name in ['HP_MoveForward','HP_MoveRight','HP_Turn','HP_LookUp']}
assert mapping_counts == {'HP_MoveForward':2, 'HP_MoveRight':2, 'HP_Turn':1, 'HP_LookUp':1}, mapping_counts
input_text = (ROOT / 'Config/DefaultInput.ini').read_text(encoding='utf-8-sig')
assert sum(line.startswith('+AxisMappings=(AxisName="HP_') for line in input_text.splitlines()) == 6, 'Persist six axis mappings to DefaultInput.ini'
(OUT / 'saved-runtime-verification.json').write_text(json.dumps({'world': world.get_path_name(),
    'game_mode': game_mode.get_path_name(), 'pawn_class': pawn_class.get_path_name(),
    'player_start_cm': [start_position.x,start_position.y,start_position.z],
    'capsule_cm': {'radius':34,'height':180}, 'input_mapping_counts': mapping_counts,
    'meshes': meshes, 'pilot_components': instances,
    'limits': 'Readback is technical persistence evidence; visual LOD motion and PIE control require separate receipts'}, indent=2), encoding='utf-8')
