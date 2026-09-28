"""Coordinator-only native-ground placement of the additive ecology V5 plan.

Optional Docs/WorldExpansion/ecology-v5-request.json: {"groups":["Grass"]}.
Omit request/groups for all groups. Each group is independently idempotent.
"""
import json, math, hashlib
from pathlib import Path
from collections import Counter,defaultdict
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve();assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
DOC=ROOT/'Docs/WorldExpansion';data=json.loads((DOC/'ecology-v5-layout.json').read_text())
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not E.get_game_world();world=E.get_editor_world();assert world.get_path_name().split('.')[0]==data['map']
terrain=json.loads((ROOT/'SourceAssets/WorldExpansion/Terrain/manifest.json').read_text())
ground_labels={'WX_'+r['name'] for r in terrain['assets'] if r['kind']=='terrain'}
v5_terrain_path=ROOT/'SourceAssets/WorldExpansion/TerrainV5/manifest.json'
if v5_terrain_path.exists():
    v5_terrain=json.loads(v5_terrain_path.read_text())
    # V5 has separate collidable stepped ground and rock assets, including
    # walkable rocky hilltops. HomeApron retains its existing actor label.
    ground_labels.update('WX_'+r['name'] for r in v5_terrain['assets'] if r.get('role') in ['ground','rock'])
actors=A.get_all_level_actors();ignored=[a for a in actors if isinstance(a,unreal.InstancedFoliageActor)]
groups=defaultdict(list)
for index,row in enumerate(data['instances']):groups[row['asset']].append((index,row))
request_path=DOC/'ecology-v5-request.json';request=json.loads(request_path.read_text()) if request_path.exists() else {}
selected=request.get('groups',sorted(groups));assert set(selected)<=set(groups)
DEST='/Game/Terrarium/WorldExpansion/EcologyV5';AT=unreal.AssetToolsHelpers.get_asset_tools()
receipt_path=DOC/'ecology-v5-integration.json'
receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else {'map':data['map'],'groups':{},'seed':data['seed']}
receipt['accepted_ground_actor_labels']=sorted(ground_labels)

def vec(v):return [v.x,v.y,v.z]
def ground(x,y):
    result=unreal.SystemLibrary.line_trace_single(world_context_object=world,start=unreal.Vector(x*100,y*100,90000),end=unreal.Vector(x*100,y*100,-3000),
        trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,trace_complex=True,actors_to_ignore=ignored,
        draw_debug_type=unreal.DrawDebugTrace.NONE,ignore_self=False)
    hit=result if isinstance(result,unreal.HitResult) else next((v for v in (result or []) if isinstance(v,unreal.HitResult)),None)
    if hit is None:return None,'no_hit'
    t=hit.to_tuple()
    if not bool(t[0]):return None,'no_blocking_hit'
    actor=t[9];label=actor.get_actor_label() if actor else ''
    if label not in ground_labels:return None,'non_terrain_hit:'+label
    if t[5].z<15:return None,'water_level_or_riverbed'
    if t[7].z<.86:return None,'slope_above_30_degrees'
    return (t[5],t[7],label),None

