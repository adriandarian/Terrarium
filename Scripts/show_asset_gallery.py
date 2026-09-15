"""Phase 1 review display only; this is not the homestead composition."""
import unreal,json,math
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
assert '/ModularGallery.' in str(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level())
root=Path(unreal.Paths.project_dir())
layout=[
 ('SM_OrchardTree',-1060,660),('SM_Cottage',-320,660),('SM_Shed',440,660),('SM_WheatPatch',1110,660),
 ('SM_PlankBridge',-1060,-80),('SM_CliffWall',-270,-40),('SM_StoneStairs',500,-50),('SM_PerimeterWall',1140,-40),
 ('SM_GardenBed',-1110,-700),('SM_Bush',-680,-690),('SM_FencePost',-370,-700),('SM_FenceRails',-155,-690),
 ('SM_GrassTile',230,-700),('SM_PathTile',670,-700),('SM_WaterTile',1110,-700)]
for name,_,_ in layout:
 d=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
 assert d['visual_review'].startswith('passed'),name+' not reviewed'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
scene['Baseline_Ground'].set_actor_location(unreal.Vector(0,0,-50),False,False)
for a in list(scene.values()):
 if a.get_actor_label()=='Asset_Inspection' or a.get_actor_label().startswith('Study_'):actors.destroy_actor(a)
for name,u,v in layout:
 x=(-u-v)/math.sqrt(2);y=(-u+v)/math.sqrt(2)
 z={'SM_GrassTile':26,'SM_PathTile':16.5,'SM_WaterTile':24}.get(name,0)
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z))
 a.set_actor_label('Study_'+name[3:])
 a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/'+name))
 a.set_folder_path('Phase1/ModularStudies')
camera=scene['Baseline_Orthographic_Review']
pitch=-40;yaw=135;distance=4300
forward=unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)),math.cos(math.radians(pitch))*math.sin(math.radians(yaw)),math.sin(math.radians(pitch)))
camera.set_actor_location(unreal.Vector(0,0,150)-forward*distance,False,False)
camera.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False)
camera.camera_component.set_ortho_width(3200)
camera.camera_component.set_editor_property('aspect_ratio',1.7)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
levels.save_current_level()
(root/'Docs/Phase1/gallery-layout.json').write_text(json.dumps(layout,indent=2))
