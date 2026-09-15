"""Mount the crest's solid reverse against the left counter's front planks."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/EmberCrest';world='/Game/Terrarium/Blender/Maps/HomesteadBlender'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert world+'.' in str(levels.get_current_level());scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
counter=scene['Blender_MarketStall_UpperPath'].static_mesh_component;probes=[]
for x in [181,184,187]:
    for z in [596,607,618]:
        h=counter.line_trace_component(unreal.Vector(x,670,z),unreal.Vector(x,600,z),True,False,False);assert h
        probes.append({'xz':[x,z],'y':h[0].y})
ys=[p['y'] for p in probes];assert max(ys)-min(ys)<.01
mesh=unreal.load_asset('/Game/Terrarium/Blender/EmberCrest/SM_Blender_EmberCrest');assert mesh
scale=.24;x=184.;z=592.;y=max(ys)-mesh.get_bounding_box().min.y*scale+.015
label='Blender_EmberCrest_MarketFront';ob=scene.get(label)
if ob:assert ob.static_mesh_component.static_mesh==mesh
else:ob=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z));ob.set_actor_label(label)
ob.set_actor_location(unreal.Vector(x,y,z),False,False);ob.set_actor_scale3d(unreal.Vector(scale,scale,scale));ob.set_actor_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0),False)
c=ob.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll')
assert levels.save_current_level()
materials=json.loads((out/'material-bindings.json').read_text())['slots'];b=mesh.get_bounding_box()
(out/'world-placement.json').write_text(json.dumps({'world':world,'actor':label,'mesh':mesh.get_path_name(),'location_cm':[x,y,z],'scale':scale,'yaw':0,'height_cm':(b.max.z-b.min.z)*scale,'materials':[s['material'] for s in materials],'camera':'Blender_EmberCrest_Review','support_actor':'Blender_MarketStall_UpperPath','wall_samples':probes,'back_clearance_cm':.015,'status':'placed_pending_reload_and_native_view'},indent=2))
