import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Terrarium/Maps/ModularGallery')
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_actor_label().startswith('Study_'):
        a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
