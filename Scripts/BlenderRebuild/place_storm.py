"""Place the Blender lightning display in the verified right counter interval."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/Storm';world='/Game/Terrarium/Blender/Maps/HomesteadBlender'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert world+'.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};counter=scene['Blender_MarketStall_UpperPath'].static_mesh_component
x,y,scale,yaw=397.,626.,.11,-90.
mesh=unreal.load_asset('/Game/Terrarium/Blender/Storm/SM_Blender_Storm');assert mesh
source=json.loads((out/'base-support-source.json').read_text());samples=source['samples_m'];assert len(samples)>=2
points=samples+[[sum(p[i] for p in samples)/len(samples) for i in range(3)]]
probes=[]
for p in points:
    # Blender Y flips on FBX import; yaw -90 maps (X,Y) to (-Y,-X).
    px=x-p[1]*100*scale;py=y-p[0]*100*scale
    hit=counter.line_trace_component(unreal.Vector(px,py,670),unreal.Vector(px,py,630),True,False,False)
    assert hit and abs(hit[0].z-634.9919962882996)<.005
    probes.append({'xy':[px,py],'counter_z':hit[0].z,'local_z_m':p[2]})
z=max(p['counter_z'] for p in probes)-source['minimum_z_m']*100*scale+.02
label='Blender_Storm_MarketCounter';actor=scene.get(label)
if actor:assert actor.static_mesh_component.static_mesh==mesh
else:actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z));actor.set_actor_label(label)
actor.set_actor_location(unreal.Vector(x,y,z),False,False);actor.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);actor.set_actor_scale3d(unreal.Vector(scale,scale,scale))
c=actor.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll')
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh) and levels.save_current_level()
b=mesh.get_bounding_box();center,extent=actor.get_actor_bounds(False)
# The full display fits between Grove and the end of the counter in plan view.
assert center.x-extent.x>388 and center.x+extent.x<407
assert center.y-extent.y>622.7 and center.y+extent.y<627.8
(out/'world-placement.json').write_text(json.dumps({'world':world,'actor':label,'mesh':mesh.get_path_name(),'location_cm':[x,y,z],'scale':scale,'yaw':yaw,'height_cm':(b.max.z-b.min.z)*scale,'materials':[s['material'] for s in json.loads((out/'material-bindings.json').read_text())['slots']],'support_actor':'Blender_MarketStall_UpperPath','support_probes':probes,'base_clearance_cm':.02,'bounds_center_cm':[center.x,center.y,center.z],'bounds_extent_cm':[extent.x,extent.y,extent.z],'status':'placed_pending_saved_reload_and_visual_review','limits':'Static display on a narrow tip. The concept includes floating sparks; cloud attachment, rigid-body stability and gameplay are not certified.'},indent=2))
