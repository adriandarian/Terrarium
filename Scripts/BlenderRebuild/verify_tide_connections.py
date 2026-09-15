"""Check real shared interior points between the Grove's evaluated solid blocks."""
import bpy,json,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene
assert s.get('terrarium_project')==str(root) and s['asset_name']=='Tide'
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in s.objects:
    if not ob.get('part'):continue
    ev=ob.evaluated_get(dg);me=ev.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices]
    tree=BVHTree.FromPolygons(vs,[list(p.vertices) for p in me.polygons])
    rows.append((ob,tree,Vector([min(v[i] for v in vs) for i in range(3)]),Vector([max(v[i] for v in vs) for i in range(3)])))
    ev.to_mesh_clear()
parent=list(range(len(rows)));edges=[]
def find(i):
    while parent[i]!=i:i=parent[i]
    return i
for i,(a,ta,amin,amax) in enumerate(rows):
    for j in range(i):
        b,tb,bmin,bmax=rows[j];lo=Vector([max(amin[k],bmin[k]) for k in range(3)]);hi=Vector([min(amax[k],bmax[k]) for k in range(3)])
        if any(hi[k]-lo[k]<1e-6 for k in range(3)):continue
        point=(lo+hi)/2
        # Every authored part here is a convex beveled box. Its nearest surface
        # normal provides an inside/outside test at this shared candidate point.
        interior=True
        for tree in [ta,tb]:
            p,n,_,distance=tree.find_nearest(point)
            if p is None or (point-p).dot(n)>-1e-7:interior=False;break
        if interior:parent[find(i)]=find(j);edges.append([a.name,b.name])
groups={}
for i,row in enumerate(rows):groups.setdefault(find(i),[]).append(row[0].name)
result={'parts':len(rows),'connected_components':len(groups),'shared_interior_connections':len(edges),'groups':list(groups.values()),'method':'Shared AABB-center point is strictly inside both evaluated convex beveled boxes. Each accepted link therefore has overlapping solid interior.','limits':'Does not establish mechanical strength, single watertight union, collision or gameplay.'}
(root/'Docs/BlenderRebuild/Tide/connection-verification.json').write_text(json.dumps(result,indent=2))
result={k:result[k] for k in ['parts','connected_components','shared_interior_connections','groups']}
