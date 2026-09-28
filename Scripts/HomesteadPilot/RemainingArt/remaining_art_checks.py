"""Read-only Unreal validation shared by final verification and safe resume."""
import hashlib, json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
DOC = ROOT / 'Docs/HomesteadPilot/RemainingArt'
DEST = '/Game/Terrarium/HomesteadPilot/RemainingArt'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value): return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
def vec(value): return [value.x, value.y, value.z]
def transform(actor):
    t = actor.get_actor_transform()
    return {'location': vec(t.translation), 'scale': vec(t.scale3d),
            'quaternion': [t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w]}

def specs():
    result = json.loads((DOC / 'manifest.json').read_text())['assets']
    assert len(result) == 15
    for key in ('BlueShed', 'Tower'):
        result.append({'name': key, 'baseline_mesh': '/Game/Terrarium/Environment/Meshes/SM_Env_' + key,
            'collision': 'complex_as_simple', 'screen_sizes': [1., .20, .065], 'unreal_reduction': [1., .72, .42]})
    return result

def assert_editor():
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    assert not editor.get_game_world(), 'Stop PIE before verification or resume'
    assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'

def package_file(asset_path):
    package = asset_path.split('.')[0]
    assert package.startswith('/Game/Terrarium/')
    path = ROOT / 'Content' / (package[len('/Game/'):] + '.uasset')
    assert path.is_file(), path
    return path

def inputs(spec):
    for lod in spec.get('lods', []):
        assert digest(ROOT / lod['fbx']) == lod['sha256'], (spec['name'], 'Source changed')
    result = {'spec_sha256': canonical(spec), 'baseline_package_sha256': digest(package_file(spec['baseline_mesh']))}
    baseline = unreal.load_asset(spec['baseline_mesh']); assert baseline
    result['baseline_materials'] = {s.material_interface.get_path_name(): digest(package_file(s.material_interface.get_path_name())) for s in baseline.static_materials}
    return result

