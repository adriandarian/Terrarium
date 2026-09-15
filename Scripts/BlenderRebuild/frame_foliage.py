"""Frame an actual migrated tree using its rotation and native Unreal camera."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
key=(root/'Saved/blender-import-asset.txt').read_text().strip();assert key=='HomesteadTree'
record=json.loads((root/'Docs/BlenderRebuild'/key/'instance-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert record['world']+'.' in str(levels.get_current_level())
row=min(record['instances'],key=lambda r:(r['after']['translation'][0]+959)**2+(r['after']['translation'][1]+685)**2)['after']
mesh=unreal.load_asset(record['mesh']);bounds=mesh.get_bounding_box()
pos=row['translation'];focus=unreal.Vector(pos[0],pos[1],pos[2]+(bounds.min.z+bounds.max.z)*.5*row['scale'][2])
q=row['rotation_xyzw'];yaw=2*math.atan2(q[2],q[3]);co=math.cos(yaw);si=math.sin(yaw)
offset=unreal.Vector(650,-650,450)
label='Blender_HomesteadTree_Review';scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
cam=scene.get(label) or actors.spawn_actor_from_class(unreal.CameraActor,focus+offset)
cam.set_actor_label(label);cam.set_actor_location(focus+offset,False,False);cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),focus),False)
c=cam.get_component_by_class(unreal.CameraComponent);c.set_editor_property('projection_mode',unreal.CameraProjectionMode.PERSPECTIVE);c.set_editor_property('field_of_view',32)
actors.set_selected_level_actors([]);levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);assert levels.save_current_level()
p=cam.get_actor_location();r=cam.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/blender-foliage-capture.json').write_text(json.dumps(args))
