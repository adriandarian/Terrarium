import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Blender_Cottage_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
capture=actors.spawn_actor_from_class(unreal.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation())
c=capture.get_component_by_class(unreal.SceneCaptureComponent2D)
c.set_editor_property('capture_every_frame',False);c.set_editor_property('capture_on_movement',False)
c.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
c.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC);c.set_editor_property('ortho_width',850)
pp=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_FixedExposure_EV12')
s=pp.get_editor_property('settings')
# SceneCapture has no physical camera exposure; use an explicit equivalent EV.
for k,v in [('auto_exposure_apply_physical_camera_exposure',False),('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL),('auto_exposure_bias',-12.0)]:
    s.set_editor_property('override_'+k,True);s.set_editor_property(k,v)
c.set_editor_property('post_process_settings',s);c.set_editor_property('post_process_blend_weight',1.0)
rt=unreal.RenderingLibrary.create_render_target2d(world,1200,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',2.2)
c.set_editor_property('texture_target',rt)
try:
    c.capture_scene();unreal.RenderingLibrary.export_render_target(world,rt,str(root/'Docs/BlenderRebuild/Cottage'),'unreal-world.png')
finally:actors.destroy_actor(capture)
