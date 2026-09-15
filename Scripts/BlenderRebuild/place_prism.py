"""Seat the flat lower crystal tip on empty space on the market counter."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/TrailPrism';world='/Game/Terrarium/Blender/Maps/HomesteadBlender'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert world+'.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};label='Blender_TrailPrism_MarketCounter'
counter=scene['Blender_MarketStall_UpperPath'].static_mesh_component
x=307.;y=623.;scale=.19;probes=[]
# The bottom is a 3.85 cm square in the full-sized source: 0.7315 cm here.
for dx in [-.34,0,.34]:
    for dy in [-.34,0,.34]:
        hit=counter.line_trace_component(unreal.Vector(x+dx,y+dy,670),unreal.Vector(x+dx,y+dy,630),True,False,False)
        assert hit,('Unsupported prism tip',dx,dy)
        probes.append({'xy':[x+dx,y+dy],'z':hit[0].z})
heights=[p['z'] for p in probes];assert max(heights)-min(heights)<.08
mesh=unreal.load_asset('/Game/Terrarium/Blender/TrailPrism/SM_Blender_TrailPrism');assert mesh
z=max(heights)-mesh.get_bounding_box().min.z*scale+.02
ob=scene.get(label)
if ob:assert ob.static_mesh_component.static_mesh==mesh
else:ob=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z));ob.set_actor_label(label)
ob.set_actor_location(unreal.Vector(x,y,z),False,False)
ob.set_actor_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0),False);ob.set_actor_scale3d(unreal.Vector(scale,scale,scale))
c=ob.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll')
assert levels.save_current_level()
materials=json.loads((out/'material-bindings.json').read_text())['slots']
(out/'world-placement.json').write_text(json.dumps({'world':world,'actor':label,'mesh':mesh.get_path_name(),'location_cm':[x,y,z],'scale':scale,'yaw':0,'height_cm':112*scale,'materials':[s['material'] for s in materials],'camera':'Blender_TrailPrism_Review','support_actor':'Blender_MarketStall_UpperPath','support_probes':probes,'base_clearance_cm':.02,'status':'placed_pending_reload_and_native_visual_check','limits':'Static display on a small flat tip; rigid-body balance and gameplay pickup are untested.'},indent=2))
