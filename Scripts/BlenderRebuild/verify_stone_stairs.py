"""Probe imported tread collision at three points per step, plus the two approach heights."""
import unreal, json, math
from pathlib import Path
root = Path(unreal.Paths.project_dir()).resolve()
assert root == Path('C:/Users/hello/Projects/Terrarium')
folder = root / 'Docs/BlenderRebuild/StoneStairs'
r = json.loads((folder / 'world-placement.json').read_text())
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = actors.get_all_level_actors()
ob = next(a for a in all_actors if a.get_actor_label() == r['actor'])
assert ob.static_mesh_component.static_mesh.get_path_name() == r['mesh']
ignored = [a for a in all_actors if a != ob]
co, si = math.cos(math.radians(2)), math.sin(math.radians(2))
p = r['location_cm']
def point(x, y, z):
    return unreal.Vector(p[0] + x * co - y * si, p[1] + x * si + y * co, z)
def trace(x, y, end, ignore):
    return unreal.SystemLibrary.line_trace_single(ob, point(x, y, 700), point(x, y, end), unreal.TraceTypeQuery.ECC_VISIBILITY, False, ignore, unreal.DrawDebugTrace.NONE, ignore_self=False)
probes = []
for step in range(8):
    y = -110.25 + 31.5 * step
    top = 280 + (step + 1) * 35
    for x in [-85, 0, 85]:
        above, below = trace(x, y, top + .04, ignored), trace(x, y, top - .04, ignored)
        assert above is None and below is not None, (step, x, str(above), str(below))
        probes.append({'step': step + 1, 'x_cm': x, 'top_cm': top, 'tolerance_cm': .04, 'passed': True})
approaches = []
for y, expected in [(-150, 280), (150, 560)]:
    high, low = 700, 0
    hit = trace(0, y, low, [])
    if hit is not None:
        for _ in range(18):
            mid = (high + low) / 2
            if trace(0, y, mid, []) is None:
                high = mid
            else:
                low = mid
    approaches.append({'offset_cm': y, 'expected_terrain_cm': expected, 'collision_height_cm': (high + low) / 2 if hit is not None else None})
adjustment = folder / 'terrain-adjustment.json'
terrain_checks = []
if adjustment.exists():
    data = json.loads(adjustment.read_text())
    terrain = next(a for a in all_actors if a.get_actor_label() == 'Fidelity_StaticInstances')
    components = {c.get_name(): c for c in terrain.get_components_by_class(unreal.InstancedStaticMeshComponent)}
    for row in data['instances']:
        c = components[row.get('replacement_component',row['component'])]
        assert c.static_mesh.get_path_name() == row.get('replacement_mesh',row['mesh']) and c.get_instance_count() == row['component_count']
        t = c.get_instance_transform(row.get('replacement_index',row['index']), world_space=True)
        p = t.translation
        q = t.rotation
        assert all(abs(a - b) < .01 for a, b in zip([p.x, p.y, p.z], row['after_cm']))
        assert all(abs(a - b) < .0001 for a, b in zip([t.scale3d.x, t.scale3d.y, t.scale3d.z], row['scale']))
        assert all(abs(a - b) < .0001 for a, b in zip([q.x, q.y, q.z, q.w], row['rotation_xyzw']))
        terrain_checks.append({'component': row['component'], 'index': row['index'], 'passed': True})
(folder / 'collision-verification.json').write_text(json.dumps({'tread_probes': probes, 'approaches': approaches, 'terrain_transform_checks': terrain_checks, 'limits': 'Static visibility traces. Character traversal, step-up and performance have not been tested.'}, indent=2))
unreal.log('BLENDER_STONE_STAIRS_COLLISION_VERIFIED')
