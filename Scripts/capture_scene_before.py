import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);l=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
s={o.get_actor_label():o for o in a.get_all_level_actors()};cam=s['Baseline_Orthographic_Review']
l.pilot_level_actor(cam);l.set_exact_camera_view(True);l.editor_set_game_view(True);a.set_selected_level_actors([])
# Native captures are made with Scripts/BlenderRebuild/capture_viewport.py.
meshes={}
for o in s.values():
 for c in o.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh:
   key=c.static_mesh.get_path_name();meshes[key]=meshes.get(key,0)+(c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1)
missing=[]
for folder in (root/'SourceAssets/Blender').iterdir():
 p='/Game/Terrarium/Blender/'+folder.name+'/SM_Blender_'+folder.name
 if (folder/(folder.name+'.blend')).exists():
  m=unreal.load_asset(p)
  if m and m.get_path_name() not in meshes:
   b=m.get_bounding_box();missing.append({'key':folder.name,'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]})
(root/'Docs/SceneAssembly/coverage-before.json').write_text(json.dumps({'meshes':meshes,'missing':missing},indent=2))
