"""Read-only V5 geometry/ground inventory plus explicit surface provenance contract.

Root fills Docs/WorldExpansion/V5/contract.json with actual admitted bindings.
An empty contract is deliberately not accepted as proof of a texture correction.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
sys.path.insert(0, str(ROOT / 'Scripts/WorldExpansion/validation_v5'))
from common import OUT, assert_baseline_copy, legacy_source, execute_source
assert_baseline_copy()
execute_source(legacy_source('validate_world.py'), 'validate_world.py')
inventory = json.loads((OUT / 'validation.json').read_text())
contract = json.loads((OUT / 'contract.json').read_text())
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().split('.')[0] == contract['map']
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
errors, warnings, textures, materials, bindings, foliage = [], [], [], [], [], []


def full_path(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def mesh_components(actor):
    return actor.get_components_by_class(unreal.StaticMeshComponent)


if not contract.get('textures'):
    errors.append('No generated texture source contract provided')
if not contract.get('actor_bindings'):
    errors.append('No expected native V5 actor/material bindings provided')
if not (contract.get('material_used_textures') or contract.get('material_texture_parameters')):
    errors.append('No expected material-to-texture reference contract provided')
for item in contract.get('textures', []):
    row = dict(item)
    try:
        file = full_path(item['source_file'])
        data = file.read_bytes()
        row['source_sha256'] = hashlib.sha256(data).hexdigest()
        row['source_bytes'] = len(data)
        assert len(data) > 128, 'Texture source is empty or implausibly small'
        if item.get('sha256'):
            assert row['source_sha256'] == item['sha256'], 'Source texture hash mismatch'
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            row['source_size_px'] = list(struct.unpack('>II', data[16:24]))
        if item.get('generated_source_file'):
            generated_hash = hashlib.sha256(full_path(item['generated_source_file']).read_bytes()).hexdigest()
            row['matches_original_generated_output'] = generated_hash == row['source_sha256']
            assert row['matches_original_generated_output'], 'Copied texture differs from specified generated output'
        else:
            row['matches_original_generated_output'] = None
            warnings.append('No original generated output file supplied for byte comparison: ' + str(file))
        asset = unreal.load_asset(item['unreal_asset'])
        assert isinstance(asset, unreal.Texture2D), 'Expected imported Texture2D'
        row['actual_unreal_asset'] = asset.get_path_name()
        row['native_source_hash_metadata'] = str(unreal.EditorAssetLibrary.get_metadata_tag(asset, 'TerrariumImagegenSourceSHA256'))
        assert row['native_source_hash_metadata'] == row['source_sha256'], 'Imported texture source metadata does not match current bytes'
        row['srgb'] = bool(asset.get_editor_property('srgb'))
        row['power_of_two_mode'] = str(asset.get_editor_property('power_of_two_mode'))
        row['mip_gen_settings'] = str(asset.get_editor_property('mip_gen_settings'))
        for setting in ('power_of_two_mode', 'mip_gen_settings'):
            if setting in item:
                assert item[setting] in row[setting], 'Unexpected texture ' + setting
        if 'srgb' in item:
            assert row['srgb'] == item['srgb'], 'Unexpected texture color space'
        if hasattr(asset, 'blueprint_get_size_x'):
            row['native_size_px'] = [asset.blueprint_get_size_x(), asset.blueprint_get_size_y()]
            if 'native_size_px' in item:
                assert row['native_size_px'] == item['native_size_px'], 'Native texture dimensions differ from explicit import contract'
            elif 'source_size_px' in row and not item.get('native_resampling'):
                assert row['native_size_px'] == row['source_size_px'], 'Imported native size differs from source image'
        try:
            row['import_source_files'] = [str(p) for p in asset.get_editor_property('asset_import_data').extract_filenames()]
        except Exception as exc:
            row['import_metadata_note'] = str(exc)
        row['passed'] = True
    except Exception as exc:
        row.update(passed=False, error=str(exc))
        errors.append('Texture contract failed: ' + item.get('unreal_asset', '') + ': ' + str(exc))
    textures.append(row)

for item in contract.get('material_used_textures', []):
    row = dict(item)
    try:
        mat = unreal.load_asset(item['material'])
        assert mat, 'Material is missing'
        used = unreal.MaterialEditingLibrary.get_used_textures(mat)
        row['actual_textures'] = [texture.get_path_name() for texture in used]
        for expected in item['textures']:
            texture = unreal.load_asset(expected)
            assert texture and texture.get_path_name() in row['actual_textures'], 'Material does not reference expected texture: ' + expected
        row['passed'] = True
    except Exception as exc:
        row.update(passed=False, error=str(exc))
        errors.append('Material texture reference failed: ' + item['material'] + ': ' + str(exc))
    materials.append(row)
for item in contract.get('material_texture_parameters', []):
    row = dict(item)
    try:
        mat, expected = unreal.load_asset(item['material']), unreal.load_asset(item['texture'])
        assert mat and expected
        actual = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mat, item['parameter'])
        row['actual_texture'] = actual.get_path_name() if actual else None
        assert actual == expected, 'Texture parameter binding mismatch'
        row['passed'] = True
    except Exception as exc:
        row.update(passed=False, error=str(exc))
        errors.append('Material parameter failed: ' + item['material'] + ': ' + str(exc))
    materials.append(row)

for item in contract.get('actor_bindings', []):
    matched = [a for a in actors if a.get_actor_label().startswith(item['prefix'])]
    row = {'prefix': item['prefix'], 'actor_count': len(matched), 'components': [], 'errors': []}
    if 'count' in item and len(matched) != item['count']:
        row['errors'].append('Expected actor count ' + str(item['count']))
    if not matched:
        row['errors'].append('No matching actors')
    for actor in matched:
        for comp in mesh_components(actor):
            mesh = comp.get_editor_property('static_mesh')
            observed = {'actor': actor.get_actor_label(), 'component': comp.get_path_name(),
                'mesh': mesh.get_path_name() if mesh else None,
                'materials': [comp.get_material(i).get_path_name() if comp.get_material(i) else None for i in range(comp.get_num_materials())],
                'visible': bool(comp.get_editor_property('visible')),
                'hidden_in_game': bool(comp.get_editor_property('hidden_in_game')),
                'collision_profile': str(comp.get_collision_profile_name()),
                'collision_enabled': str(comp.get_collision_enabled()),
                'forced_lod': int(comp.get_editor_property('forced_lod_model')),
                'lods': mesh.get_num_lods() if mesh else 0,
                'collision_trace_flag': str(mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')) if mesh else None}
            try:
                assert mesh, 'Missing mesh'
                if item.get('mesh_prefix'):
                    assert observed['mesh'].startswith(item['mesh_prefix']), 'Unexpected mesh source'
                for slot, path in item.get('materials', {}).items():
                    expected = unreal.load_asset(path)
                    assert expected and comp.get_material(int(slot)) == expected, 'Unexpected material in slot ' + slot
                for key in ('visible', 'hidden_in_game', 'collision_profile'):
                    if key in item:
                        assert observed[key] == item[key], 'Unexpected ' + key
                for key in ('collision_enabled', 'collision_trace_flag'):
                    if key in item:
                        assert item[key] in observed[key], 'Unexpected ' + key
                assert observed['forced_lod'] == 0, 'Forced visual LOD must remain automatic'
                assert observed['lods'] >= item.get('min_lods', 1), 'Missing required visible LODs'
                observed['passed'] = True
            except Exception as exc:
                observed.update(passed=False, error=str(exc))
                row['errors'].append(actor.get_actor_label() + ': ' + str(exc))
            row['components'].append(observed)
    errors.extend(row['errors'])
    bindings.append(row)

all_components = {c.get_path_name(): c for a in actors for c in mesh_components(a)}
if not contract.get('foliage_groups'):
    errors.append('V5 ecology integration groups are missing; run prepare_contract.py after ecology admission')
for item in contract.get('foliage_groups', []):
    row = dict(item)
    try:
        components = [all_components[path] for path in item['components']]
        row['actual_instances'] = sum(c.get_instance_count() for c in components)
        assert row['actual_instances'] == item['count'], 'Instance count mismatch'
        for comp in components:
            mesh = comp.get_editor_property('static_mesh')
            if item.get('mesh'):
                assert mesh == unreal.load_asset(item['mesh']), 'Foliage mesh mismatch'
            if 'min_lods' in item:
                assert mesh.get_num_lods() >= item['min_lods'], 'Foliage render LOD count mismatch'
            if 'simple_collision_primitives' in item:
                assert unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_simple_collision_count(mesh) == item['simple_collision_primitives'], 'Foliage simple collision primitive mismatch'
            if 'collision_trace_flag' in item:
                assert item['collision_trace_flag'] in str(mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')), 'Foliage mesh collision policy mismatch'
            if item.get('collision_profile'):
                assert str(comp.get_collision_profile_name()) == item['collision_profile'], 'Foliage collision profile mismatch'
            for slot, path in item.get('materials', {}).items():
                actual = comp.get_material(int(slot))
                assert (actual.get_path_name() if actual else None) == path, 'Foliage material override mismatch in slot ' + slot
        row['passed'] = True
    except Exception as exc:
        row.update(passed=False, error=str(exc))
        errors.append('Foliage group failed: ' + item.get('name', '') + ': ' + str(exc))
    foliage.append(row)

report = {'map': contract['map'], 'base_inventory_passed': inventory['passed'],
    'textures': textures, 'material_texture_references': materials, 'native_actor_bindings': bindings,
    'foliage_groups': foliage, 'errors': errors, 'warnings': warnings,
    'passed': inventory['passed'] and not errors,
    'scope': 'Actual editor component/material/texture references, native geometry/collision settings, source file hashes and optional original generated-output byte comparison.',
    'limits': 'Generated source files and concept images do not establish final visual quality. Native screenshots and independent visual acceptance remain required. This does not hash decoded GPU texels or prove seamless texture tiling.'}
(OUT / 'surface-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('V5 surface contract validation: ' + str(report['passed']))
