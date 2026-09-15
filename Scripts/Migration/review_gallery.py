"""Tune only the migration review level and frame a whole gallery or a named mesh."""
import json
import math
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root = Path(unreal.Paths.project_dir())
request = json.loads((root / 'Saved/migration-review.json').read_text())
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.eject_pilot_level_actor()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
path = '/Game/Terrarium/Migration/Maps/' + request['kind']
if str(levels.get_current_level()).split('.')[0] != path:
    assert levels.load_level(path)
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
for a in scene.values():
    if a.get_actor_label().startswith('Label_'):
        a.set_actor_rotation(unreal.Rotator(pitch=-90, yaw=-90, roll=0), False)
        a.text_render.set_world_size({'Architecture':55, 'Characters':22, 'Environment':35, 'References':20, 'Surfaces':20}[request['kind']])
matpath = '/Game/Terrarium/Migration/Materials/M_GalleryFloor'
mat = unreal.load_asset(matpath) if unreal.EditorAssetLibrary.does_asset_exist(matpath) else None
if not mat:
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_GalleryFloor', '/Game/Terrarium/Migration/Materials', unreal.Material, unreal.MaterialFactoryNew())
    lib = unreal.MaterialEditingLibrary
    node = lib.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
    node.set_editor_property('constant', unreal.LinearColor(.045, .054, .050, 1))
    lib.connect_material_property(node, '', unreal.MaterialProperty.MP_BASE_COLOR)
    value = lib.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 180)
    value.set_editor_property('r', .95)
    lib.connect_material_property(value, '', unreal.MaterialProperty.MP_ROUGHNESS)
    lib.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
scene['Baseline_Ground'].static_mesh_component.set_material(0, mat)
camera = scene['Baseline_Orthographic_Review']
if request.get('asset'):
    origin, extent = scene[request['asset']].get_actor_bounds(False)
    pitch, yaw = -24, request.get('yaw', 55)
    width = max(extent.x*2, extent.y*2, extent.z*3.4)*1.45
    direction = unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)), math.cos(math.radians(pitch))*math.sin(math.radians(yaw)), math.sin(math.radians(pitch)))
    camera.set_actor_location(origin-direction*width*2, False, False)
    camera.set_actor_rotation(unreal.Rotator(pitch=pitch, yaw=yaw, roll=0), False)
    camera.camera_component.set_ortho_width(width)
else:
    count = json.loads((root / 'Docs/AssetMigration' / (request['kind'].lower() + '-gallery.json')).read_text())['count']
    cols, sx, sy = {'Characters': (4,410,570), 'Architecture': (3,1550,1700), 'Environment': (4,1100,1250), 'References': (7,480,530), 'Surfaces': (7,480,530)}[request['kind']]
    rows = math.ceil(count/cols)
    center = unreal.Vector((min(cols,count)-1)*sx/2, (rows-1)*sy/2, 100)
    width, depth = cols*sx+350, rows*sy+350
    pitch, yaw = (-88,90) if request['kind'] in ['References','Surfaces'] else (-42,90)
    direction = unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)), math.cos(math.radians(pitch))*math.sin(math.radians(yaw)), math.sin(math.radians(pitch)))
    camera.set_actor_location(center-direction*max(width,depth)*1.6, False, False)
    camera.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False)
    camera.camera_component.set_ortho_width(max(width,depth*1.6*.9))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(), camera.get_actor_rotation())
levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
levels.editor_invalidate_viewports()
(root / 'Saved/migration-camera.json').write_text(json.dumps({'location': {'x': camera.get_actor_location().x, 'y': camera.get_actor_location().y, 'z': camera.get_actor_location().z}, 'rotation': {'pitch': camera.get_actor_rotation().pitch, 'yaw': camera.get_actor_rotation().yaw, 'roll': camera.get_actor_rotation().roll}, 'scale': {'x': 1, 'y': 1, 'z': 1}}))
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'viewmode unlit' if request['kind'] == 'References' else 'viewmode lit')
if not request.get('asset'):
    assert levels.save_current_level()
