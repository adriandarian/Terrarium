"""Whole-scene pass 2: final reference-facing composition and softer fill."""
import unreal,sys,math,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Scene'))
from placement import world
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Homestead.' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
camera=scene['Baseline_Orthographic_Review']
pitch=-45;yaw=153;distance=6500
forward=unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)),math.cos(math.radians(pitch))*math.sin(math.radians(yaw)),math.sin(math.radians(pitch)))
camera.set_actor_location(world(20,50,230)-forward*distance,False,False)
camera.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False)
camera.camera_component.set_ortho_width(2550)
camera.camera_component.set_editor_property('aspect_ratio',.66)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
(root/'Docs/Phase3/pass-2-settings.json').write_text(json.dumps({'pass':2,'camera_pitch':pitch,'camera_yaw':yaw,'ortho_width':2550,'changes':['Framing matches ascending right-hand terraces in reference','Extended terrain beyond frame','Cliff courses retain original unstretched proportions','Removed trees obscuring bridge and wheat','Added original stones wildflowers and reeds']},indent=2))
