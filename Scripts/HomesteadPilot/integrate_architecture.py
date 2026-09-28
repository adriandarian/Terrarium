"""Fit the new architectural kit into the preserved starting-home layout."""
import unreal,json,math
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadPilot/Maps/StartingHome.' in str(L.get_current_level())
receipt=R/'Docs/HomesteadPilot/architecture-placement.json'
assert not receipt.exists(),'Already placed; use a focused revision instead of rebuilding'
data=json.loads((R/'Docs/HomesteadPilot/Architecture/unreal-import.json').read_text())
meshes={r['name']:unreal.load_asset(r['mesh']) for r in data['meshes']}
assert all(meshes.get(k) for k in ('Cottage','Fence','Bridge'))
scene={a.get_actor_label():a for a in A.get_all_level_actors()}
changes=[]
def vec(v):return [v.x,v.y,v.z]
def place(label,mesh,pos,yaw=0,scale=(1,1,1)):
 a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));a.set_actor_label(label)
 a.set_folder_path('HomesteadPilot/Architecture');a.static_mesh_component.set_static_mesh(mesh)
 a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);a.set_actor_scale3d(unreal.Vector(*scale))
 a.static_mesh_component.set_collision_profile_name('BlockAll')
 changes.append({'actor':label,'mesh':mesh.get_path_name(),'location_cm':pos,'yaw':yaw,'scale':scale})
 return a
house=scene['Reference_Cottage'];old=house.static_mesh_component.static_mesh.get_path_name()
house.static_mesh_component.set_static_mesh(meshes['Cottage']);house.static_mesh_component.set_editor_property('override_materials',[])
house.set_actor_scale3d(unreal.Vector(1,1,1));house.static_mesh_component.set_collision_profile_name('BlockAll')
house.set_folder_path('HomesteadPilot/Architecture')
changes.append({'actor':house.get_actor_label(),'previous_mesh':old,'mesh':meshes['Cottage'].get_path_name(),'location_cm':vec(house.get_actor_location()),'scale':[1,1,1]})
# Preserve the three existing fence runs and their deliberately open entrance.
for run,(first,last) in enumerate(((0,4),(4,8),(9,11))):
 p=scene['AssemblyFence_Post_'+str(first)].get_actor_location();q=scene['AssemblyFence_Post_'+str(last)].get_actor_location()
 dx,dy=q.x-p.x,q.y-p.y;length=math.hypot(dx,dy);n=math.ceil(length/300);span=length/n
 for i in range(n):
  t=(i+.5)/n
  place('HP_Fence_%s_%s'%(run,i),meshes['Fence'],(p.x+dx*t,p.y+dy*t,560),math.degrees(math.atan2(dy,dx)),(span/300,1,1))
for label,a in scene.items():
 if label.startswith('AssemblyFence_'):A.destroy_actor(a)
# Two standard spans form the existing crossing; no end rails block walking.
old_bridge=scene['Fidelity_PlankBridge_v4_001'];center=old_bridge.get_actor_location();yaw=old_bridge.get_actor_rotation().yaw
t=math.radians(yaw);ux,uy=math.cos(t),math.sin(t);vx,vy=-math.sin(t),math.cos(t)
for i,offset in enumerate((-180,180)):
 place('HP_Bridge_'+str(i),meshes['Bridge'],(center.x+vx*offset,center.y+vy*offset,248),yaw)
A.destroy_actor(old_bridge)
# Dedicated piles carry the raised deck to the river bed, rather than hanging in space.
cube=unreal.load_asset('/Engine/BasicShapes/Cube');wood=unreal.load_asset('/Game/Terrarium/HomesteadPilot/Architecture/Materials/M_HP_Wood')
for j,along in enumerate((-335,0,335)):
 for side in (-1,1):
  x=center.x+vx*along+ux*side*94;y=center.y+vy*along+uy*side*94
  pile=place('HP_BridgePile_%s_%s'%(j,side),cube,(x,y,108),yaw,(.16,.16,3.2));pile.static_mesh_component.set_material(0,wood)
assert L.save_current_level()
receipt.write_text(json.dumps({'changes':changes,'cottage_floor_cm':584,'bridge_deck_cm':280,'baseline_assets_modified':False,'status':'Placed; traversal and visual verification follow'},indent=2))
