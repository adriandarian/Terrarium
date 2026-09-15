"""Reload the world; verify placement and actual imported paver/soil collision."""
import unreal,json,hashlib,math
from pathlib import Path
from collections import Counter
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/TrailPatch';r=json.loads((folder/'instance-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(r['world'])
mesh=unreal.load_asset(r['mesh']);oldmesh=unreal.load_asset(r['old_mesh']);scene=actors.get_all_level_actors()
def vec(p):return [p.x,p.y,p.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def same(actual,expected):
    return all(abs(a-b)<(.001 if key=='translation' else .000001) for key in actual for a,b in zip(actual[key],expected[key]))
components=[];jobs=[]
for a in scene:
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh==oldmesh:
            assert isinstance(c,unreal.FoliageInstancedStaticMeshComponent) and c.get_instance_count()==0
        if c.static_mesh!=mesh:continue
        assert c.get_material(0)==mesh.get_material(0)
        assert c.get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS
        assert c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)==unreal.CollisionResponseType.ECR_BLOCK
        if isinstance(c,unreal.FoliageInstancedStaticMeshComponent):
            components.append(c);jobs.extend((c.get_name()+':'+str(i),c,c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count()))
        else:jobs.append((a.get_actor_label(),c,a.get_actor_transform()))
assert len(jobs)==84 and sum(c.get_instance_count() for c in components)==61
actual=[serial(t) for label,c,t in jobs];expected=[row['after'] for g in r['groups'] for row in g['instances']]+[row['after'] for row in r['static_actors']]
for t in expected:assert sum(same(a,t) for a in actual)==1
for group in r['groups']:
    assert unreal.load_asset(group['old_foliage_type']).get_editor_property('mesh')==oldmesh
    ft=unreal.load_asset(group['new_foliage_type']);assert ft.get_editor_property('mesh')==mesh
for path in r['unused_original_foliage_types']:assert unreal.load_asset(path).get_editor_property('mesh')==oldmesh
checks=[]
for label,c,t in jobs:
    p=t.translation
    hit=c.line_trace_component(unreal.Vector(p.x,p.y,p.z+15),unreal.Vector(p.x,p.y,p.z-2),trace_complex=True,show_trace=False,persistent_show_trace=False)
    assert hit is not None,(label,'missing path center collision')
    checks.append({'placement':label,'xy_cm':[p.x,p.y],'surface_z_cm':hit[0].z,'trace_scope':'own path component; overlapping instances of the same component can be the first hit'})
asset_checks=[]
for key in ['TrailTerrain','TrailPatch']:
    f=root/'Docs/BlenderRebuild'/key;exported=json.loads((f/'mesh-validation.json').read_text());imported=json.loads((f/'unreal-import.json').read_text())
    assert exported['files']['SM_Blender_'+key+'.fbx']['sha256']==imported['source_fbx_sha256']
    original=root/exported['source'];copy=root/'SourceAssets/Blender'/key/(key+'_BaseColor.png');assert original.read_bytes()==copy.read_bytes()
    m=unreal.load_asset(imported['mesh']);assert m.get_editor_property('body_setup').get_editor_property('collision_trace_flag')==unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
    samples=json.loads((f/'collision-samples.json').read_text())['samples'];origin=unreal.Vector(100000,100000,10000)
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,origin);a.set_actor_label('Temporary_Blender_Trail_Collision_Probe');c=a.static_mesh_component;c.set_static_mesh(m);c.set_collision_profile_name('BlockAll')
    try:
        attempts=[]
        # FBX converts the handedness. Verify the complete sample set, rather
        # than assuming an axis sign from a symmetric bounding box.
        for ysign in [1,-1]:
            measured=[]
            for s in samples:
                x,y=s['local_xy_cm'];x+=origin.x;y=origin.y+y*ysign
                h=c.line_trace_component(unreal.Vector(x,y,origin.z+10),unreal.Vector(x,y,origin.z-2),trace_complex=True,show_trace=False,persistent_show_trace=False)
                z=h[0].z-origin.z if h is not None else None
                measured.append({**s,'actual_z_cm':z,'passed':z is not None and abs(z-s['expected_z_cm'])<.04})
            attempts.append({'blender_y_to_unreal_y_sign':ysign,'samples':measured,'all_passed':all(s['passed'] for s in measured)})
        passing=[a for a in attempts if a['all_passed']];assert len(passing)==1,(key,attempts)
        asset_checks.append({'asset':key,'source_albedo_byte_identical':True,'import_hash_matches_export':True,**passing[0]})
    finally:actors.destroy_actor(a)
assert levels.save_current_level()
(folder/'saved-world-verification.json').write_text(json.dumps({'world':r['world'],'reloaded_from_disk':True,'foliage_count':61,'static_count':23,'all_transforms_and_bindings_verified':True,'original_foliage_assets_preserved':True,'center_collision_checks':checks,'isolated_imported_mesh_collision':asset_checks,'limits':'Center traces verify path collision presence, not complete terrain support. Two ground-before edge samples remain unsupported. Other same-component instances can overlap center queries. Isolated mesh probes separately verify actual paver and soil heights. No character traversal or performance test; visual fidelity remains unaccepted.'},indent=2))
unreal.log('BLENDER_TRAIL_RELOAD_VERIFIED')
