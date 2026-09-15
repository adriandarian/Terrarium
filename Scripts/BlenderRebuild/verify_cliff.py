"""Reload the saved cliff replacement and verify all placements and sampled cap collision."""
import unreal,json
from pathlib import Path
from collections import Counter
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/CliffColumn';r=json.loads((folder/'instance-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(r['world'])
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();mesh=unreal.load_asset(r['mesh'])
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def code(t):return json.dumps({k:[round(v,5) for v in values] for k,values in t.items()},sort_keys=True)
components=[c for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh]
assert sum(c.get_instance_count() for c in components)==r['count']==2076
groups=[];checks=[]
for g in r['groups']:
    oldmesh=unreal.load_asset(g['old_mesh']);assert unreal.load_asset(g['old_foliage_type']).get_editor_property('mesh')==oldmesh
    assert unreal.load_asset(g['new_foliage_type']).get_editor_property('mesh')==mesh
    assert not [c for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent) if c.static_mesh==oldmesh and c.get_instance_count()]
    matches=[c for c in components if c.get_instance_count()==g['count']];assert len(matches)==1;c=matches[0]
    actual=[serial(c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count())]
    assert Counter(code(t) for t in actual)==Counter(code(t) for t in g['transforms'])
    assert c.get_material(0)==mesh.get_material(0)
    assert c.get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS
    assert c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)==unreal.CollisionResponseType.ECR_BLOCK
    groups.append({'suffix':g['suffix'],'component':c.get_name(),'count':c.get_instance_count(),'profile':str(c.get_collision_profile_name()),'all_transforms_verified':True})
    for i in range(0,c.get_instance_count(),max(1,c.get_instance_count()//12)):
        t=c.get_instance_transform(i,world_space=True);p=t.translation;z=p.z+323.5*t.scale3d.z
        def trace(end):return unreal.SystemLibrary.line_trace_single(world,unreal.Vector(p.x,p.y,z+.2),unreal.Vector(p.x,p.y,end),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,ignore_self=False)
        above=trace(z+.04);below=trace(z-.04)
        assert above is None and below is not None,(c.get_name(),i,z,str(above),str(below))
        checks.append({'component':c.get_name(),'index':i,'cap_height_cm':z,'tolerance_cm':.04,'passed':True})
exported=json.loads((folder/'mesh-validation.json').read_text());imported=json.loads((folder/'unreal-import.json').read_text())
assert exported['files']['SM_Blender_CliffColumn.fbx']['sha256']==imported['source_fbx_sha256']
# The two lowered staircase cliff instances now belong to the new A component.
stair=root/'Docs/BlenderRebuild/StoneStairs/terrain-adjustment.json';data=json.loads(stair.read_text())
for row in data['instances']:
    if 'SM_Env_Cliff_A_R2.' not in row['mesh']:continue
    matches=[]
    for c in components:
        for i in range(c.get_instance_count()):
            p=c.get_instance_transform(i,world_space=True).translation
            if all(abs(a-b)<.01 for a,b in zip(vec(p),row['after_cm'])):matches.append((c,i))
    assert len(matches)==1;c,i=matches[0]
    row['replacement_component']=c.get_name();row['replacement_index']=i;row['replacement_mesh']=mesh.get_path_name()
stair.write_text(json.dumps(data,indent=2))
(folder/'saved-world-verification.json').write_text(json.dumps({'world':r['world'],'reloaded_from_disk':True,'count':r['count'],'groups':groups,'import_export_hash_match':True,'surface_probes':checks,'limits':'Sampled visibility traces; no character traversal, performance or perfect-fidelity approval.'},indent=2))
unreal.log('BLENDER_CLIFF_RELOAD_VERIFIED')
