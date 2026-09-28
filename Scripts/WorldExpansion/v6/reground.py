"""Reground only regional private foliage, preserving count/XY/rotation/scale."""
import unreal,json,hashlib
from pathlib import Path
from collections import Counter
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w=E.get_editor_world();assert w.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion';assert not E.get_game_world()
L.eject_pilot_level_actor()
# Explicit identity avoids editor placement offsets for world-space source meshes.
for a in A.get_all_level_actors():
 if a.get_actor_label().startswith('WX6_') and (a.get_actor_label().startswith('WX6_Terrain6_') or a.get_actor_label() in ['WX6_'+q['name'] for q in json.loads((R/'Docs/WorldExpansion/V6/layout.json').read_text())['geometry']]):a.set_actor_transform(unreal.Transform(location=unreal.Vector(0,0,0),rotation=unreal.Rotator(0,0,0),scale=unreal.Vector(1,1,1)),False,False)
actors=A.get_all_level_actors();ignored=[a for a in actors if not a.get_actor_label().startswith('WX6_Terrain6_') and not a.get_actor_label().startswith('WX_VoxelChunk64')]
# Look up the preserved apron labels from the source contract.
apron=next(c for c in json.loads((R/'SourceAssets/WorldExpansion/TerrainV5/manifest.json').read_text())['chunks'] if c['old_actor']=='WX_HomeApron')
ground={'WX_'+n for n in apron['assets']}|{a.get_actor_label() for a in actors if a.get_actor_label().startswith('WX6_Terrain6_')}
ignored=[a for a in actors if a.get_actor_label() not in ground]
types=[]
for folder in ['Forest','EcologyV5/Foliage','V5Forest']:
 for p in unreal.EditorAssetLibrary.list_assets('/Game/Terrarium/WorldExpansion/'+folder,recursive=True,include_folder=False):
  obj=unreal.load_asset(p)
  if isinstance(obj,unreal.FoliageType_InstancedStaticMesh):types.append(obj)
def comps(mesh):return [c for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh]
def transforms(mesh):return [c.get_instance_transform(i,world_space=True) for c in comps(mesh) for i in range(c.get_instance_count())]
def key(t):
 p=t.translation;q=t.rotation;s=t.scale3d;return tuple(round(v,4) for v in [p.x,p.y,p.z,q.x,q.y,q.z,q.w,s.x,s.y,s.z])
records=[]
for ft in types:
 mesh=ft.get_editor_property('mesh');before=transforms(mesh);unreal.InstancedFoliageActor.remove_all_instances(w,ft);remaining=Counter(key(t) for t in transforms(mesh));removed=[]
 for t in before:
  k=key(t)
  if remaining[k]:remaining[k]-=1
  else:removed.append(t)
 assert not +remaining
 out=[];changes=[];failed=[];minimum=mesh.get_bounding_box().min.z
 for t in removed:
  p=t.translation;hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(p.x,p.y,90000),unreal.Vector(p.x,p.y,-3000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignored,unreal.DrawDebugTrace.NONE,False)
  hit=hit if isinstance(hit,unreal.HitResult) else next((h for h in (hit or []) if isinstance(h,unreal.HitResult)),None);ht=hit.to_tuple() if hit else None
  if not ht or not ht[0]:failed.append([p.x,p.y]);out.append(t);continue
  z=ht[5].z-minimum*t.scale3d.z-5;changes.append(abs(z-p.z));t.translation=unreal.Vector(p.x,p.y,z);out.append(t)
 unreal.InstancedFoliageActor.add_instances(w,ft,out)
 assert len(transforms(mesh))==len(before)
 records.append({'type':ft.get_path_name(),'count':len(out),'failed_ground_traces':failed,'max_z_change_cm':max(changes,default=0)})
 assert not failed,(ft.get_name(),failed[:3])
assert L.save_current_level();(R/'Docs/WorldExpansion/V6/reground.json').write_text(json.dumps({'groups':records,'total':sum(r['count'] for r in records)},indent=2));print('Regrounded',sum(r['count'] for r in records))
