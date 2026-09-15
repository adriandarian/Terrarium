"""Fill bounded interior space between the flame's authored solid columns."""
import bpy,math,json
from mathutils import Vector

def fill_body(asset,pigments,course=.084):
    bpy.context.view_layer.update();original=[o for o in asset.parts if not o.get('detached_reference_feature')]
    from ember_core_guard import make_core_guard
    occludes_core=make_core_guard(original)
    boxes=[]
    for o in original:
        vs=[o.matrix_world@Vector(v) for v in o.bound_box]
        boxes.append(([min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def hull(points):
        p=sorted(set(points));lower=[];upper=[]
        for point in p:
            while len(lower)>1 and cross(lower[-2],lower[-1],point)<=0:lower.pop()
            lower.append(point)
        for point in reversed(p):
            while len(upper)>1 and cross(upper[-2],upper[-1],point)<=0:upper.pop()
            upper.append(point)
        return lower[:-1]+upper[:-1]
    def inside(p,h):return all(cross(a,b,p)>=1e-6 for a,b in zip(h,h[1:]+h[:1]))
    az=math.radians(45);el=math.radians(25);unit=.0012
    def projection_ok(p):
        u=627+(math.cos(az)*p[0]-math.sin(az)*p[1])/unit
        v=1160-(math.sin(el)*math.sin(az)*p[0]+math.sin(el)*math.cos(az)*p[1]+math.cos(el)*p[2])/unit
        x=int(u/1254*314);y=int(v/1254*314)
        return 1<=x<313 and 1<=y<313 and all(pigments[py][px] is not None for py in range(y-1,y+2) for px in range(x-1,x+2))
    step=.07;half=(step+.004)/2;created=[]
    for k in range(math.ceil(max(hi[2] for lo,hi in boxes)/course)):
        z=k*course+course/2;active=[(lo,hi) for lo,hi in boxes if lo[2]<=z<=hi[2]]
        if not active:continue
        h=hull([(x,y) for lo,hi in active for x in [lo[0],hi[0]] for y in [lo[1],hi[1]]])
        if len(h)<3:continue
        for ix in range(math.floor(min(p[0] for p in h)/step),math.ceil(max(p[0] for p in h)/step)):
            for iy in range(math.floor(min(p[1] for p in h)/step),math.ceil(max(p[1] for p in h)/step)):
                x=(ix+.5)*step;y=(iy+.5)*step
                if not all(inside((x+dx,y+dy),h) for dx in [-half,half] for dy in [-half,half]):continue
                if any(lo[0]<=x<=hi[0] and lo[1]<=y<=hi[1] for lo,hi in active):continue
                if occludes_core((x,y,z),(step+.004,step+.004,course+.004)):continue
                if not all(projection_ok((x+dx,y+dy,z+dz)) for dx in [-half,0,half] for dy in [-half,0,half] for dz in [-course/2,0,course/2]):continue
                pu=627+(math.cos(az)*x-math.sin(az)*(y-half))/unit
                pv=1160-(math.sin(el)*math.sin(az)*x+math.sin(el)*math.cos(az)*(y-half)+math.cos(el)*z)/unit
                index=pigments[int(pv/1254*314)][int(pu/1254*314)]
                assert index is not None
                index=min(index,4)  # Keep cream confined to measured core cubes.
                ob=asset.box('Solid flame interior',(x,y,z),(step+.004,step+.004,course+.004),index,.004)
                ob['inferred_interior']=True;ob['palette_index']=index;ob['course']=k;ob['bulk_fill']=True
                created.append({'part':ob.name,'center_m':[x,y,z],'dimensions_m':[step+.004,step+.004,course+.004]})
    (asset.review/'bulk-interior.json').write_text(json.dumps({'cells':created,'method':'Interior cubes lie within per-course hulls of existing columns; 27 projected samples per candidate remain inside the reference silhouette. Sparks excluded.','limits':'Inferred interior volume, not a reconstruction of unseen reference surfaces.'},indent=2))
