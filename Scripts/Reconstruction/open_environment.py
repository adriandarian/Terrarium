"""Open the saved environment and restore its portrait review camera."""
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.eject_pilot_level_actor()
if '/HomesteadReference.' not in str(levels.get_current_level()):
    assert levels.load_level('/Game/Terrarium/Maps/HomesteadReference')
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='Reference_TransientDetailCamera':actors.destroy_actor(a)
assert levels.save_current_level()
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([])
levels.editor_invalidate_viewports()
