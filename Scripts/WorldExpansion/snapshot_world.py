"""Read-only snapshot; execute on pristine copy, admitted world, and reopened world.

snapshot-request.json: {"name":"original-baseline" | "admitted" | "reopened"}.
Original per-instance signatures must remain as a multiset subset; new placements
may reuse approved meshes or append instances inside an inherited foliage actor.
"""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/WorldExpansion'
REQUEST = OUT / 'snapshot-request.json'
name = json.loads(REQUEST.read_text())['name'] if REQUEST.exists() else 'original-baseline'
assert name in ('original-baseline', 'admitted', 'reopened')
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world()
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] in (
    '/Game/Terrarium/HomesteadPilot/Maps/StartingHome',
    '/Game/Terrarium/WorldExpansion/Maps/ValleyRegion')
destination = OUT / (name + '.json')
assert name != 'original-baseline' or not destination.exists(), 'Baseline exists; do not overwrite preservation evidence'
signatures, mesh_transforms, components, cameras = Counter(), defaultdict(list), [], []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if isinstance(actor, unreal.CameraActor):
        cameras.append({'actor': actor.get_actor_label(), 'auto_activate_player_index': actor.get_auto_activate_player_index()})
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = comp.get_editor_property('static_mesh')
        if not mesh:
            continue
        transforms = [comp.get_instance_transform(i, world_space=True) for i in range(comp.get_instance_count())] if isinstance(comp, unreal.InstancedStaticMeshComponent) else [comp.get_world_transform()]
        material_paths = [comp.get_material(i).get_path_name() if comp.get_material(i) else None for i in range(comp.get_num_materials())]
        properties = {'mesh': mesh.get_path_name(), 'visible': bool(comp.get_editor_property('visible')),
            'hidden_in_game': bool(comp.get_editor_property('hidden_in_game')),
            'forced_lod': int(comp.get_editor_property('forced_lod_model')),
            'collision_enabled': str(comp.get_collision_enabled()),
            'collision_profile': str(comp.get_collision_profile_name()), 'materials': material_paths}
        values = []
        for transform in transforms:
            p, s, q = transform.translation, transform.scale3d, transform.rotation
            data = [round(v, 5) for v in (p.x, p.y, p.z, s.x, s.y, s.z, q.x, q.y, q.z, q.w)]
            signature = hashlib.sha256(json.dumps([properties, data], sort_keys=True).encode()).hexdigest()
            signatures[signature] += 1
            values.append(data)
        mesh_transforms[mesh.get_path_name()].extend(values)
        components.append(dict(properties, actor=actor.get_actor_label(), instances=len(values)))
components.sort(key=lambda r: (r['actor'], r['mesh'], json.dumps(r, sort_keys=True)))
mesh_summary = {path: {'instances': len(values), 'transform_sha256': hashlib.sha256(json.dumps(sorted(values)).encode()).hexdigest()}
                for path, values in sorted(mesh_transforms.items())}
protected = {}
for relative in ('Content/Terrarium/HomesteadPilot/Maps/StartingHome.umap',
                 'Content/Terrarium/Blender/Maps/HomesteadBlender.umap'):
    file = ROOT / relative
    protected[relative] = hashlib.sha256(file.read_bytes()).hexdigest()
report = {'world': world.get_path_name(), 'instances': sum(signatures.values()),
    'instance_signatures': dict(sorted(signatures.items())), 'meshes': mesh_summary,
    'components': components, 'protected_map_sha256': protected,
    'cameras': sorted(cameras, key=lambda r: r['actor']), 'errors': [],
    'scope': 'Rendered mesh placements rounded to 0.00001 cm, mesh assignments, visibility, component collision modes, forced LODs and effective material assignments. Protected source map bytes are hashed.',
    'limits': 'Does not hash every source asset or prove render parity, character traversal, or performance.'}
if name != 'original-baseline':
    baseline = json.loads((OUT / 'original-baseline.json').read_text())
    missing = Counter(baseline['instance_signatures']) - signatures
    report['original_instances_missing_or_modified'] = sum(missing.values())
    report['original_instances_preserved'] = not missing
    report['protected_maps_unchanged'] = protected == baseline['protected_map_sha256']
    if missing:
        report['errors'].append('Original placements or component properties changed')
    if not report['protected_maps_unchanged']:
        report['errors'].append('Protected map file bytes changed')
if name == 'reopened':
    admitted = json.loads((OUT / 'admitted.json').read_text())
    report['all_instance_signatures_survive_reopen'] = report['instance_signatures'] == admitted['instance_signatures']
    report['component_assignments_survive_reopen'] = report['components'] == admitted['components']
    report['camera_settings_survive_reopen'] = report['cameras'] == admitted['cameras']
    for key in ('all_instance_signatures_survive_reopen', 'component_assignments_survive_reopen', 'camera_settings_survive_reopen'):
        if not report[key]:
            report['errors'].append(key)
    report['review_cameras_do_not_override_player'] = all(r['auto_activate_player_index'] == -1 for r in cameras)
    if not report['review_cameras_do_not_override_player']:
        report['errors'].append('A review camera may override the player')
report['passed'] = not report['errors']
destination.write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('WorldExpansion snapshot: ' + name + ', passed=' + str(report['passed']))
