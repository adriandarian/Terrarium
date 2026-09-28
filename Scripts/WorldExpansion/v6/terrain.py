"""Continuous fractured terrain replaces V5's uniform shelves. Exact protected corridors."""
import sys,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'Scripts/WorldExpansion'))
import voxel_terrain as v5
S=R/'SourceAssets/WorldExpansion/V6/Terrain';S.mkdir(exist_ok=True)
manifest=[];cache={}
def vertex(i,j):
 if (i,j) in cache:return cache[i,j]
 x=-800+i*5;y=-800+j*5;keep=v5.preservation(x,y)
 base=v5.original(x,y);slope=math.hypot(v5.original(min(799,x+1),y)-v5.original(max(-799,x-1),y),v5.original(x,min(799,y+1))-v5.original(x,max(-799,y-1)))/2
 influence=(1-keep)*v5.smooth(.08,.6,slope)
 xx=x+(v5.noise(i,j,301)-.5)*3.2*influence;yy=y+(v5.noise(i,j,307)-.5)*3.2*influence
 z=v5.original(xx,yy)
 # Fine fractured strata, without flat 5m tiles or a shared quantization height.
 z+=influence*(1.1*math.sin(xx/8+yy/31)+.7*math.sin(yy/7-xx/17)+.5*(v5.noise(i,j,331)-.5))
 p=[round(xx,4),round(yy,4),round(z,4)];cache[i,j]=p;return p
for tx in range(8):
 for ty in range(8):
  vs=[];uv=[];ts=[]
  for i in range(tx*40,tx*40+40):
   for j in range(ty*40,ty*40+40):
    x=-800+i*5;y=-800+j*5
    if -65<x+2.5<65 and -65<y+2.5<65:continue
    n=len(vs);p=[vertex(a,b) for a,b in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]];vs+=p;uv += [[q[0]/2,q[1]/2] for q in p]
    ts += [[n,n+1,n+2],[n,n+2,n+3]] if (i+j)%2 else [[n,n+1,n+3],[n+1,n+2,n+3]]
  name=f'Terrain6_{tx}_{ty}';path=S/(name+'.json');path.write_text(json.dumps({'vertices':vs,'triangles':ts,'uv0':uv},separators=(',',':')))
  manifest.append({'name':name,'material':'ground','source':path.relative_to(R).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangles':len(ts)})
(S/'manifest.json').write_text(json.dumps({'geometry':manifest,'triangles':sum(q['triangles'] for q in manifest),'preserved':'V4 continuous roads, river banks, settlement bases; V5 outer home apron remains'},indent=2))
print('V6 terrain source',len(manifest),sum(q['triangles'] for q in manifest))
