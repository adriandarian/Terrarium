"""Read-only sampled tree-ground contact and simple trunk-query evidence.

Terrain queries ignore foliage so the tree itself cannot count as its own ground.
Trunk rays are Visibility queries, not movement or capsule traversal acceptance.
"""
import json
import math
from collections import defaultdict
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/WorldExpansion'
source = json.loads((ROOT / 'SourceAssets/WorldExpansion/Terrain/manifest.json').read_text())
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
play_world = editor.get_game_world()
world = play_world or editor.get_editor_world()
assert '/Game/Terrarium/WorldExpansion/Maps/' in world.get_path_name()
assert world.get_path_name().split('.')[0].endswith('ValleyRegion')
actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if play_world else unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
foliage = [a for a in actors if isinstance(a, unreal.InstancedFoliageActor)]
private_tree_path = '/Game/Terrarium/WorldExpansion/Forest/SM_WX_BroadTree5m.SM_WX_BroadTree5m'
tree_path = private_tree_path if unreal.load_asset(private_tree_path) else '/Game/Terrarium/HomesteadPilot/Landscape/Meshes/SM_BroadTree5m.SM_BroadTree5m'
cells = defaultdict(list)
for actor in foliage:
    for comp in actor.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        mesh = comp.get_editor_property('static_mesh')
        if not mesh or mesh.get_path_name() != tree_path:
            continue
        for i in range(comp.get_instance_count()):
            transform = comp.get_instance_transform(i, world_space=True)
            p = transform.translation
            cells[(math.floor(p.x / 100), math.floor(p.y / 100))].append((comp, i, transform))


def xyz(p):
    return [p.x, p.y, p.z]


def trace(start, end, complex_trace, ignored):
    result = unreal.SystemLibrary.line_trace_single(world_context_object=world,
        start=unreal.Vector(*start), end=unreal.Vector(*end),
        trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, trace_complex=complex_trace,
        actors_to_ignore=ignored, draw_debug_type=unreal.DrawDebugTrace.NONE, ignore_self=False)
    hit = result if isinstance(result, unreal.HitResult) else next(
        (v for v in (result or []) if isinstance(v, unreal.HitResult)), None)
    if hit is None:
        return {'blocking_hit': False}
    values = hit.to_tuple()
    return {'blocking_hit': bool(values[0]), 'impact_point_cm': xyz(values[5]),
            'impact_normal': xyz(values[7]), 'actor': values[9].get_actor_label() if values[9] else None,
            'component': values[10].get_path_name() if values[10] else None,
            'instance_index': int(values[13])}


forest = source['forest_instances']
indices = sorted(set(round(i * (len(forest) - 1) / 11) for i in range(12))) if forest else []
rows, errors, warnings = [], [], []
for index in indices:
    planned = forest[index]
    x, y, expected_z = [v * 100 for v in planned['location_m']]
    cx, cy = math.floor(x / 100), math.floor(y / 100)
    candidates = [entry for ox in (-1, 0, 1) for oy in (-1, 0, 1) for entry in cells.get((cx + ox, cy + oy), [])
                  if math.hypot(entry[2].translation.x - x, entry[2].translation.y - y) < 2]
    row = {'source_index': index, 'planned_ground_cm': [x, y, expected_z], 'matched_instances': len(candidates), 'ground_traces': []}
    if len(candidates) != 1:
        errors.append('Tree instance match is not unique at source index ' + str(index))
        rows.append(row)
        continue
    comp, instance_index, transform = candidates[0]
    mesh = comp.get_editor_property('static_mesh')
    visual_bottom = transform.translation.z + mesh.get_bounding_box().min.z * transform.scale3d.z
    row.update(component=comp.get_path_name(), instance_index=instance_index,
               visual_bottom_z_cm=visual_bottom,
               pawn_response=str(comp.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)),
               collision_enabled=str(comp.get_collision_enabled()))
    for complex_trace in (False, True):
        hit = trace([x, y, expected_z + 500], [x, y, expected_z - 500], complex_trace, foliage)
        hit['trace_complex'] = complex_trace
        hit['root_to_terrain_cm'] = visual_bottom - hit['impact_point_cm'][2] if hit['blocking_hit'] else None
        hit['within_30cm_contact_tolerance'] = bool(hit['blocking_hit'] and abs(hit['root_to_terrain_cm']) <= 30)
        if not hit['within_30cm_contact_tolerance']:
            warnings.append('Root contact requires review at source index ' + str(index) + ', complex=' + str(complex_trace))
        row['ground_traces'].append(hit)
    trunk = trace([x - 80, y, visual_bottom + 100], [x + 80, y, visual_bottom + 100], False, [])
    trunk['matched_tree_instance'] = bool(trunk['blocking_hit'] and trunk.get('component') == comp.get_path_name()
                                          and trunk.get('instance_index') == instance_index)
    if not trunk['matched_tree_instance']:
        warnings.append('Simple trunk ray did not identify expected tree at source index ' + str(index))
    row['simple_trunk_ray'] = trunk
    rows.append(row)
report = {'world': world.get_path_name(), 'playing': bool(play_world), 'sampled_trees': len(rows), 'rows': rows,
          'errors': errors, 'warnings': warnings,
          'instance_matches_passed': bool(rows) and not errors,
          'all_sampled_ground_contacts_within_30cm': bool(rows) and all(len(r['ground_traces']) == 2 and all(h['within_30cm_contact_tolerance'] for h in r['ground_traces']) for r in rows),
          'all_sampled_simple_trunk_rays_hit_expected_instance': bool(rows) and all(r.get('simple_trunk_ray', {}).get('matched_tree_instance', False) for r in rows),
          'scope': 'Twelve deterministic tree samples distributed through the forest manifest. Terrain queries ignore all foliage. Separate simple Visibility rays cross the trunk at one metre above visual mesh bounds bottom.',
          'limits': 'Root bounds and sampled terrain heights do not prove complete slope contact. Trunk rays do not prove capsule traversal or complete branch/canopy collision. No actors, transforms, meshes, or saves are changed.'}
(OUT / ('forest-contact-play.json' if play_world else 'forest-contact-validation.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('WorldExpansion forest contact evidence written; warnings=' + str(len(warnings)))
