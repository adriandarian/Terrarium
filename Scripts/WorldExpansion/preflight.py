import unreal, json, hashlib
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve()
assert R==Path('C:/Users/hello/Projects/Terrarium')
D=R/'Docs/WorldExpansion';D.mkdir(parents=True,exist_ok=True)
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w=E.get_editor_world();assert not E.get_game_world()
rows=[]
for a in A.get_all_level_actors():
 p=a.get_actor_location();o,e=a.get_actor_bounds(False)
 rows.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':[p.x,p.y,p.z],'center':[o.x,o.y,o.z],'extent':[e.x,e.y,e.z]})
data={'project':unreal.Paths.get_project_file_path(),'world':w.get_path_name(),'actors':rows,
 'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
 'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
 'protected_maps':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap',R/'Content/Terrarium/HomesteadPilot/Maps/StartingHome.umap']}}
(D/'preflight.json').write_text(json.dumps(data,indent=2))
unreal.log('World expansion preflight written')
