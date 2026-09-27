import unreal,json,sys,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();terrain=[c for a in actors for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and 'SM_Blender_GrassTerrain.' in c.static_mesh.get_path_name()]
results={}
for key,points,rx,ry in [('HomesteadCompound',[(-65,150),(-55,210),(-30,160),(-30,240),(-20,190)],345,470),('CivicHall',[(90,-95),(130,-95),(40,-65),(160,-75),(100,-45)],280,230)]:
 candidates=[]
 for px,py in points:
  x,y,z=ref.world(px,py,560);hits=[]
  for dx,dy in [(0,0),(-rx,-ry),(-rx,ry),(rx,-ry),(rx,ry)]:
   hh=[h[0].z for c in terrain if (h:=c.line_trace_component(unreal.Vector(x+dx,y+dy,660),unreal.Vector(x+dx,y+dy,500),True,False,False))]
   hits.append(max(hh) if hh else None)
  candidates.append({'pixel':[px,py],'location':[x,y,z],'heights':hits,'supported':all(h is not None for h in hits)})
 results[key]=candidates
(root/'Docs/SceneAssembly/building-sites.json').write_text(json.dumps(results,indent=2))
