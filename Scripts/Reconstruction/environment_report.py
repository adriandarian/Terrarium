"""Package the inspected scene comparison and verified delivery evidence."""
import json,shutil,hashlib,struct
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];out=root/'Docs/Environment'
source=Path('C:/Users/hello/.codex/attachments/1ccf9c86-0559-4bb2-8197-f3f4da9c0f7f/image-1.png')
shutil.copyfile(source,out/'reference.png')
r=json.loads((out/'verification.json').read_text())
assert r['saved_and_reopened_identically'] and r['material_bindings_verified']
assert all(abs(x['error_cm'])<.02 for x in r['contacts'])
captures={}
for name,size in [('assembled',(962,1618)),('courtyard',(1500,1000)),('crossing',(1500,1000))]:
    p=out/(name+'.png');data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==size
    captures[name]={'file':p.name,'dimensions':size,'sha256':hashlib.sha256(data).hexdigest()}
ini=(root/'Config/DefaultEngine.ini').read_text();assert 'GameDefaultMap=/Game/Terrarium/Maps/HomesteadReference' in ini and 'EditorStartupMap=/Game/Terrarium/Maps/HomesteadReference' in ini
r.update(verified_utc=datetime.now(timezone.utc).isoformat(),captures=captures,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),startup_and_default_map_verified=True,
         visual_acceptance='Feature and relative-layout audit passed; main inspected full Lit scene and courtyard/crossing close-ups. Artistic fidelity is approximate.',
         exact_artistic_parity=False,remaining_visual_differences=['Cleaner cottage surfaces and more regular roof courses','Some banded cliff column silhouettes remain','Foliage and water pattern distribution differs from the source'])
(out/'verification.json').write_text(json.dumps(r,indent=2))
(out/'comparison.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Terrarium · reference environment</title>
<style>*{box-sizing:border-box}body{margin:0;background:#17201b;color:#e9eadb;font:16px/1.6 system-ui,sans-serif}main{max-width:1140px;margin:0 auto;padding:36px 24px}h1{font:500 34px/1.2 Georgia,serif;margin:0 0 12px}p{color:#bfc9b8;max-width:850px}a{color:#ddd49f}nav{display:flex;gap:22px;flex-wrap:wrap;margin:24px 0}figure{margin:0}figcaption{padding:12px 0;color:#c2c9b9}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}.pair img{width:100%;height:auto;display:block;border-radius:6px}.details{display:grid;gap:24px;margin-top:30px}.details img{width:100%;border-radius:6px}small{display:block;color:#aeb8a7;margin-top:22px}button{background:#344335;border:1px solid #667557;color:#e9eadb;padding:10px 16px;border-radius:6px;cursor:pointer}body.wide main{max-width:1800px}@media(max-width:650px){main{padding:24px 12px}.pair{gap:8px}h1{font-size:28px}figcaption{font-size:13px}}</style>
<main><h1>The homestead, assembled</h1><p>The supplied reference alongside the native Unreal environment. The cottage, shed, garden, wheat terrace, stairs, river crossing and winding trail are assembled with the rebuilt explorer and vegetation.</p>
<nav><a href="README.md">Environment notes</a><a href="verification.json">Saved-level verification</a><a href="../../Content/Terrarium/Maps/HomesteadReference.umap">Unreal map</a><button onclick="document.body.classList.toggle('wide')">Toggle larger comparison</button></nav>
<div class="pair"><figure><img src="reference.png" alt="Supplied portrait reference"><figcaption>Supplied reference · the inset is an asset preview outside the scene</figcaption></figure><figure><img src="assembled.png" alt="Native Unreal reference environment"><figcaption>Unreal · HomesteadReference · actual Lit render</figcaption></figure></div>
<p>Feature and layout review passed. The reconstruction is more regular and cleaner in its surfaces than the source illustration; it is not an exact artistic copy. This is a static environment, with gameplay, collision and animation untested.</p>
<div class="details"><figure><img src="courtyard.png" alt="Cottage, rebuilt explorer, garden and courtyard"><figcaption>Courtyard and rebuilt explorer</figcaption></figure><figure><img src="crossing.png" alt="Stone stair approach and timber river crossing"><figcaption>Lower landing, riverbank and timber crossing</figcaption></figure></div>
<small>Level saved and reopened with identical mesh transforms and material bindings. The prior environment levels are retained.</small></main></html>''',encoding='utf-8')
print(json.dumps({'map':r['map'],'saved_reopened':True,'contacts':len(r['contacts']),'captures':list(captures),'startup_map':True,'visual_review':r['visual_acceptance']},indent=2))
