"""Read ground/path collision settings without modifying shared source assets."""
import unreal, json
from pathlib import Path
root = Path(unreal.Paths.project_dir()).resolve()
assert root == Path('C:/Users/hello/Projects/Terrarium')
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Game/Terrarium/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
rows = []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        mesh = c.static_mesh
        if not mesh or not any(k in mesh.get_name() for k in ['PathTile', 'MeadowTile', 'GrassTerrain', 'Cliff']):
            continue
        body = mesh.get_editor_property('body_setup')
        rows.append({'actor': actor.get_actor_label(), 'component': c.get_name(), 'mesh': mesh.get_path_name(), 'instances': c.get_instance_count(), 'collision_enabled': str(c.get_collision_enabled()), 'visibility_response': str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)), 'pawn_response': str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)), 'profile': str(c.get_collision_profile_name()), 'mesh_collision_trace': str(body.get_editor_property('collision_trace_flag')) if body else None})
(root / 'Docs/BlenderRebuild/ground-collision-inspection.json').write_text(json.dumps(rows, indent=2))
unreal.log('BLENDER_GROUND_COLLISION_INSPECTED')
