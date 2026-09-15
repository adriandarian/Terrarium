"""Allow native capture while Codex is focused; session-only, no config write."""
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
settings=unreal.load_object(None,'/Script/UnrealEd.Default__EditorPerformanceSettings')
assert settings
settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.SystemLibrary.execute_console_command(None,'Slate.bAllowThrottling 0')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_invalidate_viewports()
unreal.log('PASS7_BACKGROUND_RENDERING_ENABLED')
