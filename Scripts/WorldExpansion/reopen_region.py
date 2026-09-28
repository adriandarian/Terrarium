import unreal,json,hashlib
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();D=R/'Docs/WorldExpansion'
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not E.get_game_world()
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
assert L.save_current_level()
assert L.load_level('/Game/Terrarium/HomesteadPilot/Maps/StartingHome')
assert L.load_level('/Game/Terrarium/WorldExpansion/Maps/ValleyRegion')
baseline=json.loads((D/'preflight.json').read_text())
for p,h in baseline['protected_maps'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
(D/'reopen.json').write_text(json.dumps({'map':'/Game/Terrarium/WorldExpansion/Maps/ValleyRegion','switched_to_StartingHome_and_back':True,'protected_maps_unchanged':True},indent=2))
