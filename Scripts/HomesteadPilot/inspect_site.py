import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def vec(v):return [v.x,v.y,v.z]
rows=[];lights=[];meshes={}
for a in A.get_all_level_actors():
 if isinstance(a,(unreal.DirectionalLight,unreal.SkyLight,unreal.PostProcessVolume)):
  lights.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'properties':str(a.get_editor_property('settings')) if isinstance(a,unreal.PostProcessVolume) else str(a.light_component.get_editor_property('intensity'))})
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if not c.static_mesh:continue
  path=c.static_mesh.get_path_name()
  if path not in meshes:
   m=c.static_mesh;bs=m.get_editor_property('body_setup');meshes[path]={'collision':str(bs.get_editor_property('collision_trace_flag')) if bs else None,'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]}
  if any(s in path for s in ['HomesteadTree','VoxelTree','CliffColumn','GrassTerrain','TrailPatch']):
   transforms=[]
   if isinstance(c,unreal.InstancedStaticMeshComponent):
    for i in range(c.get_instance_count()):
     t=c.get_instance_transform(i,world_space=True);q=t.rotation.rotator();transforms.append({'i':i,'location':vec(t.translation),'scale':vec(t.scale3d),'rotation':[q.pitch,q.yaw,q.roll]})
   rows.append({'actor':a.get_actor_label(),'mesh':path,'component':c.get_path_name(),'instances':transforms})
(R/'Docs/HomesteadPilot/site-details.json').write_text(json.dumps({'components':rows,'meshes':meshes,'lights':lights},indent=2))
