"""Preserve the open map's unsaved state before switching to asset review levels."""
import json
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
original = world.get_path_name()
backup = '/Game/Terrarium/Maps/BeforeAssetMigration'
assert not unreal.EditorAssetLibrary.does_asset_exist(backup), 'Backup already exists; inspect before rerunning'
assert unreal.EditorLoadingAndSavingUtils.save_map(world, backup)
Path(unreal.Paths.project_dir(), 'Docs/AssetMigration/editor-backup.json').write_text(json.dumps({'original_world': original, 'preserved_snapshot': backup, 'project': unreal.Paths.get_project_file_path()}, indent=2))
