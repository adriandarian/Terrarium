"""Resume an interrupted coordinator import without rebuilding verified families.

Does not change the original importer. Requires the source manifest fingerprint
captured while the initial import was running. Completed rows are checked against
actual Unreal state before skipping; source/package fingerprints are checkpointed.
"""
import sys, json, importlib
from pathlib import Path
folder = Path('C:/Users/hello/Projects/Terrarium/Scripts/HomesteadPilot/RemainingArt')
if str(folder) not in sys.path: sys.path.insert(0, str(folder))
import remaining_art_checks as checks
checks = importlib.reload(checks)

checks.assert_editor()
stamp = json.loads((checks.DOC / 'initial-import-inputs.json').read_text())
assert checks.digest(checks.DOC / 'manifest.json') == stamp['manifest_sha256'], 'Inputs changed since initial import: review before resuming'
source = (folder / 'integrate_remaining_art.py').read_text()
assert checks.digest(folder / 'integrate_remaining_art.py') == stamp['importer_sha256'], 'Importer changed: review before resuming'
specs = checks.specs(); receipts = {r['name']: r for r in checks.completed_rows()}
checkpoint_path = checks.DOC / 'resume-checkpoint.json'
previous = {r['name']: r for r in json.loads(checkpoint_path.read_text())['assets']} if checkpoint_path.exists() else {}
verified = []; failures = []
for spec in specs:
    key = spec['name']
    if key not in receipts: continue
    try:
        row = checks.verify(spec, receipts[key])
        if key in previous:
            assert row['inputs'] == previous[key]['inputs'], 'Inputs changed from checkpoint'
            assert row['packages'] == previous[key]['packages'], 'Saved packages changed from checkpoint'
        verified.append(row)
    except AssertionError as exc:
        failures.append({'name': key, 'reason': str(exc)})
checkpoint_path.write_text(json.dumps({'manifest_sha256': stamp['manifest_sha256'], 'assets': verified, 'rebuild': failures}, indent=2))
skip = {row['name'] for row in verified}
skip_rows = [row['receipt'] for row in verified]
print('REMAINING_ART_RESUME_SKIP', sorted(skip), 'REBUILD', failures)
# Execute the unchanged coordinator implementation with a strictly checked loop
# filter. The initial importer is never rewritten, and completed progress remains.
needle = 'rows = []\nfor spec in specs:\n'
assert source.count(needle) == 1, 'Importer structure changed; refuse unsafe text patch'
patched = source.replace(needle, 'rows = list(VERIFIED_ROWS)\nfor spec in specs:\n    if spec["name"] in VERIFIED_SKIP: continue\n')
scope = {'__name__': '__main__', '__file__': str(folder / 'integrate_remaining_art.py'),
         'VERIFIED_ROWS': skip_rows, 'VERIFIED_SKIP': skip}
exec(compile(patched, str(folder / 'integrate_remaining_art.py'), 'exec'), scope)
