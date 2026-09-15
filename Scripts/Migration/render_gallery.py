"""Deterministic base-color gallery capture, independent of editor viewport state."""
import json
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root = Path(unreal.Paths.project_dir())
kind = (root / 'Saved/migration-gallery.txt').read_text().strip()
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.eject_pilot_level_actor()
assert levels.load_level('/Game/Terrarium/Migration/Maps/' + kind)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene = {a.get_actor_label():a for a in actors.get_all_level_actors()}
camera = scene['Baseline_Orthographic_Review']
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actor = actors.spawn_actor_from_class(unreal.SceneCapture2D, camera.get_actor_location(), camera.get_actor_rotation())
capture = actor.get_component_by_class(unreal.SceneCaptureComponent2D)
capture.set_editor_property('capture_every_frame', False)
capture.set_editor_property('capture_on_movement', False)
capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_BASE_COLOR)
capture.set_editor_property('projection_type', unreal.CameraProjectionMode.ORTHOGRAPHIC)
capture.set_editor_property('ortho_width',camera.camera_component.get_editor_property('ortho_width'))
target = unreal.RenderingLibrary.create_render_target2d(world, 1600, 1000, unreal.TextureRenderTargetFormat.RTF_RGBA8)
capture.set_editor_property('texture_target', target)
try:
    capture.capture_scene()
    unreal.RenderingLibrary.export_render_target(world,target,str((root/'Docs/AssetMigration').resolve()),kind.lower()+'-layout.png')
finally:
    actors.destroy_actor(actor)
unreal.log('MIGRATION_LAYOUT_CAPTURE '+kind)
