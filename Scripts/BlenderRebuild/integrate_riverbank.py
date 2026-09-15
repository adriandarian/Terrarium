"""Migrate foliage and static riverbank placements while preserving the old shared asset."""
import unreal,json,math,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/Riverbank';receipt=folder/'instance-placement.json'
assert not receipt.exists(),'Already migrated; inspect recorded transforms before refining'
before_path=root/'Saved/blender-foliage-Riverbank.json';before=json.loads(before_path.read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==before['world'] and '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert len(before['foliage_types'])==1 and len(before['static_actors'])==7
oldft=unreal.load_asset(before['foliage_types'][0]['path']);oldmesh=oldft.get_editor_property('mesh')
mesh=unreal.load_asset('/Game/Terrarium/Blender/Riverbank/SM_Blender_Riverbank');assert mesh
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def instances(m):return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==m for i in range(c.get_instance_count())]
jobs=instances(oldmesh);assert len(jobs)==28 and not instances(mesh)
assert [serial(t) for t in jobs]==[t for c in before['components'] for t in c['transforms']]
ob=oldmesh.get_bounding_box();nb=mesh.get_bounding_box()
area_ratio=((ob.max.x-ob.min.x)*(ob.max.y-ob.min.y))/((nb.max.x-nb.min.x)*(nb.max.y-nb.min.y))
def fit(t):
    initial=serial(t);scale=math.sqrt(t.scale3d.x*t.scale3d.y*area_ratio)
    p=t.translation;p.z+=ob.min.z*t.scale3d.z-nb.min.z*scale;t.translation=p;t.scale3d=unreal.Vector(scale,scale,scale)
    return {'before':initial,'after':serial(t)}
changes=[fit(t) for t in jobs]
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};statics=[]
for row in before['static_actors']:
    a=scene[row['actor']];t=a.get_actor_transform()
    assert a.static_mesh_component.static_mesh==oldmesh and serial(t)==row['transform']
    statics.append((a,t,{'actor':row['actor'],**fit(t)}))
dest='/Game/Terrarium/Blender/Riverbank/FT_Blender_Riverbank';assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest);assert ft
ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[]);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
shutil.copyfile(before_path,folder/'before-placement.json')
unreal.InstancedFoliageActor.add_instances(world,ft,jobs);assert len(instances(mesh))==28
unreal.InstancedFoliageActor.remove_all_instances(world,oldft);assert not instances(oldmesh)
for a,t,row in statics:
    a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_editor_property('override_materials',[])
    a.set_actor_transform(t,False,False)
assert levels.save_current_level()
receipt.write_text(json.dumps({'asset':'Riverbank','world':world.get_path_name().split('.')[0],'old_foliage_type':oldft.get_path_name(),'new_foliage_type':ft.get_path_name(),'old_mesh':oldmesh.get_path_name(),'mesh':mesh.get_path_name(),'count':28,'static_count':7,'instances':changes,'static_actors':[r for a,t,r in statics],'scale_policy':'Uniform scale preserves each preceding XY mesh-bounds footprint area; no inherited stretching. Original root elevation retained pending bank-contact review.','status':'saved_pending_visual_review'},indent=2))
unreal.log('BLENDER_RIVERBANK_MIGRATED')
