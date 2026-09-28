"""Read-only Unreal editor inventory and grounding coverage for WorldExpansion.

Coordinator executes this after integration and again after reopening the map.
Docs/WorldExpansion/validation-request.json supplies map, actor_prefixes,
required_labels, expected_counts_by_prefix, ground_probes, and optional output_tag.
Ground probes are Visibility traces; they do not establish character traversal.
"""
import json
import math
from collections import Counter
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/WorldExpansion'
REQUEST = json.loads((OUT / 'validation-request.json').read_text(encoding='utf-8'))
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world(), 'End PIE before editor validation'
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] == REQUEST['map'], world.get_path_name()
prefixes = tuple(REQUEST['actor_prefixes'])
assert prefixes and all(prefixes), 'Explicit expansion actor prefixes are required'
mesh_editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
extra_component_paths = set(REQUEST.get('include_component_paths', []))
integration_path = OUT / 'settlement-integration.json'
integration = json.loads(integration_path.read_text()) if integration_path.exists() else {}
for group in integration.get('instances', []):
    extra_component_paths.update(group.get('components', []))
selected = [a for a in actors if a.get_actor_label().startswith(prefixes) or any(
    c.get_path_name() in extra_component_paths for c in a.get_components_by_class(unreal.StaticMeshComponent))]
errors, warnings, rows, meshes, probes = [], [], [], {}, []


def xyz(v):
    return [v.x, v.y, v.z]


def describe_hit(result):
    hit = result if isinstance(result, unreal.HitResult) else next(
        (v for v in (result or []) if isinstance(v, unreal.HitResult)), None)
    if hit is None:
        return {'blocking_hit': False}
    values = hit.to_tuple()
    return {'blocking_hit': bool(values[0]), 'initial_overlap': bool(values[1]),
            'impact_point_cm': xyz(values[5]), 'impact_normal': xyz(values[7]),
            'actor': values[9].get_actor_label() if values[9] else None,
            'component': values[10].get_path_name() if values[10] else None}


labels = Counter(a.get_actor_label() for a in selected)
for label in REQUEST.get('required_labels', []):
    if labels[label] != 1:
        errors.append('Required actor count is not one: ' + label)
for prefix, count in REQUEST.get('expected_counts_by_prefix', {}).items():
    actual = sum(a.get_actor_label().startswith(prefix) for a in selected)
    if actual != count:
        errors.append(f'Actor count {prefix}: expected {count}, found {actual}')
for label, count in labels.items():
    if count > 1:
        errors.append(f'Duplicate expansion actor label: {label} ({count})')
if not selected:
    errors.append('No expansion actors found')
for actor in selected:
    transform = actor.get_actor_transform()
    rotation = actor.get_actor_rotation()
    row = {'label': actor.get_actor_label(), 'class': actor.get_class().get_path_name(),
           'location_cm': xyz(actor.get_actor_location()),
           'rotation_degrees': [rotation.pitch, rotation.yaw, rotation.roll],
           'scale': xyz(actor.get_actor_scale3d()), 'components': []}
    if not all(math.isfinite(v) for v in row['location_cm'] + row['scale']):
        errors.append('Nonfinite transform: ' + row['label'])
    if any(v <= 0 for v in row['scale']):
        warnings.append('Zero or negative scale: ' + row['label'])
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        if not actor.get_actor_label().startswith(prefixes) and comp.get_path_name() not in extra_component_paths:
            continue
        mesh = comp.get_editor_property('static_mesh')
        if not mesh:
            errors.append('Missing static mesh: ' + comp.get_path_name())
            continue
        path = mesh.get_path_name()
        if path not in meshes:
            body = mesh.get_editor_property('body_setup')
            counts = [mesh.get_num_triangles(i) for i in range(mesh.get_num_lods())]
            meshes[path] = {'triangles_by_lod': counts,
                'screen_sizes': list(mesh_editor.get_lod_screen_sizes(mesh)),
                'simple_collision_primitives': mesh_editor.get_simple_collision_count(mesh),
                'collision_flag': str(body.get_editor_property('collision_trace_flag')) if body else None,
                'collision_lod': int(mesh.get_editor_property('lod_for_collision')),
                'nanite_enabled': mesh_editor.get_nanite_settings(mesh).get_editor_property('enabled')}
            if not counts or any(n <= 0 for n in counts):
                errors.append('Empty LOD geometry: ' + path)
            if len(counts) == 1 and counts[0] > REQUEST.get('single_lod_warning_triangles', 5000):
                warnings.append('Dense single-LOD mesh: ' + path)
            if any(counts[i] > counts[i-1] for i in range(1, len(counts))):
                warnings.append('LOD triangle count increases with distance: ' + path)
        instance_count = comp.get_instance_count() if isinstance(comp, unreal.InstancedStaticMeshComponent) else 1
        forced = int(comp.get_editor_property('forced_lod_model'))
        item = {'component': comp.get_name(), 'mesh': path, 'instances': instance_count,
                'forced_lod_model': forced, 'visible': comp.get_editor_property('visible'),
                'collision_enabled': str(comp.get_collision_enabled()),
                'collision_profile': str(comp.get_collision_profile_name()),
                'pawn_response': str(comp.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)),
                'materials': [str(comp.get_material(i).get_path_name()) if comp.get_material(i) else None
                              for i in range(comp.get_num_materials())]}
        if forced != 0:
            errors.append('Forced LOD is not automatic: ' + comp.get_path_name())
        if any(m is None for m in item['materials']):
            warnings.append('Unassigned material slot: ' + comp.get_path_name())
        row['components'].append(item)
    rows.append(row)

