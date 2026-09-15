"""Copy original reference bytes into this project for durable reimport."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('C:/Users/hello/Projects/Pokemon/assets/voxel')
DEST = ROOT / 'SourceAssets/Voxel'
DEST.mkdir(parents=True, exist_ok=True)
records = []
for source in sorted(SOURCE.glob('*.png')):
    target = DEST / source.name
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists():
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest, target
    else:
        shutil.copy2(source, target)
    records.append({'source': str(source), 'local_source': target.relative_to(ROOT).as_posix(), 'sha256': digest})
shutil.copy2(SOURCE / 'README.md', DEST / 'PROVENANCE.md')
out = ROOT / 'Docs/AssetMigration'
out.mkdir(parents=True, exist_ok=True)
(out / 'source-copy.json').write_text(json.dumps(records, indent=2))
print(f'Verified {len(records)} original PNG copies')
