"""Reopen the working world and probe the saved stall's actual collision."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level('/Game/Terrarium/Blender/Maps/HomesteadBlender')
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};bindings=[]
for key,label in [('Cottage','Reference_Cottage'),('Lantern','Reference_Lantern'),('Sign','Blender_Sign_Courtyard'),('MarketStall','Blender_MarketStall_UpperPath')]:
    actor=scene[label];mesh=actor.static_mesh_component.static_mesh;base='/Game/Terrarium/Blender/'+key
    assert mesh.get_path_name()==base+'/SM_Blender_'+key+'.SM_Blender_'+key
    assert mesh.get_material(0).get_path_name()==base+'/M_'+key+'.M_'+key and len(mesh.static_materials)==1
    bindings.append({'asset':key,'mesh':mesh.get_path_name(),'material':mesh.get_material(0).get_path_name()})
stall=scene['Blender_MarketStall_UpperPath'];mesh=stall.static_mesh_component.static_mesh
assert mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')==unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
ignored=[a for a in actors.get_all_level_actors() if a!=stall];probes=[]
for name,x,z,expected in [('opening_low',275,600,False),('opening_mid',275,670,False),('left_counter',198,605,True),('right_counter',352,605,True)]:
    hit=unreal.SystemLibrary.line_trace_single(stall,unreal.Vector(x,710,z),unreal.Vector(x,550,z),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignored,unreal.DrawDebugTrace.NONE,ignore_self=False)
    passed=(hit is not None)==expected
    probes.append({'name':name,'hit':hit is not None,'expected_hit':expected,'passed':passed})
    assert passed,(name,str(hit))
levels.pilot_level_actor(scene['Blender_Market_Review']);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
(root/'Docs/BlenderRebuild/MarketStall/saved-world-verification.json').write_text(json.dumps({'world':'/Game/Terrarium/Blender/Maps/HomesteadBlender','bindings':bindings,'collision_probes':probes,'limits':'Point traces verify opening versus counter blocking. Character capsule traversal and full gameplay have not been tested.','fidelity':'not_complete'},indent=2))
