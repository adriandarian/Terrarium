"""Read the saved project in a separate process without touching live Blender IDs."""
import bpy,subprocess,hashlib,json
from pathlib import Path
root=Path('C:/Users/hello/Projects/Terrarium');scene=bpy.context.scene
assert Path(scene.get('terrarium_project',''))==root
key=scene['asset_name'];source=root/'SourceAssets/Blender'/key/(key+'.blend')
proc=subprocess.run([bpy.app.binary_path,'--background',str(source),'--python-exit-code','1','--python',str(root/'Scripts/BlenderRebuild/verify_opened_blend.py')],capture_output=True,text=True,timeout=120,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
assert proc.returncode==0 and 'VERIFIED_NORMAL_BLEND '+key in proc.stdout,(proc.stdout,proc.stderr)
result=json.loads((root/'Docs/BlenderRebuild'/key/'saved-blend-verification.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==result['sha256']
