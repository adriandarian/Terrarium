"""Check the open counter interval between Tonic and Prism for Storm."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
scene={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
counter=scene['Blender_MarketStall_UpperPath'].static_mesh_component
rows=[]
for x in [390,395,400,405,410,415,420]:
    for y in [619,621,624]:
        hit=counter.line_trace_component(unreal.Vector(x,y,670),unreal.Vector(x,y,630),True,False,False)
        rows.append({'xy':[x,y],'z':hit[0].z if hit else None})
neighbors=[]
for label,actor in scene.items():
    p=actor.get_actor_location()
    if 380<p.x<435 and 605<p.y<635:
        c,e=actor.get_actor_bounds(False)
        neighbors.append({'label':label,'center':[c.x,c.y,c.z],'extent':[e.x,e.y,e.z]})
(root/'Docs/BlenderRebuild/Storm/site-preflight.json').write_text(json.dumps({'counter_samples':rows,'nearby_actors':neighbors},indent=2))
