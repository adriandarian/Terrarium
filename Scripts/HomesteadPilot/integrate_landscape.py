"""Integrate the finer landscape kit without editing shared baseline assets."""
import unreal,json,math
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadPilot/Maps/StartingHome.' in str(L.get_current_level())
out=R/'Docs/HomesteadPilot/landscape-placement.json';assert not out.exists()
data=json.loads((R/'Docs/HomesteadPilot/Landscape/unreal-import.json').read_text())
meshes={r['name']:unreal.load_asset(r['mesh']) for r in data['meshes']}
changes=[]
def vec(v):return [v.x,v.y,v.z]
def spawn(label,key,p,yaw=0,scale=(1,1,1)):
 a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*p));a.set_actor_label(label);a.set_folder_path('HomesteadPilot/Landscape')
 a.static_mesh_component.set_static_mesh(meshes[key]);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);a.set_actor_scale3d(unreal.Vector(*scale))
 a.static_mesh_component.set_collision_profile_name('NoCollision' if key in ('ShrubGroundcover','WheatPatch2m','GardenPatch2m') else 'BlockAll')
 changes.append({'actor':label,'mesh':key,'location_cm':p,'scale':scale});return a
for a in list(A.get_all_level_actors()):
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  old=c.static_mesh
  if not old:continue
  path=old.get_path_name();key=None
  if '/HomesteadTree/' in path or 'SM_VoxelTree.' in path:key='BroadTree5m'
  elif '/CliffColumn/' in path:key='FineCliffColumn1m'
  elif '/MeadowShrub/' in path:key='ShrubGroundcover'
  elif '/WheatPatch/' in path:key='WheatPatch2m'
  if not key:continue
  new=meshes[key];ob=old.get_bounding_box();nb=new.get_bounding_box();os=ob.max-ob.min;ns=nb.max-nb.min
  is_tree=key=='BroadTree5m'
  # Preserve cliff envelopes and shrub/crop footprints. Trees deliberately gain
  # broad crowns at coherent 4-6m height; ground contacts remain fixed.
  if isinstance(c,unreal.InstancedStaticMeshComponent):
   count=c.get_instance_count();transforms=[c.get_instance_transform(i,world_space=True) for i in range(count)]
   c.set_static_mesh(new);c.set_editor_property('override_materials',[])
   for i,t in enumerate(transforms):
    bottom=t.translation.z+ob.min.z*t.scale3d.z
    if is_tree:
     zscale=min(1.25,max(.85,t.scale3d.z));t.scale3d=unreal.Vector(zscale,zscale,zscale)
    else:t.scale3d=unreal.Vector(t.scale3d.x*os.x/ns.x,t.scale3d.y*os.y/ns.y,t.scale3d.z*os.z/ns.z)
    p=t.translation;p.z=bottom-nb.min.z*t.scale3d.z;t.translation=p
    assert c.update_instance_transform(i,t,True,True,True)
  else:
   count=1;t=a.get_actor_transform();bottom=t.translation.z+ob.min.z*t.scale3d.z
   c.set_static_mesh(new);c.set_editor_property('override_materials',[])
   scale=unreal.Vector(1,1,1) if is_tree else unreal.Vector(t.scale3d.x*os.x/ns.x,t.scale3d.y*os.y/ns.y,t.scale3d.z*os.z/ns.z)
   a.set_actor_scale3d(scale);p=a.get_actor_location();p.z=bottom-nb.min.z*scale.z;a.set_actor_location(p,False,False)
  c.set_collision_profile_name('NoCollision' if key in ('ShrubGroundcover','WheatPatch2m') else 'BlockAll')
  changes.append({'actor':a.get_actor_label(),'component':c.get_path_name(),'old_mesh':path,'mesh':new.get_path_name(),'instances':count})
# Fit a twelve-tread flight to the existing 2.8m level change. Keep the upper
# endpoint; extend its lower approach rather than making the treads too short.
scene={a.get_actor_label():a for a in A.get_all_level_actors()}
old=scene['Fidelity_StoneStairs_v3_001'];p=old.get_actor_location();yaw=old.get_actor_rotation().yaw
# Blender +Y ascends; FBX flips Y, so local -Y is the upper end in Unreal.
t=math.radians(yaw);dirx,diry=math.sin(t),-math.cos(t)
topx=p.x+dirx*126;topy=p.y+diry*126
mesh=meshes['StoneStairs2mRise'];b=mesh.get_bounding_box();sz=b.max-b.min
zscale=280/sz.z
spawn('HP_TerraceStairs','StoneStairs2mRise',(topx-dirx*180,topy-diry*180,280),yaw,(1.25,1,zscale))
A.destroy_actor(old)
# Garden at the existing cultivated bed, keeping the surrounding clear path.
garden=next((a for a in A.get_all_level_actors() if any(c.static_mesh and 'SM_Env_VegetableBed.' in c.static_mesh.get_path_name() for c in a.get_components_by_class(unreal.StaticMeshComponent))),None)
if garden:
 p=garden.get_actor_location();rot=garden.get_actor_rotation()
 spawn('HP_KitchenGarden','GardenPatch2m',(p.x,p.y,560),rot.yaw,(1.15,1.15,1));A.destroy_actor(garden)
# Small landing uses the new surface sample while maintaining the established path.
spawn('HP_EntryLanding','WornPath2m',(170,53,556),0,(1,1,.5))
# One full-size cap demonstrates the reusable large terrace module, embedded
# into the upper shelf rather than rescaling a 4m module into a narrow column.
spawn('HP_UpperTerraceModule','MossCliff4m',(-1350,850,678.6),0)
assert L.save_current_level()
out.write_text(json.dumps({'changes':changes,'stair_riser_cm':280/12,'stair_tread_cm':30,'baseline_assets_modified':False,'status':'Placed; saved reload and traversal must verify component persistence'},indent=2))
