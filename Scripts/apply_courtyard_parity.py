"""Correct the full courtyard composition, using native editor assets only."""
import unreal,sys,json,math,random,importlib,gc
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/CourtyardParity';out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(root/'Scripts/Fidelity'));sys.path.insert(0,str(root/'Scripts/Assets'))
import reference as ref,courtyard_layout as layout
importlib.reload(layout)
from paths_v7 import sample_track
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.eject_pilot_level_actor()
world=None;camera=None;review=None;baseline=None;actor=None;a=None;c=None;scene=None;capture=None;gc.collect()
working='/Game/Terrarium/Maps/HomesteadFidelity'
backup='/Game/Terrarium/Maps/HomesteadBeforeCourtyardParity'
assert levels.load_level(working)
if not unreal.EditorAssetLibrary.does_asset_exist(backup):
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,backup)
    world=None
assert levels.load_level(backup)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,working)
world=None
assert levels.load_level(working)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
material=unreal.load_asset('/Game/Terrarium/Materials/M_DetailCrafted')
def components():
    return [c for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh]
def mesh_actor(token):
    return next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and token in a.static_mesh_component.static_mesh.get_name())
def spawn(mesh,label,xyz,scale=1,yaw=0,mat=None):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*xyz))
    a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/'+mesh))
    a.static_mesh_component.set_material(0,mat or material)
    a.set_actor_label(label);a.set_folder_path('HomesteadFidelity/CourtyardParity')
    a.set_actor_scale3d(unreal.Vector(*(scale if isinstance(scale,tuple) else (scale,)*3)))
    a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    return a
def ft_for(name):
    ft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+name[3:]);assert ft,name
    return ft
def replace_instances(name,keep):
    source=ft_for(name)
    unreal.InstancedFoliageActor.remove_all_instances(world,source)
    if keep:unreal.InstancedFoliageActor.add_instances(world,source,keep)
def distance_to(p,path):return min(ref.distance_segment(p,a,b) for a,b in zip(path,path[1:]))
shed=mesh_actor('Shed_v2');shed.set_actor_rotation(unreal.Rotator(pitch=0,yaw=layout.SHED_YAW,roll=0),False);shed=None
# Retain every segment of the main trail, stairs approach and river routes.
path_name='SM_PathTile_v4_Detail'
path_component=next(c for c in components() if c.static_mesh.get_name()==path_name)
retained=[];removed=[]
for i in range(path_component.get_instance_count()):
    t=path_component.get_instance_transform(i,world_space=True);p=t.translation
    if abs(p.z-571)<4:
        q=ref.pixel(p.x,p.y,560)
        distances=[distance_to(q,path) for h,path,w in ref.PATHS if h==560]
        if min(range(len(distances)),key=lambda k:distances[k]) in (1,2):
            removed.append((q[0],q[1]));continue
    retained.append(t)
path_material=path_component.get_material(0);path_component=None
replace_instances(path_name,retained)
new_paths=[]
for label,points,width in layout.PATHS:
    for center,yaw,length in sample_track([ref.world(*p,560) for p in points],spacing=90):
        spawn(path_name,'CourtyardPath_'+label+'_'+str(len(new_paths)),(*center,571),
              (length/188,width/200,.65),yaw,path_material)
        new_paths.append((label,*center))
# Replace the well silhouette with the closed lantern tower visible in reference.
tower_path='/Game/Terrarium/Meshes/SM_CourtyardTower_Reference'
if not unreal.EditorAssetLibrary.does_asset_exist(tower_path):
    import courtyard_tower;importlib.reload(courtyard_tower);courtyard_tower.build()
well=mesh_actor('GardenWell');well.static_mesh_component.set_static_mesh(unreal.load_asset(tower_path))
well.set_actor_label('Courtyard_LanternTower');well.static_mesh_component.set_material(0,material)
well.set_actor_location(unreal.Vector(*ref.world(*layout.ANCHORS['tower'],568)),False,False)
well.set_actor_scale3d(unreal.Vector(1,1,1));well=None
for token,key,scale in [('GardenBed_v3','main_bed',.95),('GardenBed_v2','flower_bed',.80)]:
    a=mesh_actor(token);a.set_actor_location(unreal.Vector(*ref.world(*layout.ANCHORS[key],570)),False,False)
    a.set_actor_scale3d(unreal.Vector(scale,scale,scale));a=None
flower_path='/Game/Terrarium/Meshes/SM_CourtyardFlowerBed_Reference'
if not unreal.EditorAssetLibrary.does_asset_exist(flower_path):
    import courtyard_flowers;importlib.reload(courtyard_flowers);courtyard_flowers.build()
