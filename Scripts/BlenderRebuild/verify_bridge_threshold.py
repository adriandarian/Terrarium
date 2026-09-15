"""Reload and verify source geometry, bearing transforms and the bank-to-deck lane."""
import unreal,json,math,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/BridgeThreshold';r=json.loads((folder/'world-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(r['world'])
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();scene=actors.get_all_level_actors();matches=[a for a in scene if a.get_actor_label()==r['actor']];assert len(matches)==1
a=matches[0];c=a.static_mesh_component;mesh=unreal.load_asset(r['mesh']);assert c.static_mesh==mesh and c.get_material(0)==mesh.get_material(0)
assert c.get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS and c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)==unreal.CollisionResponseType.ECR_BLOCK
assert mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')==unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
def serial(t):
    q=t.rotation;return {'translation':[t.translation.x,t.translation.y,t.translation.z],'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z],'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def same(t,row):return all(abs(x-y)<1e-5 for k,v in serial(t).items() for x,y in zip(v,row[k]))
contact=json.loads((folder/'clearance-inspection.json').read_text());assert same(a.get_actor_transform(),contact['threshold_transform'])
bridge=next(o for o in scene if o.get_actor_label()=='Fidelity_PlankBridge_v4_001');assert same(bridge.get_actor_transform(),contact['bridge_transform'])
cliffs={x.get_name():x for o in scene for x in o.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if x.static_mesh and x.static_mesh.get_name()=='SM_Blender_CliffColumn'}
for row in contact['nearby_cliffs']:assert same(cliffs[row['component']].get_instance_transform(row['index'],world_space=True),row['transform'])
assert not contact['issues']
bearings=json.loads((folder/'bearing-verification.json').read_text());assert bearings['all_four_bearings_verified']
exported=json.loads((folder/'mesh-validation.json').read_text());imported=json.loads((folder/'unreal-import.json').read_text())
assert exported['files']['SM_Blender_BridgeThreshold.fbx']['sha256']==imported['source_fbx_sha256']
for kind in ['BaseColor','Emission','Roughness']:
    source=root/'SourceAssets/Blender/RiverBridge'/('RiverBridge_'+kind+'.png');copy=root/'SourceAssets/Blender/BridgeThreshold'/('BridgeThreshold_'+kind+'.png');assert source.read_bytes()==copy.read_bytes()
probes=[];t=a.get_actor_transform()
for sample in json.loads((folder/'collision-samples.json').read_text())['samples']:
    x,y=sample['blender_xy_cm'];p=unreal.MathLibrary.transform_location(t,unreal.Vector(x,-y,0))
    hit=c.line_trace_component(unreal.Vector(p.x,p.y,p.z+20),unreal.Vector(p.x,p.y,p.z-35),trace_complex=True,show_trace=False,persistent_show_trace=False)
    assert hit is not None and abs(hit[0].z-p.z-sample['height_cm'])<.04,(sample,str(hit))
    probes.append({**sample,'actual_local_height_cm':hit[0].z-p.z,'passed':True})
parts=[x for o in scene for x in o.get_components_by_class(unreal.StaticMeshComponent) if x.static_mesh and x.static_mesh.get_name() in ['SM_Blender_GrassTerrain','SM_Blender_CliffColumn','SM_Blender_TrailPatch','SM_Blender_RiverBridge','SM_Blender_BridgeThreshold']]
p=bridge.get_actor_location();angle=math.radians(bridge.get_actor_rotation().yaw)
def xy(across,along):return (p.x+across*math.cos(angle)-along*math.sin(angle),p.y+across*math.sin(angle)+along*math.cos(angle))
def center(along):return 50*min(1,max(0,(-320-along)/100))
lanes=[];center_points=[]
for offset in [-24,0,24]:
    lane=[]
    for along in range(-430,-319,2):
        across=center(along)+offset;x,y=xy(across,along);hits=[]
        for component in parts:
            hit=component.line_trace_component(unreal.Vector(x,y,310),unreal.Vector(x,y,260),trace_complex=True,show_trace=False,persistent_show_trace=False)
            if hit is not None:hits.append({'height_cm':hit[0].z,'mesh':component.static_mesh.get_name()})
        assert hits,('unsupported lane sample',offset,along,across)
        top=max(hits,key=lambda h:h['height_cm']);assert 279.9<=top['height_cm']<=287.5,top
        lane.append({'along_cm':along,'across_cm':across,'top':top})
        if offset==0:center_points.append(unreal.Vector(x,y,top['height_cm']+92))
    max_step=max(abs(x['top']['height_cm']-y['top']['height_cm']) for x,y in zip(lane,lane[1:]));assert max_step<2.0,(offset,max_step)
    lanes.append({'lateral_offset_cm':offset,'samples':lane,'maximum_adjacent_height_change_cm':max_step})
sweeps=0
for start,end in zip(center_points,center_points[1:]):
    for first,last in [(start,end),(end,start)]:
        hit=unreal.SystemLibrary.capsule_trace_single(world,first,last,34,88,unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,ignore_self=False)
        assert hit is None,('capsule corridor blocked',str(first),str(last),str(hit));sweeps+=1
(folder/'saved-world-verification.json').write_text(json.dumps({'world':r['world'],'reloaded_from_disk':True,'actor_and_material_binding_verified':True,'nearby_bearing_transforms_verified':True,'import_export_hash_match':True,'material_atlas_matches_bridge_bytes':True,'modeled_surface_probes':probes,'bearing_samples':4,'path_overlap_samples':contact['samples_with_underlying_path'],'minimum_path_clearance_cm':contact['minimum_clearance_cm'],'supported_lanes':lanes,'capsule_sweeps':sweeps,'capsule_radius_cm':34,'capsule_half_height_cm':88,'capsule_foot_clearance_cm':4,'limits':'Surface support sampled every 2 cm across three lanes; not every point of the wider banks. Capsule sweeps follow the measured surface with 4 cm clearance, in both directions. These are collision checks, not a character-controller playtest or performance test. The threshold is a site adaptation; canonical river_crossing reference and visual fidelity remain separate.'},indent=2))
unreal.log('BRIDGE_THRESHOLD_SAVED_WORLD_VERIFIED')
