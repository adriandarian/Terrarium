"""Temporary QA viewpoints. The saved hero camera is never moved."""
import unreal,sys,json,math
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Scene'))
from placement import world
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Homestead.' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='Temporary_QA_Camera':actors.destroy_actor(a)
r=json.loads((root/'Saved/scene-review-request.json').read_text())
if r.get('restore'):
    camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
else:
    camera=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
    camera.set_actor_label('Temporary_QA_Camera')
    p=r['pitch'];y=r['yaw'];d=6500
    forward=unreal.Vector(math.cos(math.radians(p))*math.cos(math.radians(y)),math.cos(math.radians(p))*math.sin(math.radians(y)),math.sin(math.radians(p)))
    camera.set_actor_location(world(0,0,250)-forward*d,False,False)
    camera.set_actor_rotation(unreal.Rotator(pitch=p,yaw=y,roll=0),False)
    camera.camera_component.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC)
    camera.camera_component.set_ortho_width(r.get('width',3300))
    camera.camera_component.set_editor_property('aspect_ratio',1.35)
    camera.camera_component.set_editor_property('post_process_blend_weight',0.0)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
