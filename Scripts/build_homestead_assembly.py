"""Build and integrate the complete isolated-reference homestead family."""
import unreal,sys,json,importlib,gc,math
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/HomesteadAssembly';out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(root/'Scripts/Assets'));sys.path.insert(0,str(root/'Scripts/Fidelity'))
import homestead_assembly as family,reference as ref
importlib.reload(family)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label() in ('HouseFence_Review_Transient','Assembly_Review_Transient'):actors.destroy_actor(a)
a=None;camera=None;review=None;baseline=None;world=None;gc.collect()
backup='/Game/Terrarium/Maps/HomesteadBeforeAssemblyReference'
if not unreal.EditorAssetLibrary.does_asset_exist(backup):
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,backup)
    world=None;assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
for name,build in family.BUILDERS.items():
    if not unreal.EditorAssetLibrary.does_asset_exist('/Game/Terrarium/Meshes/'+name):build()
material=unreal.load_asset('/Game/Terrarium/Materials/M_AssemblyCrafted') or unreal.load_asset('/Game/Terrarium/Materials/M_DetailCrafted')
mapping={'SM_Cottage_Reference_v2':'SM_Assembly_Cottage_v2','SM_Shed_Context_Reference':'SM_Assembly_BlueShed_v2',
 'SM_CourtyardTower_Reference':'SM_Assembly_Tower','SM_LanternPost_Detail':'SM_Assembly_Lantern',
 'SM_GardenBed_v3_Detail':'SM_Assembly_VegetableBed','SM_CourtyardFlowerBed_Reference':'SM_Assembly_FlowerBorder'}
replaced={}
for a in actors.get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor) or not a.static_mesh_component.static_mesh:continue
    old=a.static_mesh_component.static_mesh.get_name()
    if old in mapping:
        name=mapping[old];a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/'+name))
        a.static_mesh_component.set_material(0,material);a.set_actor_label(name[3:]);a.set_folder_path('HomesteadFidelity/Assembly')
        if name=='SM_Assembly_Tower':a.set_actor_scale3d(unreal.Vector(1.08,1.08,1.08))
        if name=='SM_Assembly_FlowerBorder':
            a.set_actor_location(unreal.Vector(*ref.world(383,352,570)),False,False)
            a.set_actor_scale3d(unreal.Vector(1.1,1.1,1.1))
        replaced[old]=name
assert set(replaced)==set(mapping) or all(unreal.EditorAssetLibrary.does_asset_exist('/Game/Terrarium/Meshes/'+n) for n in mapping.values())
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label().startswith(('ReferenceFence_','AssemblyFence_')):actors.destroy_actor(a)
fence_runs=[[(330,397),(431,345),(310,292)],[(144,312),(208,282)]]
posts={};rails=[]
for run in fence_runs:
    for first,last in zip(run,run[1:]):
        v,w=ref.world(*first,568),ref.world(*last,568);length=math.hypot(w[0]-v[0],w[1]-v[1])
        n=max(1,round(length/175));yaw=math.degrees(math.atan2(w[1]-v[1],w[0]-v[0]))
        for i in range(n+1):
            xyz=tuple(v[k]+(w[k]-v[k])*i/n for k in range(3));posts[(round(xyz[0],2),round(xyz[1],2))]=(xyz,yaw)
        for i in range(n):rails.append((tuple(v[k]+(w[k]-v[k])*(i+.5)/n for k in range(3)),yaw,length/n/170))
def fence(kind,xyz,yaw,scale,i):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*xyz))
    a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/SM_Assembly_Fence'+kind))
    a.static_mesh_component.set_material(0,material);a.set_actor_label('AssemblyFence_'+kind+'_'+str(i))
    a.set_actor_scale3d(unreal.Vector(*scale));a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    a.set_folder_path('HomesteadFidelity/Assembly')
for i,(xyz,yaw) in enumerate(posts.values()):fence('Post',xyz,yaw,(.90,.90,.88),i)
for i,(xyz,yaw,sx) in enumerate(rails):fence('Rails',xyz,yaw,(sx,1,.88),i)
assert levels.save_current_level()
(out/'integration.json').write_text(json.dumps({'backup':backup,'asset_mapping':mapping,'fence_runs':fence_runs,
 'fence_posts':len(posts),'fence_sections':len(rails),'source_image':'codex-clipboard-9fcedba1-2186-4ac3-9363-19e0ee7d4446.png'},indent=2))
a=None;world=None;gc.collect()
unreal.log('HOMESTEAD_ASSEMBLY_INTEGRATED')
exec(compile((root/'Scripts/refine_homestead_assembly.py').read_text(),str(root/'Scripts/refine_homestead_assembly.py'),'exec'),globals())
exec(compile((root/'Scripts/fit_homestead_assembly.py').read_text(),str(root/'Scripts/fit_homestead_assembly.py'),'exec'),globals())
