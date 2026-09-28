"""Stage a named pilot comparison view and record native-capture parameters."""
import unreal, json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve()
assert R==Path('C:/Users/hello/Projects/Terrarium')
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadPilot/Maps/StartingHome.' in str(L.get_current_level())
request=json.loads((R/'Docs/HomesteadPilot/view-request.json').read_text())
scene={a.get_actor_label():a for a in A.get_all_level_actors()}
label=request['label']
cam=scene.get(label)
if not cam:
    cam=A.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
    cam.set_actor_label(label)
    cam.set_folder_path('HomesteadPilot/ReviewCameras')
if 'position' in request:
    p=unreal.Vector(*request['position'])
    cam.set_actor_location(p,False,False)
    cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(p,unreal.Vector(*request['target'])),False)
c=cam.camera_component
if request.get('perspective'):
    c.set_projection_mode(unreal.CameraProjectionMode.PERSPECTIVE)
    c.set_field_of_view(request.get('fov',55.))
if 'ortho_width' in request:
    c.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC)
    c.set_ortho_width(request['ortho_width'])
if 'aspect' in request:
    c.set_editor_property('aspect_ratio',request['aspect'])
    c.set_editor_property('constrain_aspect_ratio',True)
c.set_editor_property('post_process_blend_weight',0.)
L.pilot_level_actor(cam);L.set_exact_camera_view(True);L.editor_set_game_view(True)
A.set_selected_level_actors([])
assert L.save_current_level()
p=cam.get_actor_location();r=cam.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(R/'Docs/HomesteadPilot/current-capture.json').write_text(json.dumps(args))
