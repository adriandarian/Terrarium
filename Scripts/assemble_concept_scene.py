"""Fit new model placements to the concept scale, preserving the established terrain."""
import unreal,json,sys,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
out=root/'Docs/SceneAssembly';receipt=out/'changes.json';assert not receipt.exists(),'Already applied; inspect receipt before repeating'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
terrain=[c for a in scene.values() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and 'SM_Blender_GrassTerrain.' in c.static_mesh.get_path_name()]
def vec(v):return [v.x,v.y,v.z]
def state(a):
 r=a.get_actor_rotation();c=a.get_component_by_class(unreal.StaticMeshComponent)
 return {'actor':a.get_actor_label(),'mesh':c.static_mesh.get_path_name() if c and c.static_mesh else None,'location':vec(a.get_actor_location()),'scale':vec(a.get_actor_scale3d()),'rotation':[r.pitch,r.yaw,r.roll]}
def ground(x,y,z):
 hh=[h[0].z for c in terrain if (h:=c.line_trace_component(unreal.Vector(x,y,z+80),unreal.Vector(x,y,z-80),True,False,False))]
 assert hh,('No ground',x,y,z)
 return max(hh)
changes=[]
def place(key,label,px,py,z,height=None,scale=None,yaw=-90,existing=None):
 mesh=unreal.load_asset('/Game/Terrarium/Blender/'+key+'/SM_Blender_'+key);assert mesh
 b=mesh.get_bounding_box();s=scale if scale else height/(b.max.z-b.min.z)
 x,y,_=ref.world(px,py,z)
 foot=min(18,(b.max.x-b.min.x)*s*.22)
 probes=[ground(x+dx,y+dy,z) for dx,dy in [(0,0),(-foot,0),(foot,0),(0,-foot),(0,foot)]]
 p=unreal.Vector(x,y,max(probes)+.05-b.min.z*s)
 a=scene.get(existing or label);before=state(a) if a else None
 if not a:a=actors.spawn_actor_from_class(unreal.StaticMeshActor,p);a.set_actor_label(label)
 c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[])
 a.set_actor_location(p,False,False);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);a.set_actor_scale3d(unreal.Vector(s,s,s))
 a.set_folder_path('SceneAssembly/'+('Characters' if key in ['Player','RangerSela','Kindlehorn','Rillip'] else 'OutlyingHomesteads'))
 changes.append({'reason':'Concept-relative scale and sampled ground support','before':before,'after':state(a),'ground_probes':probes,'height_cm':(b.max.z-b.min.z)*s})
 return a
with unreal.ScopedEditorTransaction('Fit Terrarium models to concept composition'):
 place('Player','Reference_Player',177,394,560,height=160,yaw=135,existing='Reference_Player')
 place('RangerSela','Blender_RangerSela_Courtyard',210,365,560,height=160,yaw=160)
 place('Kindlehorn','Blender_Kindlehorn_Meadow',95,270,560,height=125,yaw=135)
 place('Rillip','Blender_Rillip_RiverShelf',350,476,280,height=80,yaw=100)
 place('HomesteadCompound','Blender_HomesteadCompound_WestClearing',-30,160,560,scale=.90,yaw=-90)
 place('CivicHall','Blender_CivicHall_NorthPath',90,-95,560,scale=.72,yaw=-90,existing='Blender_CivicHall_NorthPath')
 # Keep bridge endpoints and deck elevation; reduce its width to fit the 130 cm trail.
 bridge=scene['Fidelity_PlankBridge_v4_001'];before=state(bridge);s=bridge.get_actor_scale3d();s.x=1.35;bridge.set_actor_scale3d(s)
 changes.append({'reason':'Narrow crossing deck from 309 cm to 193 cm; preserve span, deck and riverbed piles','before':before,'after':state(bridge)})
 # Seat the small courtyard creature on the measured grass instead of the old recessed contact.
 br=scene['Blender_Brambit_Courtyard'];before=state(br);p=br.get_actor_location();b=br.static_mesh_component.static_mesh.get_bounding_box();p.z=ground(p.x,p.y,560)+.04-b.min.z*br.get_actor_scale3d().z;br.set_actor_location(p,False,False)
 changes.append({'reason':'Correct recessed courtyard ground contact','before':before,'after':state(br)})
 # Recover the reference tree-to-house proportions while preserving each root and yaw.
 tree_rows=[]
 for a in scene.values():
  for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
   if not c.static_mesh or 'SM_Blender_HomesteadTree.' not in c.static_mesh.get_path_name():continue
   b=c.static_mesh.get_bounding_box()
   for i in range(c.get_instance_count()):
    t=c.get_instance_transform(i,world_space=True);old=vec(t.scale3d);p=t.translation;bottom=p.z+b.min.z*t.scale3d.z;t.scale3d=t.scale3d*1.4;p.z=bottom-b.min.z*t.scale3d.z;t.translation=p
    assert c.update_instance_transform(i,t,True,True,True)
    tree_rows.append({'index':i,'before_scale':old,'after_scale':vec(t.scale3d),'root':vec(p)})
 changes.append({'reason':'Increase landmark tree height and crown by 40 percent at fixed ground contacts','trees':tree_rows})
 cam=scene['Baseline_Orthographic_Review'];levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([])
 assert levels.save_current_level()
receipt.write_text(json.dumps({'world':'/Game/Terrarium/Blender/Maps/HomesteadBlender','changes':changes,'note':'Source models and material alternatives are preserved. Existing world-specific terrain/bridge/wheat variants remain in use.'},indent=2))
