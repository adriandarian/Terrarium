import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
D=R/'Docs/WorldExpansion';A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
name=json.loads((D/'view-request.json').read_text())['name'];v=next(v for v in json.loads((D/'views.json').read_text()) if v['name']==name)
L.eject_pilot_level_actor();a=next(a for a in A.get_all_level_actors() if a.get_actor_label()==v['actor'])
p=unreal.Vector(*[q*100 for q in v['position_m']]);t=unreal.Vector(*[q*100 for q in v['target_m']]);rot=unreal.MathLibrary.find_look_at_rotation(p,t)
a.set_actor_location(p,False,False);a.set_actor_rotation(rot,False);a.camera_component.set_field_of_view(v['fov']);a.set_editor_property('auto_activate_for_player',unreal.AutoReceiveInput.DISABLED)
L.pilot_level_actor(a);L.set_exact_camera_view(True);L.editor_set_game_view(True);A.set_selected_level_actors([])
(D/'capture-request.json').write_text(json.dumps({'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':rot.pitch,'yaw':rot.yaw,'roll':rot.roll},'scale':{'x':1,'y':1,'z':1}},'bShowUI':False}))
