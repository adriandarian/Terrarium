import json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[3]
for n in range(0,64,16):
 (R/'Docs/WorldExpansion/V6/terrain-request.json').write_text(json.dumps({'offset':n,'limit':16}))
 start=time.time();subprocess.run([sys.executable,str(R/'Scripts/run_editor.py'),str(R/'Scripts/WorldExpansion/v6/admit_terrain.py')],check=True,capture_output=True)
 p=R/f'Docs/WorldExpansion/V6/terrain-{n:02d}.json';assert p.exists() and p.stat().st_mtime>start
 print('Admitted',n+16,'of 64',flush=True)
