"""Editor-only original-mesh placement with efficient native static instancing."""
import unreal,math,random,json
from collections import Counter,defaultdict
from pathlib import Path
import reference as ref
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
counts=Counter();batches=defaultdict(list);rng=random.Random(120917);meshes={}
def mesh(name):
    if name not in meshes:
        path='/Game/Terrarium/Meshes/SM_'+name
        meshes[name]=unreal.load_asset(path);assert meshes[name],path
        report=json.loads(Path(unreal.Paths.project_dir(),'Docs/Phase1/Validation','SM_'+name+'.json').read_text())
        assert report['saved_normal_errors']==0 and report['visual_review'].startswith('passed')
    return meshes[name]

def place_xyz(name,xyz,scale=1,yaw=0,group='Details',instanced=True):
    sm=mesh(name);counts[name]+=1
    if not isinstance(scale,tuple):scale=(scale,scale,scale)
    rot=unreal.Rotator(pitch=0,yaw=yaw,roll=0)
    if instanced:
        batches[name].append(unreal.Transform(location=unreal.Vector(*xyz),rotation=rot,scale=unreal.Vector(*scale)))
        return None
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*xyz))
    a.set_actor_label('Fidelity_'+name+'_'+str(counts[name]).zfill(3))
    a.static_mesh_component.set_static_mesh(sm)
    a.set_actor_rotation(rot,False);a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_folder_path('Fidelity/'+group)
    return a

def place(name,px,py,z,scale=1,yaw=0,group='Details',instanced=True):
    return place_xyz(name,ref.world(px,py,z),scale,yaw,group,instanced)

def flush():
    for name,transforms in batches.items():
        path='/Game/Terrarium/Foliage/FT_'+name
        ft=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset('FT_'+name,'/Game/Terrarium/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
        assert ft
        ft.set_editor_property('mesh',mesh(name))
        unreal.EditorAssetLibrary.save_loaded_asset(ft)
        unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
    batches.clear()
    for a in actors.get_all_level_actors():
        if isinstance(a,unreal.InstancedFoliageActor):a.set_actor_label('Fidelity_StaticInstances')
