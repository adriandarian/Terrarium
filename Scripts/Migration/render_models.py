"""Render isolated front views through Unreal SceneCapture2D to real PNGs."""
import json
import math
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root = Path(unreal.Paths.project_dir())
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
group = (root / 'Saved/migration-models.txt').read_text().strip()
kind = 'Architecture' if group == 'structures' else 'Characters'
levels.eject_pilot_level_actor()
assert levels.load_level('/Game/Terrarium/Migration/Maps/' + kind)
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
capture_actor = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector())
capture_actor.set_actor_label('Migration_TransientCapture')
capture = capture_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
capture.set_editor_property('capture_every_frame', False)
capture.set_editor_property('capture_on_movement', False)
capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_BASE_COLOR)
capture.set_editor_property('projection_type', unreal.CameraProjectionMode.ORTHOGRAPHIC)
capture.set_editor_property('primitive_render_mode', unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
capture.set_editor_property('post_process_settings', scene['Baseline_FixedExposure_EV12'].get_editor_property('settings'))
target = unreal.RenderingLibrary.create_render_target2d(world, 768, 768, unreal.TextureRenderTargetFormat.RTF_RGBA8)
capture.set_editor_property('texture_target', target)
folder = root / 'Docs/AssetMigration/Models'
try:
    for record in json.loads((root / 'Docs/AssetMigration' / (group+'-built.json')).read_text()):
        actor = scene[record['name']]
        origin, extent = actor.get_actor_bounds(False)
        width = max(extent.x, extent.y, extent.z)*3.5
        pitch, yaw = -25, 65
        direction = unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)), math.cos(math.radians(pitch))*math.sin(math.radians(yaw)), math.sin(math.radians(pitch)))
        capture_actor.set_actor_location(origin-direction*width*2, False, False)
        capture_actor.set_actor_rotation(unreal.Rotator(pitch=pitch, yaw=yaw, roll=0), False)
        capture.set_editor_property('ortho_width', width)
        capture.clear_show_only_components()
        capture.show_only_actor_components(actor)
        capture.show_only_actor_components(scene['Baseline_Ground'])
        capture.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, target, str(folder.resolve()), record['name']+'-front.png')
finally:
    actors.destroy_actor(capture_actor)
unreal.log('MIGRATION_FRONT_RENDERS ' + group)
