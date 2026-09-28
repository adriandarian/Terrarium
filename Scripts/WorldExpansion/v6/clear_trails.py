import unreal,json,math
from pathlib import Path
from collections import Counter
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
D=R/'Docs/WorldExpansion/V6';E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=E.get_editor_world();assert w.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion';assert not E.get_game_world()
paths=json.loads((D/'landmark-integration.json').read_text())['paths']
def distance(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)));return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def ts(mesh):return [c.get_instance_transform(i,world_space=True) for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh for i in range(c.get_instance_count())]
def key(t):
 p=t.translation;q=t.rotation;s=t.scale3d;return tuple(round(v,4) for v in [p.x,p.y,p.z,q.x,q.y,q.z,q.w,s.x,s.y,s.z])
records=[]
for p in ['/Game/Terrarium/WorldExpansion/Forest/FT_WX_BroadTree5m','/Game/Terrarium/WorldExpansion/V5Forest/FT_WX_V5ForestGroves']:
 ft=unreal.load_asset(p);mesh=ft.get_editor_property('mesh');before=ts(mesh);unreal.InstancedFoliageActor.remove_all_instances(w,ft);remaining=Counter(key(t) for t in ts(mesh));own=[]
 for t in before:
  k=key(t)
  if remaining[k]:remaining[k]-=1
  else:own.append(t)
 kept=[];removed=[]
 for t in own:
  xy=[t.translation.x/100,t.translation.y/100]
  collision=any(distance(xy,a,b)<q['width']/2+2.5 for q in paths for a,b in zip(q['points'],q['points'][1:]))
  if collision:removed.append(xy)
  else:kept.append(t)
 unreal.InstancedFoliageActor.add_instances(w,ft,kept);assert len(ts(mesh))==len(before)-len(removed)
 records.append({'type':p,'before':len(own),'after':len(kept),'removed_xy_m':removed})
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();(D/'trail-clearance.json').write_text(json.dumps({'groups':records,'removed_count':sum(len(r['removed_xy_m']) for r in records)},indent=2))
