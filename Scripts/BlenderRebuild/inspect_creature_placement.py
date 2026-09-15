import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();rows=[]
for actor in actors:
    if any(key in actor.get_actor_label().lower() for key in ['grass','trail','courtyard','cottage','terrain']):
        p=actor.get_actor_location();c,e=actor.get_actor_bounds(False)
        rows.append({'actor':actor.get_actor_label(),'location':[p.x,p.y,p.z],'center':[c.x,c.y,c.z],'extent':[e.x,e.y,e.z]})
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
components=[(actor.get_actor_label(),c) for actor in actors for c in actor.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh]
samples=[]
for x in [300,500,700,900]:
    for y in [-600,-400,-200,0,200,400]:
        hits=[]
        for label,c in components:
            hit=c.line_trace_component(unreal.Vector(x,y,1800),unreal.Vector(x,y,0),True,False,False)
            if hit:hits.append({'actor':label,'component':c.get_name(),'mesh':c.static_mesh.get_path_name(),'z':hit[0].z})
        samples.append({'xy':[x,y],'hits':sorted(hits,key=lambda h:h['z'],reverse=True)[:3]})
(root/'Docs/BlenderRebuild/Brambit/placement-search.json').write_text(json.dumps({'actors':rows,'samples':samples},indent=2))
