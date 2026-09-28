"""Build expected V5 bindings from actual source manifests and admission receipts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Docs/WorldExpansion/V5'
terrain = json.loads((ROOT / 'SourceAssets/WorldExpansion/TerrainV5/manifest.json').read_text())
material_receipt = json.loads((OUT / 'imagegen-materials.json').read_text())
previous = json.loads((OUT / 'contract.json').read_text())
prior_textures = {r['unreal_asset']: r for r in previous.get('textures', [])}
generated_root = Path('C:/Users/hello/.codex/generated_images/01a0e4ff-7e37-7110-bc1a-ea5ad89fadeb')
generated_files = {'T_VoxelMeadow': 'exec-e63278c7-6171-4e5d-b023-b79bdf331f69.png',
                   'T_MossLimestone': 'exec-6cf959f0-1296-478f-aa2e-4d6d9f4946ef.png',
                   'T_OchreGravel': 'exec-ec8a83f2-0bde-40b0-928f-f5a9aced6ca4.png'}
base = '/Game/Terrarium/WorldExpansion/TerrainV5'
textures = []
for row in material_receipt['textures']:
    item = dict(prior_textures.get(row['texture'], {}))
    item.update(source_file=row['source_file'], unreal_asset=row['texture'], sha256=row['sha256'], srgb=True)
    item['generated_source_file'] = str(generated_root / generated_files[Path(row['source_file']).stem])
    item.update(native_resampling=True, power_of_two_mode='STRETCH_TO_POWER_OF_TWO', mip_gen_settings='TMGS_FROM_TEXTURE_GROUP')
    textures.append(item)
grass = base + '/Textures/T_VoxelMeadow.T_VoxelMeadow'
stone = base + '/Textures/T_MossLimestone.T_MossLimestone'
path = base + '/Textures/T_OchreGravel.T_OchreGravel'
used = [{'material': base + '/Materials/' + material, 'textures': refs} for material, refs in (
    ('M_VoxelGrass', [grass]), ('M_VoxelStone', [stone]), ('M_VoxelPath', [path]), ('M_VoxelGround', [grass, stone]))]
bindings = []
for role, name, material in [('ground', 'VoxelGround', 'M_VoxelGrass'), ('rock', 'VoxelRock', 'M_VoxelStone')]:
    bindings.append({'prefix': 'WX_' + name + '_',
        'count': sum(r['name'].startswith(name + '_') for r in terrain['assets']),
        'mesh_prefix': base + '/Meshes/SM_' + name + '_',
        'materials': {'0': base + '/Materials/' + material},
        'visible': True, 'hidden_in_game': False, 'collision_profile': 'BlockAll',
        'collision_enabled': 'QUERY_AND_PHYSICS', 'collision_trace_flag': 'CTF_USE_COMPLEX_AS_SIMPLE', 'min_lods': 1})
for asset in terrain['assets']:
    if asset['name'].startswith(('VoxelGround_', 'VoxelRock_')):
        continue
    bindings.append({'prefix': 'WX_' + asset['name'], 'count': 1,
        'mesh_prefix': base + '/Meshes/SM_' + asset['name'],
        'materials': {'0': base + '/Materials/' + ('M_VoxelGrass' if asset['role'] == 'ground' else 'M_VoxelStone')},
        'visible': True, 'hidden_in_game': False, 'collision_profile': 'BlockAll',
        'collision_enabled': 'QUERY_AND_PHYSICS', 'collision_trace_flag': 'CTF_USE_COMPLEX_AS_SIMPLE'})
bindings.append({'prefix': 'WX_Terrain_', 'count': sum(c['old_actor'].startswith('WX_Terrain_') for c in terrain['chunks']),
                 'visible': False, 'hidden_in_game': True, 'collision_profile': 'NoCollision', 'collision_enabled': 'NO_COLLISION'})
if any(c['old_actor'] == 'WX_HomeApron' for c in terrain['chunks']):
    bindings.append({'prefix': 'WX_HomeApron', 'count': 1, 'visible': False, 'hidden_in_game': True,
                     'collision_profile': 'NoCollision', 'collision_enabled': 'NO_COLLISION'})
for row in material_receipt.get('bindings', []):
    if row['actor'].startswith('WX_Terrain_') or row['actor'] == 'WX_HomeApron':
        continue
    bindings.append({'prefix': row['actor'], 'count': 1, 'materials': {'0': row['material']}})
foliage = []
ecology_path = ROOT / 'Docs/WorldExpansion/ecology-v5-integration.json'
if ecology_path.exists():
    ecology = json.loads(ecology_path.read_text())
    groups = ecology['groups']
    iterator = groups.items() if isinstance(groups, dict) else ((r.get('asset', str(i)), r) for i, r in enumerate(groups))
    for name, row in iterator:
        foliage.append({'name': name, 'components': row['components'], 'count': row['native_instance_count'],
                        'mesh': row['mesh'], 'collision_profile': 'NoCollision'})
path_materials_path = ROOT / 'Docs/WorldExpansion/ecology-v5-path-materials.json'
if path_materials_path.exists():
    path_materials = json.loads(path_materials_path.read_text())
    inherited_path = OUT / 'settlement-integration.json'
    inherited = json.loads(inherited_path.read_text())
    inherited_by_ft = {r['foliage_type']: r for r in inherited['instances']}
    for group in path_materials['groups']:
        if group['foliage_type'] in inherited_by_ft:
            original_group = inherited_by_ft[group['foliage_type']]
            assert group['count'] == original_group['count'], 'Path override changed the original expected instance count'
            assert group['transforms_preserved'] and group['source_mesh_unchanged'], 'Path override must preserve transforms and source geometry'
            assert sum(c['count'] for c in group['effective_components']) == original_group['count']
            original_group['components'] = [c['component'] for c in group['effective_components']]
            original_group['v5_component_replacement_evidence'] = str(path_materials_path.relative_to(ROOT))
        for component in group['effective_components']:
            foliage.append({'name': group['foliage_type'], 'components': [component['component']], 'count': component['count'],
                            'mesh': group['mesh'], 'materials': {str(i): value for i, value in enumerate(component['effective_materials'])}})
    inherited_path.write_text(json.dumps(inherited, indent=2), encoding='utf-8')
groves_path = ROOT / 'Docs/WorldExpansion/forest-groves-v5-integration.json'
if groves_path.exists():
    groves = json.loads(groves_path.read_text())
    foliage.append({'name': 'Additional V5 forest groves', 'components': [r['component'] for r in groves['components']],
                    'count': groves['native_trees'], 'mesh': groves['mesh'], 'collision_profile': 'BlockAll',
                    'min_lods': 3, 'simple_collision_primitives': 1, 'collision_trace_flag': 'CTF_USE_SIMPLE_AND_COMPLEX'})
reground_path = ROOT / 'Docs/WorldExpansion/TerrainV5/forest-reground.json'
if reground_path.exists():
    reground = json.loads(reground_path.read_text())
    groups = reground['groups']
    iterator = groups.items() if isinstance(groups, dict) else ((str(i), row) for i, row in enumerate(groups))
    for name, row in iterator:
        foliage.append({'name': 'Existing regional forest after reground ' + name,
                        'components': [entry['component'] for entry in row['components']],
                        'count': row['count'], 'mesh': row['mesh'], 'min_lods': 3,
                        'collision_profile': 'BlockAll' if 'BroadTree' in row['mesh'] else 'NoCollision'})
contract = {'map': '/Game/Terrarium/WorldExpansion/Maps/ValleyRegion',
    'terrain_manifest': 'SourceAssets/WorldExpansion/TerrainV5/manifest.json',
    'textures': textures, 'material_used_textures': used,
    'material_texture_parameters': [], 'actor_bindings': bindings, 'foliage_groups': foliage,
    'expected_ecology_receipt': str(ecology_path.relative_to(ROOT)),
    'notes': 'Generated texture sources plus expected actor/material/retirement bindings. Native validation and image review determine actual acceptance.'}
(OUT / 'contract.json').write_text(json.dumps(contract, indent=2), encoding='utf-8')
print(json.dumps({'textures': len(textures), 'binding_groups': len(bindings), 'foliage_groups': len(foliage)}))
