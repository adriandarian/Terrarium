"""Small deterministic placement helpers; all geometry is the original reviewed kit."""
import unreal, math, random
from collections import Counter

actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
counts=Counter()
rng=random.Random(1709)
meshes={}

def world(u,v,z=0):
    return unreal.Vector((-u-v)/math.sqrt(2),(-u+v)/math.sqrt(2),z)

def place(mesh,u,v,z=0,scale=1,yaw=0,group='Details'):
    if mesh not in meshes:meshes[mesh]=unreal.load_asset('/Game/Terrarium/Meshes/SM_'+mesh)
    assert meshes[mesh],mesh
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,world(u,v,z))
    counts[mesh]+=1
    a.set_actor_label('Homestead_'+mesh+'_'+str(counts[mesh]).zfill(4))
    a.static_mesh_component.set_static_mesh(meshes[mesh])
    a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    a.set_actor_scale3d(unreal.Vector(*(scale if isinstance(scale,tuple) else (scale,scale,scale))))
    a.set_folder_path('Homestead/'+group)
    return a

def segment(mesh,start,end,z,width=1,group='Paths',unit=200):
    a,b=world(*start),world(*end)
    yaw=math.degrees(math.atan2(b.y-a.y,b.x-a.x))
    length=math.hypot(end[0]-start[0],end[1]-start[1])
    return place(mesh,(start[0]+end[0])/2,(start[1]+end[1])/2,z,(length/unit,width,1),yaw,group)

def distance_to_path(u,v,points):
    best=1e10
    for (x,y),(xx,yy) in zip(points,points[1:]):
        dx,dy=xx-x,yy-y;t=max(0,min(1,((u-x)*dx+(v-y)*dy)/(dx*dx+dy*dy)))
        best=min(best,math.hypot(u-x-t*dx,v-y-t*dy))
    return best
