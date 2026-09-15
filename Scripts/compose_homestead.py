"""Phase 2 scene orchestration; each discipline and each mesh has its own module."""
import unreal,sys,math,json,importlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
path='/Game/Terrarium/Maps/Homestead'
if not unreal.EditorAssetLibrary.does_asset_exist(path):
    assert levels.load_level('/Game/Terrarium/Maps/RenderBaseline')
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,path)
    world=None
assert levels.load_level(path)
assert '/Homestead.' in str(levels.get_current_level())
sys.path.insert(0,str(root/'Scripts/Scene'))
import placement,terrain,paths,homestead,vegetation
for m in [placement,terrain,paths,homestead,vegetation]:importlib.reload(m)
actors=placement.actors
for a in list(actors.get_all_level_actors()):
    if isinstance(a,unreal.StaticMeshActor):actors.destroy_actor(a)
terrain.build();paths.build();homestead.build();vegetation.build()
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
camera=scene['Baseline_Orthographic_Review']
pitch=-52;yaw=135;distance=6500
forward=unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)),math.cos(math.radians(pitch))*math.sin(math.radians(yaw)),math.sin(math.radians(pitch)))
camera.set_actor_location(placement.world(0,30,220)-forward*distance,False,False)
camera.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False)
camera.camera_component.set_ortho_width(2650)
camera.camera_component.set_editor_property('aspect_ratio',.68)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
p=root/'Docs/Phase2';p.mkdir(parents=True,exist_ok=True)
(p/'composition.json').write_text(json.dumps({'map':path,'placed_meshes':dict(placement.counts),'total':sum(placement.counts.values()),'camera':{'pitch':pitch,'yaw':yaw,'ortho_width':2650,'aspect':.68},'terrain_heights_cm':[60,372,684]},indent=2))
unreal.log('HOMESTEAD_COMPOSITION_COMPLETE')
