"""Create separate native review cameras for a static bank actor and an instanced patch."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Game/Terrarium/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
r=json.loads((root/'Docs/BlenderRebuild/Riverbank/instance-placement.json').read_text())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
for name,point,offset in [('Actor',[56.90399627764168,-1530.8680816610001,30],[230,-360,300]),('Foliage',[-155.9718709080302,-1568.102197443675,55],[300,-380,400])]:
    label='Blender_Riverbank_'+name+'_Review';focus=unreal.Vector(*point)
    cam=scene.get(label) or actors.spawn_actor_from_class(unreal.CameraActor,focus)
    cam.set_actor_label(label);cam.set_actor_location(focus+unreal.Vector(*offset),False,False)
    cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),focus),False)
    cam.get_component_by_class(unreal.CameraComponent).set_editor_property('field_of_view',34)
    actors.set_selected_level_actors([]);levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
    p=cam.get_actor_location();q=cam.get_actor_rotation()
    args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':q.pitch,'yaw':q.yaw,'roll':q.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
    (root/'Saved'/('blender-riverbank-'+name.lower()+'-capture.json')).write_text(json.dumps(args))
assert levels.save_current_level()
