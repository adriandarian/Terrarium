"""Remove the review camera and return the saved scene to its original view."""
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='Detail_Review_Transient':actors.destroy_actor(a)
review=None;a=None;baseline=None;camera=None;world=None
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
assert levels.save_current_level()
unreal.log('DETAIL_REVIEW_FINISHED')
