"""Read-only native before/admitted/reopened V5 snapshots; original baseline retained."""
import json
import sys
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
sys.path.insert(0, str(ROOT / 'Scripts/WorldExpansion/validation_v5'))
from common import OUT, assert_baseline_copy, legacy_source, execute_source
assert_baseline_copy()
phase = json.loads((OUT / 'snapshot-request.json').read_text())['name']
assert phase in ('before', 'admitted', 'reopened')
source = legacy_source('snapshot_world.py')
if phase == 'before':
    assert not (OUT / 'before.json').exists(), 'V5 before snapshot already exists; preserve it'
    old = "name = json.loads(REQUEST.read_text())['name'] if REQUEST.exists() else 'original-baseline'"
    assert source.count(old) == 1
    source = source.replace(old, "name = 'admitted'")
    source = source.replace("destination = OUT / (name + '.json')", "destination = OUT / 'before.json'")
execute_source(source, 'snapshot_world.py')
