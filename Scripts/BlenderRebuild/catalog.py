"""Maintain full source scope independently of prior reconstruction claims."""
import json,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
old=json.loads((ROOT/'Docs/Reconstruction/asset-map.json').read_text())
sources=sorted((ROOT/'SourceAssets/Voxel').glob('*.png'))
mapping={s:m for m in old['meshes'] for s in m['sources']}
built={};variants={}
for folder in (ROOT/'SourceAssets/Blender').iterdir():
    if not (folder/(folder.name+'.blend')).exists():continue
    receipt=ROOT/'Docs/BlenderRebuild'/folder.name/'mesh-validation.json'
    if not receipt.exists():continue
    r=json.loads(receipt.read_text())
    source=Path(r.get('source','SourceAssets/Voxel/'+folder.name.lower()+'.png')).name
    if r.get('variant_of'):
        variants.setdefault(source,[]).append({'asset':folder.name,'variant_of':r['variant_of'],'purpose':r.get('variant_purpose','')})
    else:built[source]=folder.name
rows=[]
for f in sources:
    m=mapping.get(f.name,{})
    key=built.get(f.name)
    rows.append({'source':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'family':m.get('module','unclassified'),'prior_unreal_mesh':m.get('selected_asset'),'blender_model':f'SourceAssets/Blender/{key}/{key}.blend' if key else None,'placement_variants':variants.get(f.name,[]),'status':'blender_authored_visual_refinement_pending' if key else 'pending_blender_rebuild','accepted_fidelity':False})
out=ROOT/'Docs/BlenderRebuild';out.mkdir(exist_ok=True)
(out/'inventory.json').write_text(json.dumps({'scope':'Every PNG in SourceAssets/Voxel; object models, texture materials, and associated view/animation references retain explicit coverage.','source_count':len(rows),'blender_assets':len(built),'placement_variant_count':sum(len(v) for v in variants.values()),'accepted_count':0,'assets':rows},indent=2))
glb=ROOT/'SourceAssets/Blender/Cottage/SM_Blender_Cottage.glb'
b=glb.read_bytes();magic,version,total=struct.unpack_from('<III',b);size,kind=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+size])
assert magic==0x46546c67 and version==2 and total==len(b)
assert len(g['meshes'])==1 and len(g['scenes'])==1
assert all('TEXCOORD_0' in p['attributes'] and 'NORMAL' in p['attributes'] for p in g['meshes'][0]['primitives'])
(out/'Cottage/glb-validation.json').write_text(json.dumps({'file':str(glb.relative_to(ROOT)),'bytes':len(b),'meshes':len(g['meshes']),'scenes':len(g['scenes']),'uv_and_normals':True,'visual_acceptance':False},indent=2))
print(f'{len(rows)} source PNGs tracked; {len(built)} Blender models in progress; 0 fidelity approvals.')
