"""Prepare outline and coarse pigment measurements used only during authoring."""
import json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/Ember'
source=root/'SourceAssets/Voxel/ember.png';im=Image.open(source).convert('RGB')
rgb=np.array(im).astype(int);mask=~((rgb[:,:,0]>rgb[:,:,1]+60)&(rgb[:,:,2]>rgb[:,:,1]+60))
bottom=[]
for x in range(im.width):
    ys=np.flatnonzero(mask[:,x]);bottom.append(int(ys[-1]) if len(ys) else None)
(out/'source-column-bottoms.json').write_text(json.dumps(bottom))
small=im.resize((314,314));cells=[]
for y in range(314):
    row=[]
    for x in range(314):
        r,g,b=small.getpixel((x,y))
        if r>g+60 and b>g+60:q=None
        elif r>190 and g>180 and b>120:q=6
        elif r>190 and g>170:q=4
        elif r>190 and g>135:q=3
        elif r>190 and g>100:q=2
        else:q=0
        row.append(q)
    cells.append(row)
(out/'source-pigment-cells.json').write_text(json.dumps(cells,separators=(',',':')))
files={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['source-column-bottoms.json','source-pigment-cells.json']}
(out/'reference-sampling.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'files':files,'purpose':'Authoring measurements for inferred cube elevations and uniform per-block pigments. No source PNG texture is included in the exported model.','limits':'Coarse color classification is an estimate, not intrinsic albedo recovery or a fidelity metric.'},indent=2))
print('Recorded source-bound Ember authoring measurements.')
