import unreal,json,sys
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
terrain=[c for a in actors for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and 'SM_Blender_GrassTerrain.' in c.static_mesh.get_path_name()]
rows=[]
for key,px,py,z in [('Player',177,394,560),('RangerSela',285,350,560),('Kindlehorn',95,270,560),('Rillip',350,476,280),('HomesteadCompound',-130,280,560),('CivicHall',-155,70,560)]:
 x,y,_=ref.world(px,py,z);hits=[]
 for dx,dy in [(0,0),(-50,-50),(50,50),(-200,-200),(200,200),(-400,-300),(400,300)]:
  hh=[h[0].z for c in terrain if (h:=c.line_trace_component(unreal.Vector(x+dx,y+dy,z+120),unreal.Vector(x+dx,y+dy,z-90),True,False,False))]
  hits.append({'offset':[dx,dy],'z':max(hh) if hh else None})
 rows.append({'key':key,'location':[x,y,z],'samples':hits})
props=[]
for a in actors:
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh and 'SM_Blender_HomesteadTree.' in c.static_mesh.get_path_name():
   pr={}
   for k in ['visible','hidden_in_game','instance_start_cull_distance','instance_end_cull_distance','cached_max_draw_distance','min_draw_distance','ld_max_draw_distance','never_distance_cull']:
    try:pr[k]=str(c.get_editor_property(k))
    except:pass
   props.append(pr)
(root/'Docs/SceneAssembly/placement-preflight.json').write_text(json.dumps({'sites':rows,'tree_visibility':props},indent=2))
