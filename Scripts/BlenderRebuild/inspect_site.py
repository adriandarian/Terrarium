"""Read live world geometry inside a requested XY rectangle before placement."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
request=json.loads((root/'Saved/blender-site-request.json').read_text());x0,x1,y0,y1=request['bounds_xy_cm']
rows=[];static=[]
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    components=actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
    for c in components:
        if not c.static_mesh:continue
        points=[]
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,world_space=True);p=t.translation
            if x0<p.x<x1 and y0<p.y<y1:points.append({'index':i,'position':[p.x,p.y,p.z]})
        if points:rows.append({'actor':actor.get_actor_label(),'component':c.get_name(),'mesh':c.static_mesh.get_name(),'instances':points})
    if isinstance(actor,unreal.StaticMeshActor):
        p,e=actor.get_actor_bounds(False)
        if p.x+e.x>x0 and p.x-e.x<x1 and p.y+e.y>y0 and p.y-e.y<y1:static.append({'actor':actor.get_actor_label(),'center':[p.x,p.y,p.z],'extent':[e.x,e.y,e.z]})
(root/'Saved'/('blender-site-'+request['asset']+'.json')).write_text(json.dumps({'request':request,'instances':rows,'static_actors':static},indent=2))
