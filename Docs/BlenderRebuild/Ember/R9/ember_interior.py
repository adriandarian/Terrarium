"""Fill short interior gaps between authored flame blocks with solid junctions."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
def close_interior(asset):
    root=Path('C:/Users/hello/Projects/Terrarium');joins=[]
    for _ in range(12):
        bpy.context.view_layer.update()
        ns={};exec(compile((root/'Scripts/BlenderRebuild/verify_ember_connections.py').read_text(),'connections.py','exec'),ns)
        groups=[[bpy.data.objects[n] for n in g if not bpy.data.objects[n].get('detached_reference_feature')] for g in ns['result']['groups']]
        groups=[g for g in groups if g]
        if len(groups)==1:break
        def bounds(ob):
            vs=[ob.matrix_world@Vector(v) for v in ob.bound_box]
            return [min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]
        best=None
        for i,g in enumerate(groups):
            for other in groups[:i]:
                for a in g:
                    al,ah=bounds(a)
                    for b in other:
                        bl,bh=bounds(b);gap=[max(0,al[k]-bh[k],bl[k]-ah[k]) for k in range(3)]
                        score=sum(v*v for v in gap)
                        if best is None or score<best[0]:best=(score,a,b,al,ah,bl,bh)
        distance,a,b,al,ah,bl,bh=best
        assert math.sqrt(distance)<.06,('Interior gap requires an authored shape decision',a.name,b.name,distance)
        center=[];size=[]
        for k in range(3):
            lo=max(al[k],bl[k]);hi=min(ah[k],bh[k])
            if hi<lo:
                center.append((lo+hi)/2);size.append(lo-hi+.025)
            else:
                center.append((lo+hi)/2);size.append(max(.025,min(.05,hi-lo)))
                if k==1 and hi-lo>=size[-1]:
                    center[-1]=hi-size[-1]/2
        index=int(a.get('palette_index',2))
        ob=asset.box('Solid interior junction',center,size,index,.002)
        ob['palette_index']=index;ob['inferred_interior']=True
        joins.append({'between':[a.name,b.name],'gap_m':math.sqrt(distance),'center_m':center,'dimensions_m':size})
    else:raise AssertionError('Flame body still has separate components')
    (asset.review/'interior-junctions.json').write_text(json.dumps({'junctions':joins,'purpose':'Solid volume spanning short gaps between the measured front blocks. Four reference sparks are explicitly excluded.','limits':'Inferred hidden structure; no mechanical strength or rigid-body balance claim.'},indent=2))
