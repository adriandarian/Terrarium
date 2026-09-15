"""Serialize one team's modeling recipes through the verified editor."""
import importlib
import json
import sys
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root = Path(unreal.Paths.project_dir())
sys.path.insert(0, str(root / 'Scripts/Assets'))
sys.path.insert(0, str(root / 'Scripts/Migration'))
name = (root / 'Saved/migration-models.txt').read_text().strip()
assert name in ['characters', 'structures']
module = importlib.import_module(name)
importlib.reload(module)
records = module.build_all()
for record in records:
    assert unreal.EditorAssetLibrary.does_asset_exist(record['asset']), record
    validation = json.loads((root / 'Docs/Phase1/Validation' / (record['name'] + '.json')).read_text())
    assert validation['saved_normal_errors'] == 0
    record['validation'] = validation
(root / 'Docs/AssetMigration' / (name + '-built.json')).write_text(json.dumps(records, indent=2))
unreal.log('MIGRATION_MODELS_VALIDATED ' + name)
