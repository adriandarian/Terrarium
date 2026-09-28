"""Add private V5 forest groves on current native ground, preserving old forest."""
import json,hashlib,math
from collections import Counter
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve();assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
DOC=ROOT/'Docs/WorldExpansion';data=json.loads((DOC/'forest-groves-v5-layout.json').read_text())
terrain=json.loads((ROOT/'SourceAssets/WorldExpansion/TerrainV5/manifest.json').read_text())
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
S=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert not E.get_game_world();world=E.get_editor_world();assert world.get_path_name().split('.')[0]==data['map']
ground_labels={'WX_'+r['name'] for r in terrain['assets'] if r.get('role') in ['ground','rock']}
mesh=unreal.load_asset(data['mesh']);assert mesh and S.get_lod_count(mesh)==3 and S.get_simple_collision_count(mesh)==1
body=mesh.get_editor_property('body_setup')
assert body.get_editor_property('collision_trace_flag')==unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX
capsules=body.get_editor_property('agg_geom').get_editor_property('sphyl_elems');assert len(capsules)==1
cap=capsules[0];assert abs(cap.get_editor_property('radius')-30)<.001 and abs(cap.get_editor_property('length')-200)<.001
center=cap.get_editor_property('center');assert max(abs(center.x),abs(center.y),abs(center.z-130))<.001
source=ROOT/'Content'/(mesh.get_path_name().split('.')[0].removeprefix('/Game/')+'.uasset')
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
ignored=[a for a in A.get_all_level_actors() if isinstance(a,unreal.InstancedFoliageActor)]

def hit_ground(x,y):
    r=unreal.SystemLibrary.line_trace_single(world_context_object=world,start=unreal.Vector(x*100,y*100,30000),end=unreal.Vector(x*100,y*100,-2000),
        trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,trace_complex=True,actors_to_ignore=ignored,draw_debug_type=unreal.DrawDebugTrace.NONE,ignore_self=False)
    h=r if isinstance(r,unreal.HitResult) else next((v for v in (r or []) if isinstance(v,unreal.HitResult)),None)
    if h is None:return None
    t=h.to_tuple()
    if not t[0] or not t[9] or t[9].get_actor_label() not in ground_labels:return None
    return t[5],t[7],t[9].get_actor_label()

transforms=[];accepted=[];skipped=Counter();bounds=mesh.get_bounding_box()
for index,row in enumerate(data['instances']):
    x,y=row['xy_m'];contact=hit_ground(x,y)
    if not contact:skipped['no_current_terrain']+=1;continue
    p,n,label=contact
    if p.z<200 or p.z>10000 or n.z<.92:skipped['elevation_or_slope']+=1;continue
    # Four root probes reject planting across stepped cliff edges; trunks remain
    # vertical and the verified capsule is preserved without custom recooking.
    radius=.34*row['scale'];roots=[hit_ground(x+dx,y+dy) for dx,dy in [(radius,0),(-radius,0),(0,radius),(0,-radius)]]
    if any(r is None or abs(r[0].z-p.z)>30 for r in roots):skipped['root_crosses_step']+=1;continue
    s=row['scale'];z=p.z-bounds.min.z*s-2
    transforms.append(unreal.Transform(location=unreal.Vector(p.x,p.y,z),rotation=unreal.Rotator(pitch=0,yaw=row['yaw_deg'],roll=0),scale=unreal.Vector(s,s,s)))
    accepted.append({'source_index':index,'grove':row['grove'],'ground_cm':[p.x,p.y,p.z],
                     'location_cm':[p.x,p.y,z],'scale':s,'yaw_deg':row['yaw_deg'],'ground_actor':label})
assert len(transforms)>1500,('Unexpectedly few trees meet native ground criteria',len(transforms),dict(skipped))
dest='/Game/Terrarium/WorldExpansion/V5Forest';name='FT_WX_V5ForestGroves'
ft=unreal.load_asset(dest+'/'+name) or unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,dest,unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
ft.set_editor_property('mesh',mesh);b=ft.get_editor_property('body_instance')
b.set_editor_property('collision_profile_name','BlockAll');b.set_editor_property('collision_enabled',unreal.CollisionEnabled.QUERY_AND_PHYSICS)
ft.set_editor_property('body_instance',b)
assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
def comps():return [c for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh]
def code(t):return tuple(round(v,5) for v in [t.translation.x,t.translation.y,t.translation.z,t.scale3d.x,t.scale3d.y,t.scale3d.z,t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w])
unreal.InstancedFoliageActor.remove_all_instances(world,ft)
existing=Counter(code(c.get_instance_transform(i,world_space=True)) for c in comps() for i in range(c.get_instance_count()))
before={c.get_path_name():c.get_instance_count() for c in comps()}
unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
after=Counter(code(c.get_instance_transform(i,world_space=True)) for c in comps() for i in range(c.get_instance_count()))
assert not +(existing-after),'Existing forest transform removed/changed'
assert sum((after-existing).values())==len(transforms)
components=[{'component':c.get_path_name(),'count':c.get_instance_count()-before.get(c.get_path_name(),0)} for c in comps() if c.get_instance_count()>before.get(c.get_path_name(),0)]
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
receipt={'map':data['map'],'mesh':mesh.get_path_name(),'foliage_type':ft.get_path_name(),'components':components,
         'planned_trees':len(data['instances']),'native_trees':len(transforms),'skipped':dict(skipped),'by_grove':dict(Counter(r['grove'] for r in accepted)),
         'native_lod_triangles':[mesh.get_num_triangles(i) for i in range(3)],'simple_capsules':1,'capsule_radius_cm':30,'capsule_length_cm':200,
         'collision':'BlockAll / existing verified simple trunk capsule','distance_culling':'Default no distance cut; retain forest masses in full region views',
         'source_mesh_sha256':source_hash,'source_mesh_unchanged':True,'old_forest_transforms_preserved':True,
         'instances':accepted,'limits':'Native source/capsule/count/contact verification; reopened visual and pawn checks follow.'}
(DOC/'forest-groves-v5-integration.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({'planned':len(data['instances']),'native':len(transforms),'skipped':dict(skipped)}))
