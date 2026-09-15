"""Seat Ember on verified empty counter space without altering the stall."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/Ember';world='/Game/Terrarium/Blender/Maps/HomesteadBlender'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert world+'.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
label='Blender_Ember_MarketCounter'
materials=json.loads((out/'material-bindings.json').read_text())['slots']
counter=scene['Blender_MarketStall_UpperPath'].static_mesh_component
y=626.3;scale=.145
support=json.loads((out/'base-support-source.json').read_text())['samples']
# Flame-base centers must avoid the narrow seams between counter planks. Test nearby
# positions read-only before moving the actor; preserve the closest supported one.
probes=[]
for shift in [0,.25,-.25,.5,-.5,.75,-.75,1,-1,1.25,-1.25,1.5,-1.5,2,-2]:
    x=337.5+shift;candidate=[]
    for sample in support:
        sx,sy,_=sample['center_m'];(xmin,xmax),(ymin,ymax)=sample['xy_extents_m']
        points=[('center',sx,sy)]+[(f'corner_{i}_{j}',px,py) for i,px in enumerate([xmin+.005,xmax-.005]) for j,py in enumerate([ymin+.005,ymax-.005])]
        for kind,px,py in points:
            dx=px*100*scale;dy=-py*100*scale
            hit=counter.line_trace_component(unreal.Vector(x+dx,y+dy,670),unreal.Vector(x+dx,y+dy,630),True,False,False)
            if not hit or abs(hit[0].z-634.9919962882996)>.005:break
            candidate.append({'xy':[x+dx,y+dy],'z':hit[0].z,'source_part':sample['part'],'sample_kind':kind,'local_underside_m':sample['bottom_m']})
        else:continue
        break
    if len(candidate)==len(support)*5:probes=candidate;break
assert probes,'No fully supported flame-base sample set near the intended position'
heights=[p['z'] for p in probes];assert max(heights)-min(heights)<.08,probes
mesh=unreal.load_asset('/Game/Terrarium/Blender/Ember/SM_Blender_Ember');assert mesh
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
base=mesh.get_bounding_box().min.z*scale;z=max(heights)-base+.02
ob=scene.get(label)
if ob:assert ob.static_mesh_component.static_mesh==mesh
else:ob=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z));ob.set_actor_label(label)
ob.set_actor_location(unreal.Vector(x,y,z),False,False)
c=ob.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[])
ob.set_actor_scale3d(unreal.Vector(scale,scale,scale));ob.set_actor_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0),False)
c.set_collision_profile_name('BlockAll')
assert levels.save_current_level()
record={'world':world,'actor':label,'mesh':mesh.get_path_name(),'location_cm':[x,y,z],'scale':scale,'yaw':0,'height_cm':(mesh.get_bounding_box().max.z-mesh.get_bounding_box().min.z)*scale,'materials':[r['material'] for r in materials],'camera':'Blender_Ember_Review','support_actor':'Blender_MarketStall_UpperPath','support_probes':probes,'base_clearance_cm':.02,'status':'placed_pending_reload_and_native_visual_check'}
(out/'world-placement.json').write_text(json.dumps(record,indent=2))

