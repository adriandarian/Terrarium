"""Reload and verify all transforms and material bindings for a foliage migration."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
key=(root/'Saved/blender-import-asset.txt').read_text().strip();assert key in ['HomesteadTree','WheatPatch','Riverbank','MossFringe']
folder=root/'Docs/BlenderRebuild'/key;record=json.loads((folder/'instance-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(record['world'])
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
mesh=unreal.load_asset(record['mesh']);oldmesh=unreal.load_asset(record['old_mesh'])
actual=[];old_count=0
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh==mesh:
            assert c.get_material(0)==mesh.get_material(0)
            actual.extend(serial(c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count()))
        if c.static_mesh==oldmesh:old_count+=c.get_instance_count()
assert len(actual)==record['count'] and old_count==0
expected=[r['after'] for r in record['instances']];sortkey=lambda t:tuple(round(x,3) for x in t['translation'])
assert all(abs(v-e)<.0001 for a,b in zip(sorted(actual,key=sortkey),sorted(expected,key=sortkey)) for k in a for v,e in zip(a[k],b[k]))
assert unreal.load_asset(record['old_foliage_type']).get_editor_property('mesh')==oldmesh
assert unreal.load_asset(record['new_foliage_type']).get_editor_property('mesh')==mesh
assert mesh.get_material(0).get_editor_property('used_with_instanced_static_meshes') and len(mesh.static_materials)==1
imported=json.loads((folder/'unreal-import.json').read_text());exported=json.loads((folder/'mesh-validation.json').read_text())
assert imported['source_fbx_sha256']==exported['files']['SM_Blender_'+key+'.fbx']['sha256']
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
for row in record.get('static_actors',[]):
    a=scene[row['actor']];c=a.static_mesh_component
    assert c.static_mesh==mesh and c.get_material(0)==mesh.get_material(0)
    actual_transform=serial(a.get_actor_transform())
    assert all(abs(v-e)<.0001 for k in actual_transform for v,e in zip(actual_transform[k],row['after'][k]))
(folder/'saved-world-verification.json').write_text(json.dumps({'world':record['world'],'reloaded_from_disk':True,'instances':len(actual),'static_actors_verified':len(record.get('static_actors',[])),'all_transforms_verified':True,'material_bindings_verified':True,'export_import_hashes_match':True,'prior_foliage_mesh_binding_preserved':True,'fidelity':'not_accepted','limits':'Appearance requires viewport inspection; no gameplay or performance test.'},indent=2))
unreal.log('BLENDER_FOLIAGE_RELOAD_VERIFIED_'+key)
