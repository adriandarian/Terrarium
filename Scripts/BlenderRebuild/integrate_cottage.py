"""Place the imported cottage into a preserved copy of the existing world."""
import unreal,json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir()).resolve();assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
DEST='/Game/Terrarium/Blender/Cottage';LEVEL='/Game/Terrarium/Blender/Maps/HomesteadBlender'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mesh=unreal.load_asset(DEST+'/SM_Blender_Cottage');mat=unreal.load_asset(DEST+'/M_Cottage');tex=unreal.load_asset(DEST+'/T_Cottage_BaseColor');assert mesh and mat and tex
b=mesh.get_bounding_box();sz=b.max-b.min
assert 400<sz.x<600 and 400<sz.y<600 and 400<sz.z<550,str(sz)
(ROOT/'Docs/BlenderRebuild/Cottage/unreal-import.json').write_text(json.dumps({'project':str(ROOT),'engine':unreal.SystemLibrary.get_engine_version(),'mesh':mesh.get_path_name(),'texture':tex.get_path_name(),'material':mat.get_path_name(),'bounds_cm':{'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]},'material_slots':len(mesh.static_materials),'status':'saved_import_verified'},indent=2))
if not unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,LEVEL)
    del world
levels.eject_pilot_level_actor()
if LEVEL+'.' not in str(levels.get_current_level()):assert levels.load_level(LEVEL)
house=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Reference_Cottage')
old=next(r['mesh'] for r in json.loads((ROOT/'Docs/BlenderRebuild/world-before.json').read_text())['actors'] if r['label']=='Reference_Cottage')
house.static_mesh_component.set_static_mesh(mesh)
house.static_mesh_component.set_editor_property('override_materials',[])
# Preserve the world footprint using a uniform scale; base stays on the plateau.
house.set_actor_scale3d(unreal.Vector(.96,.96,.96))
house.set_actor_rotation(unreal.Rotator(pitch=0,yaw=-90,roll=0),False)
house.tags=[unreal.Name(x) for x in sorted(set(map(str,house.tags))|{'BlenderRebuild','FidelityReviewPending'})]
center,extent=house.get_actor_bounds(False)
camera=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='Blender_Cottage_Review'),None)
if not camera:camera=actors.spawn_actor_from_class(unreal.CameraActor,center+unreal.Vector(1000,450,520));camera.set_actor_label('Blender_Cottage_Review')
camera.set_actor_location(center+unreal.Vector(1000,450,520),False,False)
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),center),False)
cc=camera.get_component_by_class(unreal.CameraComponent);cc.set_editor_property('projection_mode',unreal.CameraProjectionMode.ORTHOGRAPHIC);cc.set_editor_property('ortho_width',1100)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
assert levels.save_current_level()
(ROOT/'Docs/BlenderRebuild/Cottage/world-placement.json').write_text(json.dumps({'level':LEVEL,'actor':house.get_actor_label(),'previous_mesh':old,'mesh':mesh.get_path_name(),'location':str(house.get_actor_location()),'rotation':str(house.get_actor_rotation()),'scale':str(house.get_actor_scale3d()),'camera':camera.get_actor_label(),'status':'placed_pending_visual_check','original_world':'/Game/Terrarium/Maps/HomesteadReference'},indent=2))
