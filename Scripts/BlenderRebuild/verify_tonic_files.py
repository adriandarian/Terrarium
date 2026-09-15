"""Verify on-disk export materials, color encoding and current source hashes."""
import json,struct,hashlib
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/MossTonic';source=root/'SourceAssets/Blender/MossTonic'
r=json.loads((out/'mesh-validation.json').read_text())
for name,meta in r['files'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==meta['sha256']
blob=(source/'SM_Blender_MossTonic.glb').read_bytes();size,kind=struct.unpack_from('<II',blob,12);g=json.loads(blob[20:20+size]);assert kind==0x4e4f534a
assert len(g['materials'])==3 and len(g['meshes'][0]['primitives'])==3
materials={m['name']:m for m in g['materials']}
for role,value in [('Glass',.82),('Liquid',.08)]:
    m=next(v for k,v in materials.items() if k.startswith('M_MossTonic_'+role))
    assert abs(m['extensions']['KHR_materials_transmission']['transmissionFactor']-value)<1e-6
image=Image.open(source/'MossTonic_BaseColor.png').convert('RGB');checks=[]
for i,hx in [(3,'73b58c'),(8,'b87925'),(11,'f4d793'),(20,'9bdac6')]:
    px=image.getpixel(((i%8)*64+32,511-((i//8)*64+32)));expected=tuple(int(hx[k:k+2],16) for k in (0,2,4))
    assert max(abs(v-e) for v,e in zip(px,expected))<=5,(i,px,expected)
    checks.append({'palette_index':i,'expected_srgb':expected,'png_srgb':px})
saved=json.loads((out/'saved-blend-verification.json').read_text());assert hashlib.sha256((source/'MossTonic.blend').read_bytes()).hexdigest()==saved['sha256']
(out/'export-material-verification.json').write_text(json.dumps({'three_gltf_materials_and_primitives':True,'transmission_extensions_verified':True,'palette_encoding_samples':checks,'current_file_hashes_verified':True},indent=2))
print('Moss Tonic: 3 GLB material primitives, transmission extensions, palette encoding and current file hashes verified.')
