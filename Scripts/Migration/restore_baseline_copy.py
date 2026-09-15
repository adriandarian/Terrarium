"""Restore our unintended baseline edit from its untouched gallery bootstrap copy."""
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Terrarium/Migration/Maps/Characters')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
labels = {a.get_actor_label() for a in actors}
assert {'Baseline_StoneCube', 'Baseline_ClaySphere', 'Baseline_Ground'}.issubset(labels)
assert not any(name.startswith('SM_') for name in labels)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/Terrarium/Maps/RenderBaseline')
unreal.log('MIGRATION_BASELINE_RESTORED_FROM_BOOTSTRAP')
