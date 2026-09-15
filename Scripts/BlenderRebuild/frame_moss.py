"""Frame a longer moss fringe on the rebuilt courtyard cliff."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
items=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if not c.static_mesh or c.static_mesh.get_name()!='SM_Blender_MossFringe':continue
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,world_space=True)
            if t.scale3d.z>.30:items.append((c,i,t))
c,index,t=min(items,key=lambda r:(r[2].translation.x+1000)**2+(r[2].translation.y+250)**2)
p=t.translation;normal=unreal.MathLibrary.transform_direction(t,unreal.Vector(1,0,0));tangent=unreal.Vector(-normal.y,normal.x,0)
focus=p+normal*8+unreal.Vector(0,0,-12)
campos=focus+normal*185+tangent*80+unreal.Vector(0,0,95)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};label='Blender_MossFringe_Review'
cam=scene.get(label) or actors.spawn_actor_from_class(unreal.CameraActor,campos);cam.set_actor_label(label)
cam.set_actor_location(campos,False,False);cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(campos,focus),False)
cam.get_component_by_class(unreal.CameraComponent).set_editor_property('field_of_view',42)
actors.set_selected_level_actors([]);levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);assert levels.save_current_level()
p=cam.get_actor_location();r=cam.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/blender-moss-capture.json').write_text(json.dumps(args))
(root/'Docs/BlenderRebuild/MossFringe/review-placement.json').write_text(json.dumps({'component':c.get_name(),'index':index,'translation_cm':[t.translation.x,t.translation.y,t.translation.z],'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z]},indent=2))
