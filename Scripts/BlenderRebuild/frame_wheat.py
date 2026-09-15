"""Frame the migrated wheat in its actual upper-terrace field."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve()
assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Game/Terrarium/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
record=json.loads((root/'Docs/BlenderRebuild/WheatPatch/instance-placement.json').read_text())
focus=unreal.Vector(-1380,300,922)
label='Blender_WheatField_Review'
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
cam=scene.get(label) or actors.spawn_actor_from_class(unreal.CameraActor,focus)
cam.set_actor_label(label)
cam.set_actor_location(focus+unreal.Vector(1625,-1950,1690),False,False)
cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),focus),False)
cam.get_component_by_class(unreal.CameraComponent).set_editor_property('field_of_view',46)
actors.set_selected_level_actors([]);levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
assert levels.save_current_level()
p=cam.get_actor_location();r=cam.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/blender-wheat-capture.json').write_text(json.dumps(args))
