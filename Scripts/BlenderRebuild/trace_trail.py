"""Extract the pale paver regions from the supplied trail image for Blender tracing."""
from PIL import Image,ImageFilter
from pathlib import Path
from collections import deque,defaultdict
import numpy as np,json,hashlib,sys
root=Path(__file__).resolve().parents[2];source=root/'SourceAssets/Voxel/terrain_trail_top_v8.png'
folder=root/'Docs/BlenderRebuild/TrailTerrain';folder.mkdir(exist_ok=True)
im=Image.open(source).convert('RGB');n=256
rgb=np.asarray(im.resize((n,n),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(1)),dtype=float)
threshold=float(sys.argv[1]) if len(sys.argv)>1 else -28
mask=(rgb[:,:,2]-.46*rgb[:,:,0]>threshold)
mask=np.asarray(Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)))>0
seen=np.zeros((n,n),dtype=bool);regions=[]
for y in range(n):
    for x in range(n):
        if seen[y,x] or not mask[y,x]:continue
        pixels=[];q=deque([(x,y)]);seen[y,x]=True
        while q:
            px,py=q.popleft();pixels.append((px,py))
            for nx,ny in [(px-1,py),(px+1,py),(px,py-1),(px,py+1)]:
                if 0<=nx<n and 0<=ny<n and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;q.append((nx,ny))
        if len(pixels)<30:continue
        cells=set(pixels);edges=defaultdict(list)
        for px,py in pixels:
            for neighbor,a,b in [((px,py-1),(px,py),(px+1,py)),((px+1,py),(px+1,py),(px+1,py+1)),((px,py+1),(px+1,py+1),(px,py+1)),((px-1,py),(px,py+1),(px,py))]:
                if neighbor not in cells:edges[a].append(b)
        loops=[]
        while edges:
            start=min(edges);loop=[start];at=start
            while True:
                options=edges[at];nxt=options.pop()
                if not options:del edges[at]
                if nxt==start:break
                loop.append(nxt);at=nxt
            if len(loop)>3:loops.append(loop)
        def area(loop):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(loop,loop[1:]+loop[:1]))/2)
        loop=max(loops,key=area)
        # Remove collinear grid points; preserve the stepped source silhouette.
        loop=[b for a,b,c in zip(loop[-1:]+loop[:-1],loop,loop[1:]+loop[:1]) if (b[0]-a[0])*(c[1]-b[1])!=(b[1]-a[1])*(c[0]-b[0])]
        regions.append({'pixels':pixels,'outline':loop,'area_cells':len(pixels)})
outlines=[{'outline_px':[[x*im.width/n,y*im.height/n] for x,y in r['outline']],'area_source_px':r['area_cells']*(im.width/n)**2} for r in regions]
report={'source':str(source.relative_to(root)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_size_px':list(im.size),'tracing_grid':n,'chroma_threshold':threshold,'coverage_fraction':sum(r['area_cells'] for r in regions)/(n*n),'method':'Smoothed blue/red chroma threshold, closing and connected-component outlines. This is a candidate trace, not perfect recovery.','regions':outlines}
(folder/'paver-trace.json').write_text(json.dumps(report,indent=2))
preview=np.zeros((n,n,3),dtype='uint8')
for i,r in enumerate(regions):
    color=[70+(i*73)%180,70+(i*109)%180,70+(i*151)%180]
    for x,y in r['pixels']:preview[y,x]=color
Image.fromarray(preview).resize((1024,1024),Image.Resampling.NEAREST).save(folder/'paver-trace-preview.png')
print(f'Traced {len(regions)} candidate paver regions; coverage {report["coverage_fraction"]:.1%}; largest {max(r["area_cells"] for r in regions)} cells. Inspect the preview before authoring.')
