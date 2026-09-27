"""Reload and validate scene composition; provide core and expanded review cameras."""
import unreal,json,sys
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/SceneAssembly';world='/Game/Terrarium/Blender/Maps/HomesteadBlender'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.eject_pilot_level_actor();assert levels.save_current_level();assert levels.load_level(world)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
def vec(v):return [v.x,v.y,v.z]
changes=json.loads((out/'changes.json').read_text());verified=[]
for change in changes['changes']:
 if 'after' not in change:continue
 r=change['after'];a=scene[r['actor']];c=a.static_mesh_component
 assert c.static_mesh.get_path_name()==r['mesh']
 assert max(abs(v-e) for v,e in zip(vec(a.get_actor_location()),r['location']))<.02
 assert max(abs(v-e) for v,e in zip(vec(a.get_actor_scale3d()),r['scale']))<.0001
 assert all(c.get_material(i) is not None for i in range(c.get_num_materials()))
 verified.append({'actor':a.get_actor_label(),'materials':c.get_num_materials(),'location_cm':vec(a.get_actor_location()),'scale':vec(a.get_actor_scale3d())})
meshes={}
for a in scene.values():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if not c.static_mesh:continue
  key=c.static_mesh.get_path_name();meshes[key]=meshes.get(key,0)+(c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1)
inventory=json.loads((root/'Docs/BlenderRebuild/inventory.json').read_text());coverage=[]
for r in inventory['assets']:
 if r['coverage_role']!='primary_model':continue
 key=Path(r['blender_model']).parent.name;keys=[key]+[v['asset'] for v in r['placement_variants']]
 present=[{'asset':k,'instances':meshes[p]} for k in keys if (p:='/Game/Terrarium/Blender/'+k+'/SM_Blender_'+k+'.SM_Blender_'+k) in meshes]
 assert present,('Missing primary model family',key)
 coverage.append({'source':r['source'],'primary_model':key,'represented_by':present,'uses_placement_variant':not any(p['asset']==key for p in present)})
# Verify both ends of the narrower bridge still reach their bank-side bearing.
bridge=scene['Fidelity_PlankBridge_v4_001'];s=bridge.get_actor_scale3d();deck=bridge.get_actor_location().z+62*s.z
assert abs(deck-280)<.02
bridgecheck={'width_cm':143*s.x,'span_cm':333*s.y,'deck_height_cm':deck,'pile_bottom_cm':bridge.get_actor_location().z+bridge.static_mesh_component.static_mesh.get_bounding_box().min.z*s.z}
assert bridgecheck['pile_bottom_cm']<-18
# A distinct wider camera keeps the concept camera's original framing intact.
label='SceneAssembly_WholeWorld_Review';cam=scene.get(label) or actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(2564,-2566,4596.194))
cam.set_actor_label(label);cam.set_actor_rotation(unreal.Rotator(pitch=-45,yaw=135,roll=0),False)
cc=cam.camera_component;cc.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC);cc.set_ortho_width(5000);cc.set_editor_property('aspect_ratio',.85);cc.set_editor_property('constrain_aspect_ratio',True);cc.set_editor_property('post_process_blend_weight',0.)
cam.set_folder_path('SceneAssembly/ReviewCameras')
levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([])
assert levels.save_current_level()
p=cam.get_actor_location();r=cam.get_actor_rotation();args=json.loads((root/'Saved/scene-assembly-capture.json').read_text());args['captureTransform']['location']=dict(zip(['x','y','z'],vec(p)));args['captureTransform']['rotation']={'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll}
(root/'Saved/scene-assembly-overview.json').write_text(json.dumps(args))
(out/'verification.json').write_text(json.dumps({'project':str(root),'world':world,'saved_and_reloaded':True,'primary_model_families':len(coverage),'canonical_models':sum(not r['uses_placement_variant'] for r in coverage),'placement_variant_families':sum(r['uses_placement_variant'] for r in coverage),'coverage':coverage,'changed_actors_verified':verified,'bridge':bridgecheck,'limits':['Static editor composition and material validation only.','No character animation, navigation, gameplay or performance validation.','Source model fidelity differences remain; material alternatives are retained in the library.']},indent=2))
