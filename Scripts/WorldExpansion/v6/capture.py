import json,subprocess,sys,time,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[3];D=R/'Docs/WorldExpansion';out=D/'V6/Captures';out.mkdir(exist_ok=True)
for name in sys.argv[1:] or [v['name'] for v in json.loads((D/'views.json').read_text())]:
 (D/'view-request.json').write_text(json.dumps({'name':name}))
 subprocess.run([sys.executable,str(R/'Scripts/run_editor.py'),str(R/'Scripts/WorldExpansion/v6/stage.py')],check=True,capture_output=True)
 time.sleep(2)
 subprocess.run([sys.executable,str(R/'Scripts/WorldExpansion/capture_view.py')],check=True,capture_output=True)
 for ext in ['png','json']:shutil.copy2(D/'Captures'/f'{name}.{ext}',out/f'{name}.{ext}')
 print(name,flush=True)
