"""Reload the map and verify every migrated instance and actor transform."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/Environment';record=json.loads((folder/'instance-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(record['world'])
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def matches(a,b):return all(abs(v-e)<.0001 for k in a for v,e in zip(a[k],b[k]))
shrub=unreal.load_asset(record['shrub_mesh']);rock=unreal.load_asset(record['rock_mesh'])
ft=unreal.load_asset(record['new_foliage_type']);assert ft.get_editor_property('mesh')==shrub
oldft=unreal.load_asset(record['old_foliage_type']);oldmesh=oldft.get_editor_property('mesh');assert oldmesh.get_name()=='SM_Recon_MeadowShrub_R3'
actual=[];old_count=0
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh==shrub:
            assert c.get_material(0)==shrub.get_material(0)
            actual.extend(serial(c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count()))
        if c.static_mesh==oldmesh:old_count+=c.get_instance_count()
assert old_count==0 and len(actual)==record['shrub_count']
expected=[r['after'] for r in record['shrubs']]
sortkey=lambda t:tuple(round(x,3) for x in t['translation'])
assert all(matches(a,b) for a,b in zip(sorted(actual,key=sortkey),sorted(expected,key=sortkey)))
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
for row in record['rocks']:
    a=scene[row['actor']];assert a.static_mesh_component.static_mesh==rock
    assert a.static_mesh_component.get_material(0)==rock.get_material(0)
    assert matches(serial(a.get_actor_transform()),row['after'])
for mesh,key in [(shrub,'MeadowShrub'),(rock,'MossRock')]:
    assert len(mesh.static_materials)==1 and mesh.get_material(0).get_name()=='M_'+key
    imported=json.loads((root/'Docs/BlenderRebuild'/key/'unreal-import.json').read_text())
    exported=json.loads((root/'Docs/BlenderRebuild'/key/'mesh-validation.json').read_text())
    assert imported['source_fbx_sha256']==exported['files']['SM_Blender_'+key+'.fbx']['sha256']
assert shrub.get_material(0).get_editor_property('used_with_instanced_static_meshes')
(folder/'saved-world-verification.json').write_text(json.dumps({'world':record['world'],'reloaded_from_disk':True,'shrub_count':len(actual),'rock_count':len(record['rocks']),'all_migrated_transforms_verified':True,'source_foliage_asset_unchanged':True,'material_bindings_verified':True,'export_import_hashes_match':True,'fidelity':'pending_visual_refinement','limits':'No character or performance test; anchoring and appearance require viewport inspection.'},indent=2))
unreal.log('BLENDER_ENVIRONMENT_RELOAD_VERIFIED')
