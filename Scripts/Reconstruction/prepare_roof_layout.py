"""Read the source roof's seam positions; write geometry guides, never images."""
import hashlib
import json
import argparse
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--key',choices=['cottage_roof_tile_v5','cottage_roof_tile_v6_candidate'],default='cottage_roof_tile_v5')
key=parser.parse_args().key
SOURCE=ROOT/'SourceAssets/Voxel'/(key+'.png')
rgb=np.asarray(Image.open(SOURCE).convert('RGB'),dtype=float)
lum=rgb@np.array([.2126,.7152,.0722])
height,width=lum.shape
# Source-observed course breaks. Local edge searches refine every individual
# tile independently, so these do not become straight geometry strips.
breaks=[0,76,182,286,389,491,599,708,813,918,1019,1122,1227,height]
if key=='cottage_roof_tile_v6_candidate':breaks=[0,194,409,618,834,1040,height]


def smooth(values,window=3):
    return np.convolve(np.pad(values,window//2,mode='edge'),np.ones(window)/window,mode='valid')


rows=[]
for row,(top,bottom) in enumerate(zip(breaks,breaks[1:])):
    center=(top+bottom)//2
    profile=smooth(lum[max(top,center-13):min(bottom,center+13)].mean(axis=0),3)
    # A vertical mortar seam is locally darker than both neighboring tile faces.
    contrast=np.minimum(np.roll(profile,11),np.roll(profile,-11))-profile
    candidates=[x for x in range(6,width-6) if contrast[x]>7 and contrast[x]>=max(contrast[max(0,x-3):x+4])]
    seams=[]
    for x in sorted(candidates,key=lambda x:contrast[x],reverse=True):
        if all(abs(x-s)>38 for s in seams):seams.append(int(x))
    seams=sorted(seams)
    edges=[0]+seams+[width]
    tiles=[]
    for col,(left,right) in enumerate(zip(edges,edges[1:])):
        if right-left<5:continue
        # Pick the dark foot of this tile near the observed course boundary.
        xs=slice(int(left+(right-left)*.2),max(int(left+(right-left)*.8),left+1))
        low=max(top+8,bottom-16);high=min(height,bottom+7)
        if bottom<height:
            edge_profile=smooth(lum[low:high,xs].mean(axis=1),3)
            end=int(low+np.argmin(edge_profile))-2
        else:end=height
        end=max(top+8,min(height,end))
        tiles.append({'left':left,'right':right,'top':top,'bottom':end})
    rows.append({'row':row,'seams_x_px':seams,'tiles':tiles})

record={'source':SOURCE.name,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'size_px':[width,height],'method':'source course guides and local dark vertical seam detection',
        'height_inference':'none; relief depth is explicitly authored in roof_surface.py',
        'rows':rows,'tile_count':sum(len(r['tiles']) for r in rows)}
path=ROOT/'Docs/Reconstruction'/('roof-tile-layout.json' if key=='cottage_roof_tile_v5' else 'roof-tile-v6-layout.json')
path.write_text(json.dumps(record,indent=2))
print(json.dumps({'tile_count':record['tile_count'],'rows':[{'row':r['row'],'seams':r['seams_x_px']} for r in rows]},indent=2))
