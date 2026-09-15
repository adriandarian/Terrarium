"""Apply the house and boundary-fence reference correction in native Unreal."""
import unreal,sys,json,math,importlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/HouseFence';out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(root/'Scripts/Assets'));sys.path.insert(0,str(root/'Scripts/Fidelity'))
import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='HouseFence_Review_Transient':actors.destroy_actor(a)
review=None;baseline=None;camera=None;world=None;a=None
backup='/Game/Terrarium/Maps/HomesteadBeforeHouseFence'
if not unreal.EditorAssetLibrary.does_asset_exist(backup):
    assert levels.save_current_level()
    levels.eject_pilot_level_actor();camera=None;review=None;baseline=None;world=None
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,backup)
    world=None
    assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
def state():
    result={}
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            n=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
            if not n:continue
            key=c.static_mesh.get_name()
            result[key]={'count':n,'material':c.get_material(0).get_path_name(),
                         'transforms':[str(c.get_instance_transform(i,world_space=True)) for i in range(n)] if isinstance(c,unreal.InstancedStaticMeshComponent) else [str(a.get_actor_transform())]}
    return result
if not (out/'before.json').exists():(out/'before.json').write_text(json.dumps(state(),indent=2))
for module,method,name in [('cottage_reference','build','SM_Cottage_Reference_v2'),('fence_reference','post','SM_FencePost_Reference'),('fence_reference','rails','SM_FenceRails_Reference')]:
    if not unreal.EditorAssetLibrary.does_asset_exist('/Game/Terrarium/Meshes/'+name):
        mod=importlib.import_module(module);importlib.reload(mod);getattr(mod,method)()
material=unreal.load_asset('/Game/Terrarium/Materials/M_DetailCrafted')
house=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and 'Cottage' in a.static_mesh_component.static_mesh.get_name())
house.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/SM_Cottage_Reference_v2'))
house.static_mesh_component.set_material(0,material)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for name in ('FencePost_Detail','FenceRails_Detail'):
    ft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+name)
    unreal.InstancedFoliageActor.remove_all_instances(world,ft)
world=None
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label().startswith('ReferenceFence_'):actors.destroy_actor(a)
posts={};rails=[]
# Outer garden boundary, with the whole courtyard-facing side open. A separate
# short weathered run sits behind the shed and returns toward the cottage.
runs=[[(328,393),(374,368),(421,338),(409,307),(367,286),(307,285)],
      [(146,314),(180,294),(210,281)]]
def spawn(kind,xyz,yaw,scale,index):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*xyz))
    a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/SM_Fence'+kind+'_Reference'))
    a.static_mesh_component.set_material(0,material)
    a.set_actor_label('ReferenceFence_'+kind+'_'+str(index).zfill(3))
    a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    a.set_actor_scale3d(unreal.Vector(*scale));a.set_folder_path('HomesteadFidelity/ReferenceFence')
for run in runs:
    for start,end in zip(run,run[1:]):
        a,b=ref.world(*start,568),ref.world(*end,568)
        length=math.hypot(b[0]-a[0],b[1]-a[1]);n=max(1,round(length/175))
        yaw=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
        for i in range(n+1):
            xyz=tuple(a[k]+(b[k]-a[k])*i/n for k in range(3))
            key=(round(xyz[0],2),round(xyz[1],2))
            posts[key]=(xyz,yaw)
        for i in range(n):
            xyz=tuple(a[k]+(b[k]-a[k])*(i+.5)/n for k in range(3))
            rails.append((xyz,yaw,(length/n/170,1,.82)))
for i,(xyz,yaw) in enumerate(posts.values()):spawn('Post',xyz,yaw,(.88,.88,.82+(i%3-1)*.025),i)
for i,(xyz,yaw,scale) in enumerate(rails):spawn('Rails',xyz,yaw,scale,i)
assert levels.save_current_level()
(out/'layout.json').write_text(json.dumps({'backup':backup,'house':'SM_Cottage_Reference_v2','fence_runs_in_reference_pixels':runs,'posts':len(posts),'rail_sections':len(rails)},indent=2))
unreal.log('HOUSE_FENCE_REFERENCE_SAVED')
