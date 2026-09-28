"""Sequential coordinator runner, validates receipts after each editor operation."""
import json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[2]
for offset in range(0,64,4):
 p=R/f'Docs/WorldExpansion/TerrainV5/admission-{offset:03d}.json'
 (R/'Docs/WorldExpansion/voxel-terrain-request.json').write_text(json.dumps({'offset':offset,'limit':4}))
 start=time.time()
 subprocess.run([sys.executable,str(R/'Scripts/run_editor.py'),str(R/'Scripts/WorldExpansion/voxel_terrain_admit.py')],cwd=R,check=True,capture_output=True)
 assert p.exists() and p.stat().st_mtime>start,(offset,'Missing fresh native receipt')
 data=json.loads(p.read_text());assert data['chunks']==4 and len(data['admitted'])==8
 print(json.dumps({'offset':offset,'complete_chunks':offset+4,'seconds':round(time.time()-start,1)}),flush=True)
