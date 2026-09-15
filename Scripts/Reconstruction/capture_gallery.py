"""Prepare/load and capture are separate editor calls so skylight IBL can settle."""
import json
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir());r=json.loads((root/'Saved/gallery-capture.json').read_text())
assert r['category'] in ['Architecture','Characters','Collectibles','Environment','Surfaces']
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
path='/Game/Terrarium/Reconstruction/Maps/'+r['category']
if r['mode']=='prepare':
    assert levels.save_current_level();assert levels.load_level(path)
else:
    assert path in str(levels.get_current_level())
    scene={a.get_actor_label():a for a in actors.get_all_level_actors()};camera=scene['GalleryOverviewCamera']
    assert 'GalleryAmbientSky' in scene
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    a=actors.spawn_actor_from_class(unreal.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation())
    c=a.get_component_by_class(unreal.SceneCaptureComponent2D)
    c.set_editor_property('capture_every_frame',False);c.set_editor_property('capture_on_movement',False)
    c.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR);c.set_editor_property('fov_angle',55.0)
    c.set_editor_property('post_process_settings',scene['GalleryFixedExposure'].get_editor_property('settings'));c.set_editor_property('post_process_blend_weight',1.0)
    target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    target.set_editor_property('target_gamma',2.2);c.set_editor_property('texture_target',target)
    try:
        c.capture_scene();unreal.RenderingLibrary.export_render_target(world,target,str((root/'Docs/Reconstruction/Galleries').resolve()),r['category']+'.png')
    finally:actors.destroy_actor(a)
    assert levels.save_current_level()
    if r.get('restore'):assert levels.load_level('/Game/Terrarium/Reconstruction/Maps/ReviewStage')