for key in selected:
    spec=data['assets'][key];mesh=unreal.load_asset(spec['mesh']);assert isinstance(mesh,unreal.StaticMesh)
    source_file=ROOT/'Content'/(mesh.get_path_name().split('.')[0].removeprefix('/Game/')+'.uasset')
    source_hash=hashlib.sha256(source_file.read_bytes()).hexdigest()
    bounds=mesh.get_bounding_box();dims=bounds.max-bounds.min
    # Source-scale contract catches selecting a similarly named oversized variant.
    assert max(abs(x-y) for x,y in zip(vec(dims),[v*100 for v in spec['native_dimensions_m']]))<.3,(key,vec(dims))
    transforms=[];accepted=[];skipped=Counter()
    for index,row in groups[key]:
        x,y=row['xy_m'];contact,reason=ground(x,y)
        if contact is None:skipped[reason]+=1;continue
        point,normal,label=contact;s=row['scale']
        radius=max(dims.x*s[0],dims.y*s[1])/2
        # Embed the low side of tiny ground assets on slopes, keeping all plant
        # roots and broad stones in the ground without changing the terrain.
        slope=math.sqrt(max(0,1-normal.z*normal.z))/max(.001,normal.z)
        embed_cm=row['embed_m']*100+min(18,radius*slope*.6)
        z=point.z-bounds.min.z*s[2]-embed_cm
        t=unreal.Transform(location=unreal.Vector(point.x,point.y,z),rotation=unreal.Rotator(pitch=0,yaw=row['yaw_deg'],roll=0),scale=unreal.Vector(*s))
        transforms.append(t);accepted.append({'source_index':index,'ground_cm':vec(point),'normal':vec(normal),
            'ground_actor':label,'location_cm':vec(t.translation),'scale':s,'yaw_deg':row['yaw_deg'],'embed_cm':embed_cm})
    assert transforms,(key,'All placements rejected; inspect current terrain first')
    name='FT_WX_EcologyV5_'+key;path=DEST+'/Foliage/'+name
    ft=unreal.load_asset(path) or AT.create_asset(name,DEST+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
    ft.set_editor_property('mesh',mesh);body=ft.get_editor_property('body_instance')
    body.set_editor_property('collision_profile_name','NoCollision');body.set_editor_property('collision_enabled',unreal.CollisionEnabled.NO_COLLISION)
    ft.set_editor_property('body_instance',body)
    # Native foliage distance culling limits tiny ground details to useful range.
    # Record actual property support rather than allowing an optional setting to
    # strand otherwise valid source placements on a different editor build.
    cull_end=18000 if key in ['Grass','GroundPlants','Flowers'] else 35000 if key in ['Bush','ShrubGroundcover'] else 60000
    cull_status='not_set'
    try:
        ft.set_editor_property('cull_distance',unreal.Int32Interval(min=int(cull_end*.8),max=cull_end));cull_status='configured'
    except Exception as exc:cull_status='unsupported:'+str(exc)
    assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.remove_all_instances(world,ft)
    before={c.get_path_name():c.get_instance_count() for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh}
    unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
    components=[];total=0
    for a in A.get_all_level_actors():
        for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
            if c.static_mesh!=mesh:continue
            delta=c.get_instance_count()-before.get(c.get_path_name(),0)
            if delta:
                assert delta>0;components.append(c.get_path_name());total+=delta
    assert total==len(transforms),(key,total,len(transforms))
    assert hashlib.sha256(source_file.read_bytes()).hexdigest()==source_hash,'Source package changed'
    receipt['groups'][key]={'mesh':mesh.get_path_name(),'foliage_type':ft.get_path_name(),'components':components,
        'planned_count':len(groups[key]),'native_instance_count':total,'skipped':dict(skipped),'native_bounds_cm':[vec(bounds.min),vec(bounds.max)],
        'native_lod_count':mesh.get_num_lods(),'material_bindings':[s.material_interface.get_path_name() if s.material_interface else None for s in mesh.static_materials],
        'collision':'NoCollision','distance_culling_status':cull_status,'requested_cull_end_cm':cull_end,
        'source_sha256':source_hash,'source_package_unchanged':True,'instances':accepted}
    receipt['summary']={'planned_count':len(data['instances']),'integrated_count':sum(r['native_instance_count'] for r in receipt['groups'].values()),
        'completed_groups':sorted(receipt['groups']),'remaining_groups':sorted(set(groups)-set(receipt['groups']))}
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    receipt_path.write_text(json.dumps(receipt,indent=2))
    unreal.log('Ecology V5 %s: %d native instances, %d skipped'%(key,total,sum(skipped.values())))
print(json.dumps(receipt['summary']))
