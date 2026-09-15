import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
path='/Game/Terrarium/Maps/HomesteadBeforePass7'
if not unreal.EditorAssetLibrary.does_asset_exist(path):
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,path)
    world=None
    assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
unreal.log('PASS7_BACKUP_SAVED')
