"""Create native walking-character child Blueprints and pilot map override.

Run after assembly in StartingHome. Configure spawn using runtime-config.json.
Only six uniquely named axis mappings are added to existing project input.
"""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'
OUT.mkdir(parents=True, exist_ok=True)
LEVEL = '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
DEST = '/Game/Terrarium/HomesteadPilot/Runtime'
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] == LEVEL, world.get_path_name()
assert not editor.get_game_world(), 'Stop PIE before configuring the level'
config_path = OUT / 'runtime-config.json'
config = json.loads(config_path.read_text()) if config_path.exists() else {}
assert 'spawn_cm' in config, 'Root must set spawn_cm in runtime-config.json from assembled terrain'
spawn = config['spawn_cm']
parent = unreal.load_class(None, '/Script/ArchVisCharacter.ArchVisCharacter')
assert parent, 'ArchVisCharacter runtime plugin must already be loaded'

def blueprint(name, parent_class):
    bp = unreal.load_asset(DEST + '/' + name)
    if not bp:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property('parent_class', parent_class)
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, DEST, unreal.Blueprint, factory)
    assert bp
    assert unreal.BlueprintEditorLibrary.compile_blueprint(bp), name
    return bp, unreal.get_default_object(bp.generated_class())

bp, defaults = blueprint('BP_HomesteadExplorer', parent)
defaults.modify()
for key, value in {
    'move_forward_axis_name': 'HP_MoveForward', 'move_right_axis_name': 'HP_MoveRight',
    'turn_axis_name': 'HP_Turn', 'look_up_axis_name': 'HP_LookUp',
    'turn_at_rate_axis_name': 'HP_TurnRate', 'look_up_at_rate_axis_name': 'HP_LookUpRate',
    'base_eye_height': 75.0, 'mouse_sensitivity_scale_yaw': .018,
    'mouse_sensitivity_scale_pitch': .018,
}.items():
    defaults.set_editor_property(key, value)
capsule = defaults.get_editor_property('capsule_component')
capsule.modify()
capsule.set_capsule_size(34., 90., False)
movement = defaults.get_editor_property('character_movement')
movement.modify()
for key, value in {
    'walking_speed': 280., 'walking_acceleration': 1000., 'walking_friction': 6.,
    'max_step_height': float(config.get('max_step_height_cm', 35.)),
    'walkable_floor_angle': 46., 'can_walk_off_ledges': True,
    'use_flat_base_for_floor_checks': True,
}.items():
    movement.set_editor_property(key, value)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp)

game_bp, game_defaults = blueprint('BP_HomesteadGameMode', unreal.GameModeBase)
game_defaults.modify()
game_defaults.set_editor_property('default_pawn_class', bp.generated_class())
assert unreal.EditorAssetLibrary.save_loaded_asset(game_bp)
world.get_world_settings().set_editor_property('default_game_mode', game_bp.generated_class())

mapping_specs = [('HP_MoveForward', 'W', 1.), ('HP_MoveForward', 'S', -1.),
                 ('HP_MoveRight', 'D', 1.), ('HP_MoveRight', 'A', -1.),
                 ('HP_Turn', 'MouseX', 1.), ('HP_LookUp', 'MouseY', -1.)]
settings = unreal.InputSettings.get_input_settings()
added = []
for axis, key, scale in mapping_specs:
    existing = settings.get_axis_mapping_by_name(axis)
    exact = [m for m in existing if str(m.key.get_editor_property('key_name')) == key and abs(m.scale - scale) < .001]
    conflicts = [m for m in existing if str(m.key.get_editor_property('key_name')) == key and abs(m.scale - scale) >= .001]
    assert not conflicts, (axis, key, 'Existing conflicting pilot mapping requires review')
    if not exact:
        input_key = unreal.Key()
        input_key.set_editor_property('key_name', key)
        mapping = unreal.InputAxisKeyMapping()
        mapping.set_editor_property('axis_name', axis)
        mapping.set_editor_property('key', input_key)
        mapping.set_editor_property('scale', scale)
        settings.add_axis_mapping(mapping, False)
        added.append([axis, key, scale])
settings.save_key_mappings()
settings.force_rebuild_keymaps()

starts = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.PlayerStart)]
assert len(starts) <= 1, 'Review multiple player starts before choosing a spawn'
start = starts[0] if starts else actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(*spawn))
start.set_actor_label('HP_PlayerStart')
start.set_folder_path('HomesteadPilot/Runtime')
start.set_actor_location(unreal.Vector(*spawn), False, False)
start.set_actor_rotation(unreal.Rotator(pitch=0, yaw=float(config.get('spawn_yaw', 0)), roll=0), False)
assert levels.save_current_level()
(OUT / 'explorer-setup.json').write_text(json.dumps({
    'level': LEVEL, 'pawn': bp.get_path_name(), 'game_mode': game_bp.get_path_name(),
    'spawn_cm': spawn, 'capsule_radius_cm': capsule.get_unscaled_capsule_radius(),
    'capsule_half_height_cm': capsule.get_unscaled_capsule_half_height(), 'eye_height_cm': 165,
    'walking_speed_cm_s': movement.get_editor_property('walking_speed'),
    'max_step_height_cm': movement.get_editor_property('max_step_height'),
    'axis_mappings': mapping_specs, 'mappings_added_this_run': added,
    'project_default_map_or_game_mode_changed': False, 'play_validation': 'Not run by this setup script',
}, indent=2), encoding='utf-8')
unreal.log('Homestead explorer saved: WASD and mouse; launch Play to explore.')
