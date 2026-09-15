"""Native, lit, camera-independent source comparison render of one saved mesh."""
import json,math
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());r=json.loads((root/'Saved/reconstruction-capture.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Reconstruction/Maps/ReviewStage' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
a=scene['ReviewModel'];a.static_mesh_component.set_static_mesh(unreal.load_asset(r['asset']));a.set_actor_scale3d(unreal.Vector(1,1,1));a.set_actor_location(unreal.Vector(),False,False)
origin,extent=a.get_actor_bounds(False);scene['StudioFloor'].set_actor_location(unreal.Vector(0,0,origin.z-extent.z-10.1),False,False)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ca=actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector());ca.set_actor_label('ReconstructionTransientCapture')
c=ca.get_component_by_class(unreal.SceneCaptureComponent2D)
c.set_editor_property('capture_every_frame',False);c.set_editor_property('capture_on_movement',False)
c.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
c.set_editor_property('projection_type',unreal.CameraProjectionMode.PERSPECTIVE)
c.set_editor_property('fov_angle',20.0)
if r.get('projection')=='orthographic':
    c.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
    c.set_editor_property('ortho_width',r['ortho_width'])
c.set_editor_property('post_process_settings',scene['StudioExposure'].get_editor_property('settings'))
c.set_editor_property('post_process_blend_weight',1.0)
pitch,yaw=r.get('pitch',-18),r.get('yaw',65)
direction=unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)),math.cos(math.radians(pitch))*math.sin(math.radians(yaw)),math.sin(math.radians(pitch)))
distance=r.get('distance',max(extent.x,extent.y,extent.z)*7.8)
if 'focus' in r:origin=unreal.Vector(*r['focus'])
ca.set_actor_location(origin-direction*distance,False,False);ca.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False)
resolution=r.get('resolution',960)
target=unreal.RenderingLibrary.create_render_target2d(world,r.get('width',resolution),r.get('height',resolution),unreal.TextureRenderTargetFormat.RTF_RGBA8)
target.set_editor_property('target_gamma',2.2);c.set_editor_property('texture_target',target)
dest=root/'Docs/Reconstruction/Renders';dest.mkdir(parents=True,exist_ok=True)
try:
    c.capture_scene()
    unreal.RenderingLibrary.export_render_target(world,target,str(dest.resolve()),r['name']+'.png')
finally:actors.destroy_actor(ca)
unreal.log('RECON_RENDER '+r['name'])