observed_components = {comp.get_path_name(): comp for actor in selected
                       for comp in actor.get_components_by_class(unreal.StaticMeshComponent)}
for group in integration.get('instances', []):
    actual = sum(observed_components[p].get_instance_count() for p in group['components'] if p in observed_components)
    if actual != group['count']:
        errors.append(f"Settlement instance count {group['asset']}: expected {group['count']}, found {actual}")

for probe in REQUEST.get('ground_probes', []):
    x, y, z = probe['ground_cm']
    row = {'name': probe['name'], 'expected_ground_cm': [x, y, z], 'traces': []}
    for complex_trace in [False, True]:
        try:
            hit = unreal.SystemLibrary.line_trace_single(world_context_object=world,
                start=unreal.Vector(x, y, z + probe.get('trace_above_cm', 250)),
                end=unreal.Vector(x, y, z - probe.get('trace_below_cm', 500)),
                trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                trace_complex=complex_trace, actors_to_ignore=[],
                draw_debug_type=unreal.DrawDebugTrace.NONE, ignore_self=False)
            result = describe_hit(hit)
            result['trace_complex'] = complex_trace
            result['height_error_cm'] = abs(result['impact_point_cm'][2] - z) if result['blocking_hit'] else None
            result['passed'] = bool(result['blocking_hit'] and
                result['height_error_cm'] <= probe.get('height_tolerance_cm', 40) and
                result['impact_normal'][2] >= probe.get('minimum_normal_z', 0.7))
        except Exception as exc:
            result = {'trace_complex': complex_trace, 'passed': False, 'error': repr(exc)}
        row['traces'].append(result)
    row['passed'] = all(r['passed'] for r in row['traces'])
    if not row['passed']:
        errors.append('Ground probe failed: ' + probe['name'])
    probes.append(row)

tag = REQUEST.get('output_tag', 'validation')
assert tag and tag.replace('-', '').replace('_', '').isalnum()
report = {'world': world.get_path_name(), 'request': REQUEST,
    'actor_count': len(rows), 'mesh_count': len(meshes),
    'mesh_instances': sum(c['instances'] for r in rows for c in r['components']),
    'actors': rows, 'meshes': meshes, 'ground_probes': probes,
    'errors': errors, 'warnings': warnings, 'passed': not errors,
    'scope': 'Read-only editor object inventory and vertical simple/complex Visibility traces. No assets or transforms changed.',
    'limits': 'Ground samples do not verify CharacterMovement traversal, navigation, held keyboard input, runtime streaming, automatic LOD appearance, or city-scale performance. Mesh triangle counts are shared geometry, not per-instance memory.'}
(OUT / (tag + '.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('WorldExpansion validation written: ' + str(report['passed']))
