import unreal,json,hashlib
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
l=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
l.eject_pilot_level_actor();assert l.load_level('/Game/Terrarium/Blender/Maps/HomesteadBlender')
def vec(v):return [v.x,v.y,v.z]
rows=[]
for actor in a.get_all_level_actors():
 cs=actor.get_components_by_class(unreal.StaticMeshComponent)
 p=actor.get_actor_location();b,e=actor.get_actor_bounds(False);rot=actor.get_actor_rotation()
 rows.append({'label':actor.get_actor_label(),'class':actor.get_class().get_name(),'location':vec(p),'rotation':[rot.pitch,rot.yaw,rot.roll],'scale':vec(actor.get_actor_scale3d()),'bounds':{'center':vec(b),'extent':vec(e)},'meshes':[{'path':c.static_mesh.get_path_name() if c.static_mesh else None,'instances':c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else None} for c in cs]})
cam=next(x for x in a.get_all_level_actors() if x.get_actor_label()=='Baseline_Orthographic_Review')
l.pilot_level_actor(cam);l.set_exact_camera_view(True);l.editor_set_game_view(True);a.set_selected_level_actors([])
p=cam.get_actor_location();r=cam.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(R/'Docs/HomesteadPilot/baseline-capture.json').write_text(json.dumps(args))
(R/'Docs/HomesteadPilot/baseline-audit.json').write_text(json.dumps({'actors':rows,'baseline_hash':hashlib.sha256((R/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap').read_bytes()).hexdigest(),'save_map_doc':unreal.EditorLoadingAndSavingUtils.save_map.__doc__},indent=2))
