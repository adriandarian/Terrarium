import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();D=R/'Docs/WorldExpansion'
req=json.loads((D/'view-request.json').read_text())
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not E.get_game_world()
a=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='WX_Review_'+req['name'])
L.pilot_level_actor(a);L.set_exact_camera_view(True);L.editor_set_game_view(True)
A.set_selected_level_actors([])
p=a.get_actor_location();r=a.get_actor_rotation()
(D/'capture-request.json').write_text(json.dumps({'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'bShowUI':False}))
