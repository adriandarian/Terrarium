import unreal,json,sys,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
mesh=unreal.load_asset('/Game/Terrarium/Blender/TrailPatch/SM_Blender_TrailPatch');start=unreal.Vector(*ref.world(60,-30,560));hall=scene['Blender_CivicHall_NorthPath'];delta=hall.get_actor_location()-start;delta.z=0;length=delta.length();direction=delta/length;end=start+direction*(length-285)
rows=[]
for i in range(4):
 p=start+(end-start)*(i/3);p.z=560.25;label='SceneAssembly_NorthApproach_'+str(i);a=scene.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,p);a.set_actor_label(label);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(unreal.Vector(.48,.60,.65));a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=math.degrees(math.atan2(delta.y,delta.x)),roll=0),False);a.set_folder_path('SceneAssembly/Approaches');rows.append(label)
(root/'Docs/SceneAssembly/north-approach.json').write_text(json.dumps({'actors':rows,'purpose':'Connect relocated civic hall entrance to existing northern path'},indent=2))
label='SceneAssembly_Courtyard_Review';cam=scene.get(label) or actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(1200,900,1350));cam.set_actor_label(label);cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),unreal.Vector(210,-35,645)),False);c=cam.camera_component;c.set_projection_mode(unreal.CameraProjectionMode.PERSPECTIVE);c.set_editor_property('field_of_view',48.);c.set_editor_property('aspect_ratio',1.6);c.set_editor_property('constrain_aspect_ratio',True);c.set_editor_property('post_process_blend_weight',0.);cam.set_folder_path('SceneAssembly/ReviewCameras')
levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([]);assert levels.save_current_level()
p=cam.get_actor_location();r=cam.get_actor_rotation();args=json.loads((root/'Saved/scene-assembly-capture.json').read_text());args['captureTransform']['location']={'x':p.x,'y':p.y,'z':p.z};args['captureTransform']['rotation']={'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll};(root/'Saved/scene-assembly-close.json').write_text(json.dumps(args))
