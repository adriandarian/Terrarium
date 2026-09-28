"""Disable inherited review-camera player activation on the pilot map only."""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
assert not editor.get_game_world(), 'Stop PIE before saving the map camera fix'
changes = []
for camera in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.CameraActor):
    index = camera.get_auto_activate_player_index()
    if index >= 0:
        changes.append({'actor':camera.get_path_name(),'label':camera.get_actor_label(),
                        'before':str(camera.get_editor_property('auto_activate_for_player')),'after':'DISABLED'})
        camera.set_editor_property('auto_activate_for_player',unreal.AutoReceiveInput.DISABLED)
    assert camera.get_auto_activate_player_index() == -1
levels.eject_pilot_level_actor()
assert levels.save_current_level()
(ROOT/'Docs/HomesteadPilot/Runtime/play-view-fix.json').write_text(json.dumps({
    'level':world.get_path_name(),'changes':changes,
    'reason':'Inherited baseline review camera auto-activated for Player0 and overrode the possessed explorer view',
    'PIE_view_target_validation':'Start a new PIE session and run inspect_play_view.py'},indent=2),encoding='utf-8')
