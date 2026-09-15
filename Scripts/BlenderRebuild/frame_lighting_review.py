"""Fixed native cameras for comparing shade and sunlit materials."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};view=(root/'Saved/lighting-review-view.txt').read_text().strip()
if view in ['Crest','Tonic']:
    key,shift,offset={'Crest':('Blender_EmberCrest_MarketFront',(0,0,13.7),(0,72,-25.5)),'Tonic':('Blender_MossTonic_MarketCounter',(1,0,9.8),(25,49,25))}[view]
    focus=scene[key].get_actor_location()+unreal.Vector(*shift);location=focus+unreal.Vector(*offset)
    rotation=unreal.MathLibrary.find_look_at_rotation(location,focus);fov=42
else:
    ref={'Cottage':'Cottage/unreal-camera.json','Terrace':'MossFringe/ThinFringe/unreal-camera.json'}[view]
    record=json.loads((root/'Docs/BlenderRebuild'/ref).read_text())
    location=unreal.Vector(**record['cameraLocation']);rotation=unreal.Rotator(**record['cameraRotation']);fov=record['cameraFOV']
label='Blender_Lighting_Review';cam=scene.get(label) or actors.spawn_actor_from_class(unreal.CameraActor,location);cam.set_actor_label(label)
cam.set_actor_location(location,False,False);cam.set_actor_rotation(rotation,False);cam.get_component_by_class(unreal.CameraComponent).set_editor_property('field_of_view',fov)
actors.set_selected_level_actors([]);levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
args={'captureTransform':{'location':{'x':location.x,'y':location.y,'z':location.z},'rotation':{'pitch':rotation.pitch,'yaw':rotation.yaw,'roll':rotation.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/lighting-review-capture.json').write_text(json.dumps(args))
assert levels.save_current_level()
