import unreal,json,math,random,sys
from pathlib import Path
from collections import defaultdict
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(R/'Scripts/WorldExpansion'));import terrain_source as terrain
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);w=E.get_editor_world();assert w.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion';assert not E.get_game_world();L.eject_pilot_level_actor()
data=json.loads((R/'Docs/WorldExpansion/ecology-v5-integration.json').read_text())['groups'];ignored=[a for a in A.get_all_level_actors() if not a.get_actor_label().startswith('WX6_Terrain6_')];rng=random.Random(9726);groups=defaultdict(list)
for y0 in range(-620,651,6):
 if -75<y0<125 or -315<y0<-250:continue
 for side in [-1,1]:
  for offset,k in [(3,'ShoreOutcrop'),(5,'Grass'),(8,'Bush'),(12,'GroundPlants')]:
   if k=='ShoreOutcrop' and rng.random()<.45:continue
   y=y0+rng.uniform(-2.4,2.4);x=terrain.river_center_x(y)+side*(terrain.river_halfwidth(y)+offset+rng.uniform(-1,2));d,z,rw,_=terrain.road_info(x,y)
   if d<rw/2+4:continue
   hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x*100,y*100,90000),unreal.Vector(x*100,y*100,-3000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignored,unreal.DrawDebugTrace.NONE,False)
   hit=hit if isinstance(hit,unreal.HitResult) else next((h for h in (hit or []) if isinstance(h,unreal.HitResult)),None);h=hit.to_tuple() if hit else None
   if not h or not h[0] or h[5].z<0 or h[7].z<.65:continue
   mesh=unreal.load_asset(data[k]['mesh']);s=rng.uniform(.75,1.4);z=h[5].z-mesh.get_bounding_box().min.z*s-(20 if k=='ShoreOutcrop' else 10)
   groups[k].append(unreal.Transform(location=unreal.Vector(x*100,y*100,z),rotation=unreal.Rotator(pitch=0,yaw=rng.uniform(0,360),roll=0),scale=unreal.Vector(s,s,s)))
AT=unreal.AssetToolsHelpers.get_asset_tools();out=[]
for k,ts in groups.items():
 name='FT_River6_'+k;path='/Game/Terrarium/WorldExpansion/V6/Foliage';ft=unreal.load_asset(path+'/'+name) or AT.create_asset(name,path,unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());ft.set_editor_property('mesh',unreal.load_asset(data[k]['mesh']));body=ft.get_editor_property('body_instance');body.set_editor_property('collision_profile_name','NoCollision');body.set_editor_property('collision_enabled',unreal.CollisionEnabled.NO_COLLISION);ft.set_editor_property('body_instance',body);assert unreal.EditorAssetLibrary.save_loaded_asset(ft);unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 before={c.get_path_name():c.get_instance_count() for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent)};unreal.InstancedFoliageActor.add_instances(w,ft,ts)
 cs=[{'path':c.get_path_name(),'count':c.get_instance_count()-before.get(c.get_path_name(),0)} for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.get_instance_count()>before.get(c.get_path_name(),0)];assert sum(c['count'] for c in cs)==len(ts)
 out.append({'type':ft.get_path_name(),'count':len(ts),'components':cs})
assert L.save_current_level();(R/'Docs/WorldExpansion/V6/river-ecology.json').write_text(json.dumps({'groups':out,'count':sum(r['count'] for r in out)},indent=2));print('Riparian details',sum(r['count'] for r in out))
