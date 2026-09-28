import unreal, json, hashlib
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
D=R/'Docs/WorldExpansion'
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not E.get_game_world()
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
dest='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
before=json.loads((D/'preflight.json').read_text())
L.eject_pilot_level_actor()
assert unreal.EditorLoadingAndSavingUtils.save_map(E.get_editor_world(),dest)
assert L.load_level(dest)
for p,h in before['protected_maps'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
(D/'map-created.json').write_text(json.dumps({'map':dest,'protected_maps_unchanged':True},indent=2))
