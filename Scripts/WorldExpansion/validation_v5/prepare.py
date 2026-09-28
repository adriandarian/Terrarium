"""Filesystem-only preparation; historical WorldExpansion receipts are immutable."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / 'Docs/WorldExpansion'
OUT = OLD / 'V5'
OUT.mkdir(parents=True, exist_ok=True)
for name in ('original-baseline.json', 'settlement-integration.json'):
    destination = OUT / name
    if not destination.exists():
        shutil.copy2(OLD / name, destination)
    if name == 'original-baseline.json':
        assert hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256((OLD / name).read_bytes()).digest()
request = json.loads((OLD / 'validation-request.json').read_text())
request['output_tag'] = 'validation'
if not (OUT / 'validation-request.json').exists():
    (OUT / 'validation-request.json').write_text(json.dumps(request, indent=2), encoding='utf-8')
routes = json.loads((OLD / 'traversal-request-full.json').read_text())
assert len(routes['test_routes']) == 8, 'Use the eight-route regional request, not the supplemental one-route request'
if not (OUT / 'traversal-request.json').exists():
    (OUT / 'traversal-request.json').write_text(json.dumps(routes, indent=2), encoding='utf-8')
defaults = {
    'snapshot-request.json': {'name': 'before'},
    'observation-request.json': {'name': 'idle', 'scope': 'V5 passive sample; no captures, imports or diagnostic queries during sampling.'},
    'contract.json': {'map': '/Game/Terrarium/WorldExpansion/Maps/ValleyRegion',
        'terrain_manifest': 'SourceAssets/WorldExpansion/TerrainV5/manifest.json',
        'textures': [], 'material_texture_parameters': [], 'material_used_textures': [],
        'actor_bindings': [], 'foliage_groups': [],
        'notes': 'Fill expected native bindings after generation/admission. Empty texture/binding arrays do not pass material acceptance.'},
    'review-request.json': {'publish': False, 'captures': [], 'concept_images': [],
        'visual_review': {'accepted': False, 'notes': 'Native visual review pending; generated textures or concept artwork do not establish an editor result.'}},
}
for name, value in defaults.items():
    if not (OUT / name).exists():
        (OUT / name).write_text(json.dumps(value, indent=2), encoding='utf-8')
print('V5 requests prepared. Original baseline and historical review untouched.')
