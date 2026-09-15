"""Match the reference's fuller object proportions and keep ground approaches clear."""
import unreal,sys,math,gc,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.eject_pilot_level_actor();camera=None;review=None;baseline=None;world=None;a=None;gc.collect()
if '/HomesteadFidelity.' not in str(levels.get_current_level()):assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
sizes={'SM_Assembly_Cottage_v2':(1.26,1.26,1.26),'SM_Assembly_BlueShed_v2':(1,1,1),
 'SM_Assembly_Tower':(1.08,1.08,1.22),'SM_Assembly_Lantern':(1.4,1.4,1.4),'SM_Assembly_VegetableBed':(1.1,1.1,1.1)}
centers={}
for a in actors.get_all_level_actors():
    if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh:
        n=a.static_mesh_component.static_mesh.get_name()
        if n in sizes:
            a.set_actor_scale3d(unreal.Vector(*sizes[n]));p=a.get_actor_location();centers[n]=(p.x,p.y)
def occupied(p):
    if abs(p.z-564)>20:return False
    for name,(ox,oy) in centers.items():
        dx,dy=p.x-ox,p.y-oy;s=sizes[name][0]
        if name=='SM_Assembly_Cottage_v2':
            x,y=dy/s,-dx/s
            if abs(x)<151 and abs(y)<169:return True
            if abs(x)<86 and -295<y<-169:return True
            if 53<x<150 and -230<y<-153:return True
        elif name=='SM_Assembly_BlueShed_v2':
            x,y=dx/s,dy/s
            if abs(x)<115 and -114<y<102:return True
            if 108<x<196 and -64<y<94:return True
        elif name=='SM_Assembly_VegetableBed':
            if abs(dx/s)<142 and abs(dy/s)<120:return True
    return False
cover=('SM_Bush_v2_Detail','SM_MeadowGrass_v2_Detail','SM_GroundPlants_v2_Detail','SM_MeadowFlowers_v2_Detail')
removed=0;jobs=[]
for a in list(actors.get_all_level_actors()):
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if not c.static_mesh or c.static_mesh.get_name() not in cover:continue
        if isinstance(c,unreal.FoliageInstancedStaticMeshComponent):
            keep=[]
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,world_space=True)
                if occupied(t.translation):removed+=1
                else:keep.append(t)
            jobs.append((c.static_mesh.get_name(),keep))
        elif occupied(a.get_actor_location()):actors.destroy_actor(a);removed+=1
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for name,ts in jobs:
    ft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+name[3:])
    unreal.InstancedFoliageActor.remove_all_instances(world,ft);unreal.InstancedFoliageActor.add_instances(world,ft,ts)
world=None
# Shift the cottage-side passage outward with its enlarged footing.
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label().startswith(('CourtyardPath_garden_passage','AssemblyPath_')):actors.destroy_actor(a)
from paths_v7 import sample_track
path=[(207,346),(230,359),(253,361),(282,348),(311,332),(333,319)]
mat=None
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name()=='SM_PathTile_v4_Detail':mat=c.get_material(0)
for i,(center,yaw,length) in enumerate(sample_track([ref.world(*p,560) for p in path],spacing=90)):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*center,571))
    a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/SM_PathTile_v4_Detail'));a.static_mesh_component.set_material(0,mat)
    a.set_actor_scale3d(unreal.Vector(length/188,76/200,.65));a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    a.set_actor_label('AssemblyPath_'+str(i));a.set_folder_path('HomesteadFidelity/AssemblyGround')
assert levels.save_current_level()
(root/'Docs/HomesteadAssembly/proportions.json').write_text(json.dumps({'scales':sizes,'passage':path,'plants_cleared_from_footprints':removed},indent=2))
a=None;c=None;world=None;gc.collect();unreal.log('ASSEMBLY_PROPORTIONS_AND_GROUND_FITTED')
