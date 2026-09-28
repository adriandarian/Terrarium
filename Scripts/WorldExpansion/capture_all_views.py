"""Sequentially stage and capture native review cameras through bundled MCP."""
import json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/'Docs/WorldExpansion'
names=sys.argv[1:] or [r['name'] for r in json.loads((D/'views.json').read_text())]
for name in names:
 (D/'view-request.json').write_text(json.dumps({'name':name}))
 subprocess.run([sys.executable,str(R/'Scripts/run_editor.py'),str(R/'Scripts/WorldExpansion/stage_view.py')],cwd=R,check=True,capture_output=True)
 time.sleep(1.5)
 subprocess.run([sys.executable,str(R/'Scripts/WorldExpansion/capture_view.py')],cwd=R,check=True)
