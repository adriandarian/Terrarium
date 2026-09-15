"""Compare projected source/model outlines without image registration or fitting."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/Grove'
source=root/'SourceAssets/Voxel/grove.png'
s=np.array(Image.open(source)).astype(int)
mask=~((s[:,:,0]>s[:,:,1]+60)&(s[:,:,2]>s[:,:,1]+60))
rows={}
for name,p in [('r7',out/'R7/front.png'),('r11',out/'R11/front.png'),('r13',out/'front.png')]:
    m=np.array(Image.open(p))[:,:,3]>127
    assert m.shape==mask.shape==(1254,1254)
    rows[name]={}
    for crop,lo,hi in [('full',0,1254),('leaves_and_fork',180,680),('base_below_stem',810,1200)]:
        a=mask[lo:hi];b=m[lo:hi]
        rows[name][crop]={'intersection_over_union':float(np.sum(a&b)/np.sum(a|b)),'mismatched_pixels':int(np.sum(a^b))}
    rows[name]['render_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Pixel silhouette intersection over union using source foreground against magenta and Blender alpha > 127, fixed matching 1254-pixel orthographic camera, no scaling/alignment optimization. Base crop rows 810 through 1199.','revisions':rows,'limits':'Projected outline only; excludes color, internal block divisions, depth and rear fidelity.'}
(out/'silhouette-comparison.json').write_text(json.dumps(report,indent=2))
print(json.dumps(rows,indent=2))
