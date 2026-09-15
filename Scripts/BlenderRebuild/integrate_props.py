"""Use Blender props in the working homestead; preserve old map and source assets."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};reports=[]
for key,label,pos,scale,yaw in [('Lantern','Reference_Lantern',(122,-350,560),.64,0),('Sign','Blender_Sign_Courtyard',(257,-490,560),.62,-90)]:
    mesh=unreal.load_asset('/Game/Terrarium/Blender/'+key+'/SM_Blender_'+key);assert mesh
    ob=scene.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));ob.set_actor_label(label)
    ob.static_mesh_component.set_static_mesh(mesh);ob.static_mesh_component.set_editor_property('override_materials',[])
    ob.set_actor_scale3d(unreal.Vector(scale,scale,scale));ob.set_actor_location(unreal.Vector(*pos),False,False);ob.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    ob.tags=[unreal.Name(x) for x in sorted(set(map(str,ob.tags))|{'BlenderRebuild','FidelityReviewPending'})]
    center,extent=ob.get_actor_bounds(False)
    record={'asset':key,'actor':label,'mesh':mesh.get_path_name(),'location_cm':list(pos),'scale':scale,'yaw':yaw,'bounds_center':[center.x,center.y,center.z],'bounds_extent':[extent.x,extent.y,extent.z],'world':'/Game/Terrarium/Blender/Maps/HomesteadBlender','status':'placed_pending_visual_check'}
    (root/'Docs/BlenderRebuild'/key/'world-placement.json').write_text(json.dumps(record,indent=2));reports.append(record)
camera=scene.get('Blender_Props_Review') or actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
camera.set_actor_label('Blender_Props_Review');focus=unreal.Vector(130,-380,670)
camera.set_actor_location(focus+unreal.Vector(780,800,500),False,False);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),focus),False)
c=camera.get_component_by_class(unreal.CameraComponent);c.set_editor_property('projection_mode',unreal.CameraProjectionMode.PERSPECTIVE);c.set_editor_property('field_of_view',32)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);assert levels.save_current_level()
# Supply every native MCP argument explicitly; optional defaults are not reliable.
p=camera.get_actor_location();r=camera.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/blender-props-capture.json').write_text(json.dumps(args))
