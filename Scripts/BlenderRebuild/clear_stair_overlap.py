"""Lower only the four existing terrain instances that cover the upper stair treads."""
import unreal, json
from pathlib import Path
root = Path(unreal.Paths.project_dir()).resolve()
assert root == Path('C:/Users/hello/Projects/Terrarium')
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Game/Terrarium/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
receipt = root / 'Docs/BlenderRebuild/StoneStairs/terrain-adjustment.json'
assert not receipt.exists(), 'Already adjusted; inspect the saved receipt before making further changes'
actor = next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label() == 'Fidelity_StaticInstances')
plans = []
for c in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
    if not c.static_mesh or c.static_mesh.get_name() not in ['SM_Env_MeadowTile', 'SM_Env_Cliff_A_R2']:
        continue
    expected_z = 560 if c.static_mesh.get_name() == 'SM_Env_MeadowTile' else 270
    for i in range(c.get_instance_count()):
        t = c.get_instance_transform(i, world_space=True)
        p = t.translation
        if min(abs(p.x - 780), abs(p.x - 852)) < .01 and abs(p.y + 224) < .01 and abs(p.z - expected_z) < .01:
            q = t.rotation
            plans.append((c, i, t, {'component': c.get_name(), 'mesh': c.static_mesh.get_path_name(), 'index': i, 'component_count': c.get_instance_count(), 'before_cm': [p.x, p.y, p.z], 'after_cm': [p.x, p.y, p.z - 280], 'scale': [t.scale3d.x, t.scale3d.y, t.scale3d.z], 'rotation_xyzw': [q.x, q.y, q.z, q.w]}))
assert len(plans) == 4
# Record the exact transforms before the first mutation.
data = {'purpose': 'Seat the two overlapping meadow cells and two cliff columns at the lower terrace, exposing all eight stair treads.', 'instances': [p[3] for p in plans], 'status': 'planned'}
receipt.write_text(json.dumps(data, indent=2))
for c, i, t, row in plans:
    t.translation = unreal.Vector(*row['after_cm'])
    assert c.update_instance_transform(i, t, world_space=True, mark_render_state_dirty=True, teleport=True)
assert levels.save_current_level()
data['status'] = 'saved_pending_reload_check'
receipt.write_text(json.dumps(data, indent=2))
unreal.log('BLENDER_STAIR_TERRAIN_CLEARED')
