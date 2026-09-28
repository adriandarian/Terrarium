"""Place deterministic clustered woodland using private persistent FoliageTypes."""
import unreal,json,random
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);w=E.get_editor_world()
assert w.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
assert not E.get_game_world()
data=json.loads((R/'SourceAssets/WorldExpansion/Terrain/manifest.json').read_text())
dest='/Game/Terrarium/WorldExpansion/Forest';at=unreal.AssetToolsHelpers.get_asset_tools()
rows=[]
for key,every,collision in [('BroadTree5m',1,True),('ShrubGroundcover',3,False)]:
 private=unreal.load_asset('/Game/Terrarium/WorldExpansion/Forest/SM_WX_'+key)
 mesh=private or unreal.load_asset('/Game/Terrarium/HomesteadPilot/Landscape/Meshes/SM_'+key);assert mesh
 path=dest+'/FT_WX_'+key
 ft=unreal.load_asset(path) or at.create_asset('FT_WX_'+key,dest,unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
 ft.set_editor_property('mesh',mesh)
 body=ft.get_editor_property('body_instance')
 body.set_editor_property('collision_profile_name','BlockAll' if collision else 'NoCollision')
 body.set_editor_property('collision_enabled',unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision else unreal.CollisionEnabled.NO_COLLISION)
 ft.set_editor_property('body_instance',body)
 assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
 unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 def count():
  return sum(c.get_instance_count() for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh)
 before=count();ts=[]
 for row in data['forest_instances'][::every]:
  x,y,z=[v*100 for v in row['location_m']];s=row['scale']*(1 if collision else .9)
  z-=mesh.get_bounding_box().min.z*s
  ts.append(unreal.Transform(location=unreal.Vector(x,y,z),rotation=unreal.Rotator(pitch=0,yaw=row['yaw'],roll=0),scale=unreal.Vector(s,s,s)))
 unreal.InstancedFoliageActor.add_instances(w,ft,ts)
 after=count();assert after-before==len(ts),(key,before,after,len(ts))
 rows.append({'mesh':mesh.get_path_name(),'foliage_type':ft.get_path_name(),'instances':len(ts),'collision':collision,'actual_lods':mesh.get_num_lods()})
assert L.save_current_level()
(R/'Docs/WorldExpansion/forest-integration.json').write_text(json.dumps({'groups':rows,'seed':data['seed'],'source_meshes_modified':False},indent=2))
