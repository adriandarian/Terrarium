"""Native editor correction of the complete blue-house ground vignette."""
import unreal,sys,json,math,random,importlib,gc,re
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/BlueHouseContext';out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(root/'Scripts/Assets'));sys.path.insert(0,str(root/'Scripts/Fidelity'))
import reference as ref,courtyard_layout,shed_context
importlib.reload(courtyard_layout);importlib.reload(shed_context)
from paths_v7 import sample_track
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='HouseFence_Review_Transient':actors.destroy_actor(a)
a=None;review=None;camera=None;baseline=None;world=None;gc.collect()
backup='/Game/Terrarium/Maps/HomesteadBeforeBlueHouseContext'
if not unreal.EditorAssetLibrary.does_asset_exist(backup):
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,backup)
    world=None
    assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def xyz(a):
    p=a.get_actor_location();return ref.pixel(p.x,p.y,560)
def in_area(px,py):return 99<px<173 and 307<py<378
def all_components():return [c for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh]
material=unreal.load_asset('/Game/Terrarium/Materials/M_DetailCrafted')
for name,method in [('SM_Shed_Context_Reference','build'),('SM_Shed_FlatStones','stones')]:
    if not unreal.EditorAssetLibrary.does_asset_exist('/Game/Terrarium/Meshes/'+name):getattr(shed_context,method)()
shed=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name().startswith('SM_Shed_'))
before=str(shed.get_actor_transform());shed.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/SM_Shed_Context_Reference'))
assert str(shed.get_actor_transform()).split('Rotation:')[-1]==before.split('Rotation:')[-1]
shed=None
def spawn(name,label,px,py,z,scale=1,yaw=0,mat=None):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*ref.world(px,py,z)))
    a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/'+name))
    a.static_mesh_component.set_material(0,mat or material);a.set_actor_label(label)
    a.set_folder_path('HomesteadFidelity/BlueHouseContext')
    a.set_actor_scale3d(unreal.Vector(*(scale if isinstance(scale,tuple) else (scale,)*3)))
    a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    return a
# Remove the obsolete doorway spur and dressing in this small ground region.
removed_actors=[]
for a in list(actors.get_all_level_actors()):
    label=a.get_actor_label()
    if label.startswith(('BlueHouse_','CourtyardPath_shed')) or (label.startswith(('CourtyardPlant_','CourtyardStone_')) and in_area(*xyz(a))):
        removed_actors.append(label);actors.destroy_actor(a)
cover=['SM_Bush_v2_Detail','SM_GroundPlants_v2_Detail','SM_MeadowGrass_v2_Detail','SM_MeadowFlowers_v2_Detail','SM_RockCluster_Detail']
materials={};removed={}
for name in cover:
    comp=next(c for c in all_components() if c.static_mesh.get_name()==name and isinstance(c,unreal.FoliageInstancedStaticMeshComponent))
    materials[name]=comp.get_material(0);keep=[];cut=[]
    for i in range(comp.get_instance_count()):
        t=comp.get_instance_transform(i,world_space=True);p=t.translation
        if abs(p.z-560)<25 and in_area(*ref.pixel(p.x,p.y,560)):cut.append(str(t))
        else:keep.append(t)
    comp=None
    ft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+name[3:]);assert ft
    unreal.InstancedFoliageActor.remove_all_instances(world,ft)
    unreal.InstancedFoliageActor.add_instances(world,ft,keep)
    removed[name]=len(cut)
path_mat=next(c.get_material(0) for c in all_components() if c.static_mesh.get_name()=='SM_PathTile_v4_Detail')
path=next(p for label,p,w in courtyard_layout.PATHS if label=='shed')
for i,(center,yaw,length) in enumerate(sample_track([ref.world(*p,560) for p in path],spacing=64)):
    px,py=ref.pixel(*center,560)
    spawn('SM_PathTile_v4_Detail','BlueHouse_Approach_'+str(i),px,py,571,(length/188,55/200,.65),yaw,path_mat)
# Broad, low gray slabs lie to the right of the doorway, not a shrub mound.
for i,(px,py,s,yaw) in enumerate([(155,347,1.08,12),(157,351,.72,-19),(109,350,.64,47)]):
    spawn('SM_Shed_FlatStones','BlueHouse_Stone_'+str(i),px,py,572,s,yaw,materials['SM_RockCluster_Detail'])
# Reference-shaped planting: strong rear/left clusters, low foreground tufts,
# and small accents between the stone slabs. Keep the right approach clear.
rng=random.Random(12945);plants=[]
def prop_clear(px,py):
    if not in_area(px,py):return False
    p=ref.world(px,py,564);origin=ref.world(132,351,568)
    x,y=(p[0]-origin[0])/.87,(p[1]-origin[1])/.87
    if -116<x<116 and -114<y<102:return False
    if 108<x<196 and -64<y<94:return False
    if -65<x<65 and -157<y<-90:return False
    return True
groups=[(105,331,5,4),(116,313,7,6),(143,313,7,5),(165,329,5,3),
        (107,363,5,4),(123,373,4,2),(145,376,4,1),(167,350,4,2)]
for cx,cy,radius,bushes in groups:
    for i in range(15):
        px=cx+rng.uniform(-radius,radius);py=cy+rng.uniform(-radius*.55,radius*.55)
        if not prop_clear(px,py):continue
        if min(ref.distance_segment((px,py),a,b) for a,b in zip(path,path[1:]))<6:continue
        name=cover[0 if i<bushes else 1 if i<8 else 2]
        scale=rng.uniform(.35,.63) if i<bushes else rng.uniform(.6,1)
        spawn(name,'BlueHouse_Plant_'+str(len(plants)),px,py,564,scale,rng.uniform(0,360),materials[name]);plants.append((name,px,py))
# Low, irregular grass across the exposed lawn; restrained cream flowers only.
for i in range(160):
    px,py=rng.uniform(100,171),rng.uniform(313,377)
    if not prop_clear(px,py):continue
    if 114<px<147 and 324<py<359:continue
    if 149<px<163 and 339<py<355:continue
    if min(ref.distance_segment((px,py),a,b) for a,b in zip(path,path[1:]))<6:continue
    if min(ref.distance_segment((px,py),a,b) for a,b in zip(courtyard_layout.PATHS[0][1],courtyard_layout.PATHS[0][1][1:]))<10:continue
    if any(math.hypot(px-q[1],py-q[2])<2.8 for q in plants):continue
    name=cover[3 if i%29==0 else 2];s=rng.uniform(.50,.85)
    spawn(name,'BlueHouse_Plant_'+str(len(plants)),px,py,564,s,rng.uniform(0,360),materials[name]);plants.append((name,px,py))
assert levels.save_current_level()
(out/'layout.json').write_text(json.dumps({'backup':backup,'region':[99,173,307,378],'removed_old_actors':removed_actors,
 'removed_instanced_dressing':removed,'plants_added':len(plants),'path':path,'shed':'SM_Shed_Context_Reference'},indent=2))
a=None;c=None;world=None;gc.collect()
unreal.log('BLUE_HOUSE_CONTEXT_SAVED')