def verify(spec, receipt):
    key = spec['name']; path = DEST + '/Meshes/SM_HP_' + key
    assert receipt['name'] == key and receipt['mesh'].split('.')[0] == path
    mesh = unreal.load_asset(path); baseline = unreal.load_asset(spec['baseline_mesh'])
    assert isinstance(mesh, unreal.StaticMesh) and isinstance(baseline, unreal.StaticMesh)
    sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    assert sub.get_lod_count(mesh) == 3
    triangles = [mesh.get_num_triangles(i) for i in range(3)]
    assert triangles == receipt['triangles'] and triangles[0] > triangles[1] > triangles[2] > 0
    native_exceptions = []
    if spec.get('lods'):
        for lod, actual in zip(spec['lods'], triangles):
            if actual == lod['triangles']: continue
            # No percentage tolerance: each difference requires an exact native
            # A/B import receipt for this immutable FBX and the actual build flag.
            probe = json.loads((DOC / 'native-degenerate-filter-probe.json').read_text())
            evidence = next(row for row in probe['assets'] if row['name'] == key and row['level'] == lod['level'])
            assert evidence['source_sha256'] == lod['sha256'] == digest(ROOT / lod['fbx'])
            assert evidence['source_triangles'] == lod['triangles']
            assert evidence['native_with_degenerate_filter'] == actual
            assert evidence['temporary_asset_deleted'] and evidence['admitted_asset_unchanged']
            assert sub.get_lod_build_settings(mesh, lod['level']).get_editor_property('remove_degenerates')
            native_unfiltered = evidence['native_without_degenerate_filter']
            mandatory_degenerates = lod['triangles'] - native_unfiltered
            normalization_reason = 'None'
            if mandatory_degenerates:
                source_diagnostic = json.loads((DOC / 'degenerate-source-diagnostic.json').read_text())
                source_evidence = next(row for row in source_diagnostic['assets'] if row['name'] == key and row['level'] == lod['level'])
                assert source_evidence['fbx_sha256'] == lod['sha256']
                if mandatory_degenerates == source_evidence['zero_area_triangles']:
                    normalization_reason = 'Matches independently measured exact-zero-area source triangle count'
                else:
                    # Storm contains n-gons whose native FBX normalization differs
                    # from Blender triangulation even when the optional filter is
                    # disabled. Admit only the two specifically reviewed immutable
                    # files, with exact native A/B counts and explicit provenance.
                    allowances = json.loads((DOC / 'native-normalization-allowances.json').read_text())
                    allowance = next(row for row in allowances['assets'] if row['name'] == key and row['level'] == lod['level'])
                    assert allowance['source_sha256'] == lod['sha256']
                    assert allowance['source_triangles'] == lod['triangles']
                    assert allowance['native_without_degenerate_filter'] == native_unfiltered
                    assert allowance['native_with_degenerate_filter'] == actual
                    assert allowance['native_import_normalization_triangles'] == mandatory_degenerates
                    if 'baseline_native_lod0_triangles' in allowance:
                        assert baseline.get_num_triangles(0) == allowance['baseline_native_lod0_triangles']
                    normalization_reason = allowance['basis']
            assert native_unfiltered - actual == evidence['native_removed_triangles']
            assert lod['triangles'] - actual == mandatory_degenerates + evidence['native_removed_triangles']
            native_exceptions.append({**evidence, 'native_unfiltered_normalization_triangles': mandatory_degenerates,
                'normalization_evidence': normalization_reason,
                'accounted_total_removed': lod['triangles'] - actual})
    sizes = list(sub.get_lod_screen_sizes(mesh))
    assert not mesh.is_lod_screen_size_auto_computed()
    assert all(abs(a-b) < 1e-5 for a,b in zip(sizes, spec['screen_sizes']))
    assert not sub.get_nanite_settings(mesh).get_editor_property('enabled')
    slots = mesh.static_materials
    assert len(slots) == len(baseline.static_materials) == len(receipt['materials'])
    materials = [slot.material_interface.get_path_name() for slot in slots]
    assert materials == [row['pilot'] for row in receipt['materials']]
    assert all(m.startswith(DEST + '/Materials/') for m in materials)
    section_slots = [[sub.get_lod_material_slot(mesh, lod, section) for section in range(mesh.get_num_sections(lod))] for lod in range(3)]
    assert section_slots[0] == section_slots[1] == section_slots[2], (key, 'LOD section material drift', section_slots)
    assert sorted(section_slots[0]) == list(range(len(materials))), (key, 'Unused or repeated material slot', section_slots)
    a = mesh.get_bounding_box(); b = baseline.get_bounding_box()
    error = max(abs(x-y) for x,y in zip(vec(a.min)+vec(a.max), vec(b.min)+vec(b.max)))
    assert error < .15, (key, error)
    restoration_path = ROOT / 'Docs/HomesteadPilot/RuntimeCompletion/art-collision-restoration.json'
    restoration = json.loads(restoration_path.read_text())
    assert restoration['all_match_inherited'] and restoration['restored_components'] == 17
    policies = [row for row in restoration['rows'] if row['mesh'].split('.')[0] == path]
    assert len(policies) == len(receipt['placements']), (key, 'Missing baseline collision restoration coverage')
    body = mesh.get_editor_property('body_setup')
    inherited_body = baseline.get_editor_property('body_setup')
    flag = body.get_editor_property('collision_trace_flag')
    assert flag == inherited_body.get_editor_property('collision_trace_flag'), (key, 'Baseline collision trace policy changed')
    assert body.get_editor_property('double_sided_geometry') == inherited_body.get_editor_property('double_sided_geometry')
    collision_lod = mesh.get_editor_property('lod_for_collision')
    simple_count = sub.get_simple_collision_count(mesh)
    assert collision_lod == baseline.get_editor_property('lod_for_collision')
    assert simple_count == sub.get_simple_collision_count(baseline)
    for policy in policies:
        assert policy['matches_inherited_policy'] and policy['source_disk_unchanged']
        assert policy['source'].split('.')[0] == spec['baseline_mesh']
        assert policy['source_sha256'] == digest(package_file(spec['baseline_mesh']))
        assert policy['body_after']['collision_trace_flag'] == str(flag)
        assert policy['body_after']['double_sided_geometry'] == str(body.get_editor_property('double_sided_geometry'))
        assert policy['collision_lod'] == collision_lod
        assert policy['simple_collision_primitives'] == simple_count
    scene = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    found = []; overrides = {}
    for actor in scene:
        for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
            assigned = comp.get_editor_property('static_mesh')
            if assigned and assigned.get_path_name().split('.')[0] == spec['baseline_mesh']:
                raise AssertionError((key, 'Inherited actor not migrated', actor.get_actor_label()))
            if not assigned or assigned.get_path_name().split('.')[0] != path: continue
            assert comp.get_editor_property('forced_lod_model') == 0
            policy = next(row for row in policies if row['component'] == comp.get_path_name() and row['actor'] == actor.get_actor_label())
            actual_component_policy = {'collision_profile': str(comp.get_collision_profile_name()),
                'collision_enabled': str(comp.get_collision_enabled()),
                'overlaps': comp.get_editor_property('generate_overlap_events')}
            assert actual_component_policy == policy['component_after'], (key, actual_component_policy, policy['component_after'])
            found.append({'actor': actor.get_actor_label(), 'transform': transform(actor)})
            overrides[actor.get_actor_label()] = [m.get_path_name() if m else None for m in comp.get_editor_property('override_materials')]
    assert found and sorted(found, key=lambda r:r['actor']) == sorted(receipt['placements'], key=lambda r:r['actor']), (key, 'Actor placement drift')
    packages = {receipt['mesh']: digest(package_file(receipt['mesh']))}
    packages.update({m: digest(package_file(m)) for m in materials})
    return {'name': key, 'inputs': inputs(spec), 'packages': packages, 'triangles': triangles,
            'section_material_slots': section_slots, 'screen_sizes': sizes,
            'bounds_error_cm': error, 'collision_flag': str(flag), 'collision_lod': collision_lod,
            'simple_collision_primitives': simple_count, 'collision_policy': 'inherited baseline body and original component settings',
            'collision_restoration_receipt_sha256': digest(restoration_path), 'placements': found,
            'component_material_overrides': overrides, 'native_triangle_filter_evidence': native_exceptions,
            'receipt': receipt}

def completed_rows():
    # Progress can be newer than an older final receipt after an interrupted retry.
    candidates = [p for p in (DOC / 'unreal-integration-progress.json', DOC / 'unreal-integration.json') if p.exists()]
    if not candidates: return []
    return json.loads(max(candidates, key=lambda p:p.stat().st_mtime_ns).read_text())['assets']
