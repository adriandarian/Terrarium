"""Compare raw front silhouettes only; never treat overlap as full fidelity."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/DeepDelverMark'
source=root/'SourceAssets/Voxel/deep_delver_mark.png';rgb=np.array(Image.open(source).convert('RGB'))
mask=~((rgb[:,:,0]>200)&(rgb[:,:,1]<80)&(rgb[:,:,2]>200))
rows=[]
for label,path in [('r5',out/'R5/front.png'),('r9',out/'front.png')]:
    image=np.array(Image.open(path).convert('RGBA'));assert image.shape[:2]==mask.shape
    actual=image[:,:,3]>127
    rows.append({'revision':label,'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'intersection_over_union':float((actual&mask).sum()/(actual|mask).sum()),
        'outside_reference_pixels':int((actual&~mask).sum()),'missing_reference_pixels':int((mask&~actual).sum())})
result={'reference_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dimensions':list(mask.shape),
    'method':'Reference excludes magenta RGB R>200,G<80,B>200. Render uses alpha>127. No rescaling or alignment.',
    'measurements':rows,'limits':'Front silhouette only. Does not measure internal relief, materials, lighting, rear geometry or gameplay. Not visual acceptance.'}
(out/'silhouette-comparison.json').write_text(json.dumps(result,indent=2))
html='''<!doctype html><meta charset="utf-8"><title>Deep Delver Mark refinement</title><style>body{margin:32px;background:#1b2021;color:#e8e8dc;font:16px/1.5 system-ui}.views{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}img{width:100%}figure{margin:0}p{max-width:95ch}a{color:#bed8c2}</style><h1>Deep Delver Mark refinement</h1><p>Comparison of the supplied concept, the previous draft and the current physical Blender model. Stone joints, shorter ledges, gold socket braces and lower corner flanges were refined. The cavern still differs in density and depth, and the materials remain under review.</p><div class="views">'''
for label,path in [('Original concept','../../../SourceAssets/Voxel/deep_delver_mark.png'),('Previous Blender draft','R5/front.png'),('Current Blender draft','front.png')]:html+=f'<figure><img src="{path}"><figcaption>{label}</figcaption></figure>'
html+='</div><p>Raw front silhouette intersection-over-union: '+', '.join(f'{r["revision"]}: {r["intersection_over_union"]:.2%}' for r in rows)+'. This measures only the outer shape; it is not a fidelity score for the asset.</p><p><a href="World/unreal-viewport.png">Current Unreal front view</a> · <a href="Side/unreal-viewport.png">Current Unreal side view</a> · <a href="rear.png">Inferred Blender rear</a></p>'
(out/'comparison.html').write_text(html,encoding='utf-8')
print(json.dumps(rows))
