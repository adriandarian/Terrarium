"""Repair library-only .blend outputs and independently reopen every project."""
import subprocess,json,hashlib,shutil,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];binary=Path('C:/Program Files/Blender Foundation/Blender 5.2/blender.exe')
rows=[];start=time.time();report=root/'Docs/BlenderRebuild/project-packaging-verification.json'
for folder in sorted((root/'Docs/BlenderRebuild').iterdir()):
    if not (folder/'mesh-validation.json').is_file():continue
    key=folder.name;source=root/'SourceAssets/Blender'/key/(key+'.blend');assert source.is_file()
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    verified=json.loads((folder/'saved-blend-verification.json').read_text()) if (folder/'saved-blend-verification.json').is_file() else {}
    already_normal=verified.get('direct_project_open_in_independent_process') and verified.get('sha256')==before
    if not already_normal:
        backup=root/'Saved/BlenderRebuild/pre-project-packaging'/(key+'_'+before[:16]+'.blend');backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,backup)
        proc=subprocess.run([str(binary),'--background','--factory-startup','--python-exit-code','1','--python',str(root/'Scripts/BlenderRebuild/package_blend.py'),'--',key],capture_output=True,text=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        assert proc.returncode==0 and 'PACKAGED_NORMAL_BLEND '+key in proc.stdout,(key,proc.stdout,proc.stderr)
    if not already_normal:
        proc=subprocess.run([str(binary),'--background',str(source),'--python-exit-code','1','--python',str(root/'Scripts/BlenderRebuild/verify_opened_blend.py')],capture_output=True,text=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        assert proc.returncode==0 and 'VERIFIED_NORMAL_BLEND '+key in proc.stdout,(key,proc.stdout,proc.stderr)
    verified=json.loads((folder/'saved-blend-verification.json').read_text());assert verified['sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
    rows.append({'asset':key,'repackaged':not already_normal,'before_sha256':before,**verified})
    report.write_text(json.dumps({'assets_verified':len(rows),'elapsed_seconds':time.time()-start,'scope':'Direct-open source usability, active scenes/cameras, part counts, packed textures, exported triangle counts and material/UV slots. No visual acceptance implied.','assets':rows},indent=2))
    print('VERIFIED',key,len(rows),flush=True)
print('COLLECTION_PROJECT_OPEN_COMPLETE',len(rows),flush=True)