a=mesh_actor('GardenBed_v2');a.static_mesh_component.set_static_mesh(unreal.load_asset(flower_path))
a.static_mesh_component.set_material(0,material);a.set_actor_scale3d(unreal.Vector(1,1,1))
a.set_actor_label('Courtyard_FlowerBed');a=None
# The reference fence hugs the two beds; it does not enclose the large bare
# triangle behind the tower. Keep the front approach to the house fully open.
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label().startswith('ReferenceFence_'):actors.destroy_actor(a)
posts={};rails=[]
for run in layout.FENCES:
    for start,end in zip(run,run[1:]):
        v,w=ref.world(*start,568),ref.world(*end,568)
        length=math.hypot(w[0]-v[0],w[1]-v[1]);n=max(1,round(length/175))
        yaw=math.degrees(math.atan2(w[1]-v[1],w[0]-v[0]))
        for i in range(n+1):
            xyz=tuple(v[k]+(w[k]-v[k])*i/n for k in range(3));posts[(round(xyz[0],2),round(xyz[1],2))]=(xyz,yaw)
        for i in range(n):rails.append((tuple(v[k]+(w[k]-v[k])*(i+.5)/n for k in range(3)),yaw,length/n/170))
for i,(xyz,yaw) in enumerate(posts.values()):spawn('SM_FencePost_Reference','ReferenceFence_Post_'+str(i),xyz,(.88,.88,.82+(i%3-1)*.025),yaw)
for i,(xyz,yaw,sx) in enumerate(rails):spawn('SM_FenceRails_Reference','ReferenceFence_Rails_'+str(i),xyz,(sx,1,.82),yaw)
# Clear only ground cover intersecting the corrected circulation and bed feet.
def blocked(px,py):
    if min(distance_to((px,py),path)-width/11 for _,path,width in layout.PATHS)<2:return True
    if abs(px-306)/35+abs(py-373)/25<1.2:return True
    if abs(px-386)/26+abs(py-349)/20<1.15:return True
    if math.hypot(px-351,py-347)<14:return True
    if 211<px<296 and 283<py<330:return True
    if 112<px<153 and 325<py<358:return True
    return False
cover_names=['SM_Bush_v2_Detail','SM_MeadowGrass_v2_Detail','SM_GroundPlants_v2_Detail','SM_MeadowFlowers_v2_Detail']
materials={};cleared={}
for name in cover_names:
    comp=next(c for c in components() if c.static_mesh.get_name()==name)
    materials[name]=comp.get_material(0);keep=[];count=0
    for i in range(comp.get_instance_count()):
        t=comp.get_instance_transform(i,world_space=True);p=t.translation
        px,py=ref.pixel(p.x,p.y,560)
        if abs(p.z-560)<20 and 104<px<440 and 285<py<402 and blocked(px,py):count+=1
        else:keep.append(t)
    comp=None;replace_instances(name,keep);cleared[name]=count
rng=random.Random(12912);planted=[]
for cx,cy,radius in layout.CLUSTERS:
    for i in range(21):
        ang=rng.uniform(0,math.tau);r=radius*math.sqrt(rng.random())
        px=cx+math.cos(ang)*r;py=cy+math.sin(ang)*r*.6
        if blocked(px,py):continue
        name=cover_names[0 if i<4 else 1 if i<12 else 2 if i<18 else 3]
        scale=rng.uniform(.37,.70) if i<4 else rng.uniform(.65,1.15)
        spawn(name,'CourtyardPlant_'+str(len(planted)),ref.world(px,py,564),scale,rng.uniform(0,360),materials[name])
        planted.append((name,px,py,scale))
# Low grass within the yard fills the old exclusion masks without closing routes.
yard=[(114,369),(174,382),(247,396),(322,398),(422,344),(353,313),(295,293),(203,303)]
for i in range(270):
    px,py=rng.uniform(116,421),rng.uniform(305,398)
    if not ref.inside((px,py),yard) or blocked(px,py):continue
    if any(math.hypot(px-q[1],py-q[2])<2.7 for q in planted):continue
    name=cover_names[3 if i%11==0 else 1];scale=rng.uniform(.55,.95)
    spawn(name,'CourtyardPlant_'+str(len(planted)),ref.world(px,py,564),scale,rng.uniform(0,360),materials[name])
    planted.append((name,px,py,scale))
# Stones and weeds frame the narrow passage and shed doorstep in the concept.
rock_mat=next(c.get_material(0) for c in components() if c.static_mesh.get_name()=='SM_RockCluster_Detail')
for i,(px,py,s) in enumerate([(161,342,.48),(307,309,.46),(326,302,.40),(267,335,.26),(338,337,.24)]):
    spawn('SM_RockCluster_Detail','CourtyardStone_'+str(i),ref.world(px,py,564),s,i*73,rock_mat)
assert levels.save_current_level()
(out/'layout.json').write_text(json.dumps({'backup':backup,'paths':layout.PATHS,'fences':layout.FENCES,'anchors':layout.ANCHORS,
 'removed_old_path_instances':len(removed),'preserved_path_instances':len(retained),'new_path_instances':len(new_paths),
 'fence_posts':len(posts),'rail_sections':len(rails),'plants_added':len(planted),'plants_cleared_from_routes':cleared},indent=2))
world=None;a=None;c=None;gc.collect()
unreal.log('COURTYARD_PARITY_APPLIED')
# Keep the accepted blue-house vignette when rebuilding the broader courtyard.
exec(compile((root/'Scripts/dress_blue_house.py').read_text(),str(root/'Scripts/dress_blue_house.py'),'exec'),globals())
