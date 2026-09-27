import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);world='/Game/Terrarium/Blender/Maps/HomesteadBlender'
levels.eject_pilot_level_actor();assert levels.save_current_level();assert levels.load_level(world)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};tree=[]
expected=next(c['trees'] for c in json.loads((root/'Docs/SceneAssembly/changes.json').read_text())['changes'] if 'trees' in c)
for a in scene.values():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  if c.static_mesh and 'SM_Blender_HomesteadTree.' in c.static_mesh.get_path_name():
   assert c.get_instance_count()==len(expected)
   for i,e in enumerate(expected):
    t=c.get_instance_transform(i,world_space=True);s=t.scale3d;assert max(abs(v-q) for v,q in zip([s.x,s.y,s.z],e['after_scale']))<.0001;tree.append(i)
terrain=[c for a in scene.values() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and 'SM_Blender_GrassTerrain.' in c.static_mesh.get_path_name()]
paths=[]
for i in range(4):
 a=scene['SceneAssembly_NorthApproach_'+str(i)];p=a.get_actor_location();hits=[h[0].z for c in terrain if (h:=c.line_trace_component(p+unreal.Vector(0,0,70),p-unreal.Vector(0,0,70),True,False,False))];assert hits
 paths.append({'actor':a.get_actor_label(),'ground_cm':max(hits),'surface_cm':p.z+.9*.65})
levels.pilot_level_actor(scene['Baseline_Orthographic_Review']);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([]);assert levels.save_current_level()
r=json.loads((root/'Docs/SceneAssembly/verification.json').read_text());r.update(tree_instances_reloaded_verified=len(tree),north_approach_ground_checks=paths,final_camera='Baseline_Orthographic_Review',dirty_maps=[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]);assert not r['dirty_maps'];(root/'Docs/SceneAssembly/verification.json').write_text(json.dumps(r,indent=2))
