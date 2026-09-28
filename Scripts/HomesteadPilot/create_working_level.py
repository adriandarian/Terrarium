import unreal,json,hashlib
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
L='/Game/Terrarium/HomesteadPilot/Maps/StartingHome';l=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not unreal.EditorAssetLibrary.does_asset_exist(L)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert '/Blender/Maps/HomesteadBlender.' in str(l.get_current_level())
f=R/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap';before=hashlib.sha256(f.read_bytes()).hexdigest()
l.eject_pilot_level_actor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(w,L)
del w
assert l.load_level(L)
assert before==hashlib.sha256(f.read_bytes()).hexdigest()
(R/'Docs/HomesteadPilot/working-level.json').write_text(json.dumps({'level':L,'saved_reopened':True,'baseline_unchanged':True,'baseline_sha256':before},indent=2))
