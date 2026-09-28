"""Read-only final coverage/material/transform checks and resumable checkpoint.

Execute through the coordinator's verified editor. Re-run after saving/reopening
StartingHome to establish persistence; this script itself does not save the map.
"""
import sys, json, importlib
from pathlib import Path
folder = Path('C:/Users/hello/Projects/Terrarium/Scripts/HomesteadPilot/RemainingArt')
if str(folder) not in sys.path: sys.path.insert(0, str(folder))
import remaining_art_checks as checks
checks = importlib.reload(checks)

checks.assert_editor()
specs = checks.specs(); receipt_rows = {r['name']: r for r in checks.completed_rows()}
assert set(receipt_rows) == {s['name'] for s in specs}, 'All 17 completed integration receipts required'
rows = [checks.verify(spec, receipt_rows[spec['name']]) for spec in specs]
result = {'manifest_sha256': checks.digest(checks.DOC / 'manifest.json'), 'verified_families': len(rows),
    'verification_scope': '17 actual meshes; three decreasing LODs; section material slot parity; actual materials; inherited baseline body/component collision checked against explicit restoration receipt; untouched placement transforms; forced LOD zero; source and package fingerprints. No visual or movement claims.',
    'assets': rows}
(checks.DOC / 'unreal-verification.json').write_text(json.dumps(result, indent=2))
(checks.DOC / 'resume-checkpoint.json').write_text(json.dumps(result, indent=2))
print('VERIFIED_REMAINING_ART_UNREAL', len(rows))
