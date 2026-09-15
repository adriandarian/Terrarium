"""Place the Blender timber threshold at its measured south-joint anchor."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/BridgeThreshold';receipt=folder/'world-placement.json';assert not receipt.exists()
before=json.loads((folder/'site-before.json').read_text());adaptation=json.loads((folder/'source-adaptation.json').read_text());world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()==before['world']
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};bridge=scene[before['bridge_actor']]
p=bridge.get_actor_location();yaw=bridge.get_actor_rotation().yaw
assert all(abs(a-b)<.001 for a,b in zip([p.x,p.y,p.z],before['bridge_location_cm'])) and abs(yaw-before['bridge_yaw'])<.001
assert bridge.static_mesh_component.static_mesh.get_path_name()==before['bridge_mesh']
label='Blender_BridgeThreshold_South';assert label not in scene
mesh=unreal.load_asset('/Game/Terrarium/Blender/BridgeThreshold/SM_Blender_BridgeThreshold');assert mesh
body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
along=-371.;angle=math.radians(yaw);location=unreal.Vector(p.x-along*math.sin(angle),p.y+along*math.cos(angle),280)
a=actors.spawn_actor_from_class(unreal.StaticMeshActor,location);a.set_actor_label(label);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False)
c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll')
assert levels.save_current_level()
receipt.write_text(json.dumps({'asset':'BridgeThreshold','variant_of':'RiverCrossing','actor':label,'mesh':mesh.get_path_name(),'world':world.get_path_name().split('.')[0],'location_cm':[location.x,location.y,location.z],'yaw':yaw,'scale':1,'anchor_along_cm':along,'bank_edge_along_cm':-410,'deck_edge_along_cm':-332,'bank_top_cm':adaptation['bank_top_cm'],'deck_top_cm':adaptation['deck_top_cm'],'status':'placed_pending_saved_collision_contact_and_visual_review'},indent=2))
unreal.log('BLENDER_BRIDGE_THRESHOLD_PLACED')
