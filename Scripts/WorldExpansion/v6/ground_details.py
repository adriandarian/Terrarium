"""Fit peripheral fields, garden walls and orchard roots to actual native terrain."""
import unreal,json
from pathlib import Path
from collections import Counter
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium');D=R/'Docs/WorldExpansion/V6'
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=E.get_editor_world();assert w.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion';assert not E.get_game_world()
ignored=[a for a in A.get_all_level_actors() if not a.get_actor_label().startswith('WX6_Terrain6_')]
def comps(mesh):return [c for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh]
def ts(mesh):return [c.get_instance_transform(i,world_space=True) for c in comps(mesh) for i in range(c.get_instance_count())]
def key(t):
 p=t.translation;q=t.rotation;s=t.scale3d;return tuple(round(v,4) for v in [p.x,p.y,p.z,q.x,q.y,q.z,q.w,s.x,s.y,s.z])
records=[]
for row in json.loads((D/'integration.json').read_text())['foliage']:
 ft=unreal.load_asset(row['type']);mesh=ft.get_editor_property('mesh');before=ts(mesh);unreal.InstancedFoliageActor.remove_all_instances(w,ft);remaining=Counter(key(t) for t in ts(mesh));own=[]
 for t in before:
  k=key(t)
  if remaining[k]:remaining[k]-=1
  else:own.append(t)
 changes=[]
 for t in own:
  p=t.translation;hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(p.x,p.y,90000),unreal.Vector(p.x,p.y,-3000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignored,unreal.DrawDebugTrace.NONE,False)
  hit=hit if isinstance(hit,unreal.HitResult) else next((h for h in (hit or []) if isinstance(h,unreal.HitResult)),None);assert hit and hit.to_tuple()[0]
  z=hit.to_tuple()[5].z-mesh.get_bounding_box().min.z*t.scale3d.z
  if abs(z-p.z)>10:changes.append({'xy_cm':[p.x,p.y],'old_z_cm':p.z,'new_z_cm':z});t.translation=unreal.Vector(p.x,p.y,z)
 prior={c.get_path_name():c.get_instance_count() for c in comps(mesh)};unreal.InstancedFoliageActor.add_instances(w,ft,own)
 cs=[{'path':c.get_path_name(),'count':c.get_instance_count()-prior.get(c.get_path_name(),0)} for c in comps(mesh) if c.get_instance_count()>prior.get(c.get_path_name(),0)];assert sum(c['count'] for c in cs)==row['count']
 records.append({'type':row['type'],'count':len(own),'components':cs,'corrections':changes})
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();(D/'detail-grounding.json').write_text(json.dumps({'groups':records,'corrected_instances':sum(len(r['corrections']) for r in records)},indent=2))
