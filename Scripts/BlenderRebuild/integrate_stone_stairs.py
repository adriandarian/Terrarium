"""Replace the existing terrace stair actor with the separately authored Blender variant."""
import unreal, json
from pathlib import Path
root = Path(unreal.Paths.project_dir()).resolve()
assert root == Path('C:/Users/hello/Projects/Terrarium')
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world_path = '/Game/Terrarium/Blender/Maps/HomesteadBlender'
assert world_path + '.' in str(levels.get_current_level())
folder = root / 'Docs/BlenderRebuild/StoneStairs'
before = json.loads((root / 'Saved/blender-crossing-before.json').read_text())['stairs'][0]
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
ob = scene[before['actor']]
mesh = unreal.load_asset('/Game/Terrarium/Blender/StoneStairs/SM_Blender_StoneStairs')
assert mesh and ob.static_mesh_component.static_mesh.get_path_name() in [before['mesh'], mesh.get_path_name()]
if not (folder / 'before-placement.json').exists():
    (folder / 'before-placement.json').write_text(json.dumps(before, indent=2))
pos = before['transform']['translation']
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
ob.static_mesh_component.set_static_mesh(mesh)
ob.static_mesh_component.set_editor_property('override_materials', [])
ob.set_actor_location(unreal.Vector(*pos), False, False)
ob.set_actor_scale3d(unreal.Vector(1, 1, 1))
# Blender's +Y ascending direction becomes -Y on FBX import.
ob.set_actor_rotation(unreal.Rotator(pitch=0, yaw=182, roll=0), False)
camlabel = 'Blender_StoneStairs_Review'
cam = scene.get(camlabel) or actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector())
focus = unreal.Vector(pos[0], pos[1], 425)
cam.set_actor_label(camlabel)
cam.set_actor_location(focus + unreal.Vector(650, -900, 780), False, False)
cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(), focus), False)
cam.get_component_by_class(unreal.CameraComponent).set_editor_property('field_of_view', 36)
actors.set_selected_level_actors([])
levels.pilot_level_actor(cam)
levels.set_exact_camera_view(True)
levels.editor_set_game_view(True)
assert levels.save_current_level()
record = {'asset': 'StoneStairs', 'variant_of': 'RiverCrossing', 'actor': ob.get_actor_label(), 'mesh': mesh.get_path_name(), 'world': world_path, 'location_cm': pos, 'scale': 1, 'yaw': 182, 'camera': camlabel, 'treads': 8, 'rise_cm': 35, 'run_cm': 31.5, 'bottom_cm': 280, 'top_cm': 560, 'status': 'placed_pending_collision_and_visual_check'}
(folder / 'world-placement.json').write_text(json.dumps(record, indent=2))
p = cam.get_actor_location()
r = cam.get_actor_rotation()
args = {'captureTransform': {'location': {'x': p.x, 'y': p.y, 'z': p.z}, 'rotation': {'pitch': r.pitch, 'yaw': r.yaw, 'roll': r.roll}, 'scale': {'x': 1, 'y': 1, 'z': 1}}, 'annotations': {'gridSpacing': 0, 'gridExtent': 0, 'gridHeight': 0, 'maxLabelDistance': 0, 'classFilter': {'refPath': '/Script/Engine.Actor'}, 'maxLabels': 0}, 'bShowUI': False}
(root / 'Saved/blender-stone-stairs-capture.json').write_text(json.dumps(args))
unreal.log('BLENDER_STONE_STAIRS_PLACED')
