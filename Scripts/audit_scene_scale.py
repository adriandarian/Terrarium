import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=[]
for o in a.get_all_level_actors():
 for c in o.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh and any(k in c.static_mesh.get_name() for k in ['Tree','Wheat','RiverBridge','CliffColumn']):
   b=c.static_mesh.get_bounding_box();r={'actor':o.get_actor_label(),'mesh':c.static_mesh.get_name(),'size':str(b.max-b.min),'scale':str(c.get_world_scale())}
   if isinstance(c,unreal.InstancedStaticMeshComponent):r.update(count=c.get_instance_count(),instances=[str(c.get_instance_transform(i,world_space=True)) for i in range(min(c.get_instance_count(),14))])
   rows.append(r)
(root/'Docs/SceneAssembly/scale-audit.json').write_text(json.dumps(rows,indent=2))
