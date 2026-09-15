"""Inspect live terrain and instance occupancy for the lodge site."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if not c.static_mesh:continue
        points=[]
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,world_space=True);p=t.translation
            if -2500<p.x<-1900 and -500<p.y<100:points.append({'index':i,'position':[p.x,p.y,p.z]})
        if points:rows.append({'actor':a.get_actor_label(),'component':c.get_name(),'mesh':c.static_mesh.get_name(),'instances':points})
(root/'Saved/blender-lodge-site.json').write_text(json.dumps(rows,indent=2))
