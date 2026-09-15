"""Positive interior witnesses for Storm's concave meshes and block joins.

An edge requires a sample at least 0.2 mm inside both evaluated closed parts.
This proves a volume overlap; absence of a witness is inconclusive.
"""
import bpy, itertools
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def shape(ob, shift=None):
    shift=Vector(shift or (0,0,0))
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
    vertices=[ob.matrix_world@v.co+shift for v in me.vertices]
    polygons=[tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    return {'tree':BVHTree.FromPolygons(vertices,polygons),
            'lo':Vector([min(v[i] for v in vertices) for i in range(3)]),
            'hi':Vector([max(v[i] for v in vertices) for i in range(3)])}

def interior(s,p):
    hit=s['tree'].find_nearest(p)
    if hit[0] is None or hit[3]<.0002:return False
    # Consistent outward normals are supplied by each closed mesh authoring helper.
    if (p-hit[0]).dot(hit[1])>=-.0002:return False
    # Independent parity checks avoid trusting the nearest normal around a
    # concave corner. Non-axis directions avoid most triangle/edge coincidences.
    for raw in ((1,.173,.319),(.217,1,.413),(.391,.127,1)):
        direction=Vector(raw).normalized();origin=p.copy();count=0
        for _ in range(100):
            cast=s['tree'].ray_cast(origin,direction)
            if cast[0] is None:break
            count+=1;origin=cast[0]+direction*.000001
        else:return False
        if count%2!=1:return False
    return True

def witness(a,b):
    lo=Vector([max(a['lo'][i],b['lo'][i]) for i in range(3)])
    hi=Vector([min(a['hi'][i],b['hi'][i]) for i in range(3)])
    if min(hi-lo)<.0005:return None
    for fractions in itertools.product((.5,.2,.8,.05,.95),repeat=3):
        p=Vector([lo[i]+fractions[i]*(hi[i]-lo[i]) for i in range(3)])
        if interior(a,p) and interior(b,p):return list(p)
    return None

def inspect(parts):
    shapes={o.name:shape(o) for o in parts};edges=[];adj={o.name:set() for o in parts}
    for a,b in itertools.combinations(parts,2):
        p=witness(shapes[a.name],shapes[b.name])
        if p is not None:
            edges.append({'a':a.name,'b':b.name,'interior_witness_m':p})
            adj[a.name].add(b.name);adj[b.name].add(a.name)
    remaining=set(adj);components=[]
    while remaining:
        pending=[min(remaining)];component=set()
        while pending:
            name=pending.pop()
            if name in component:continue
            component.add(name);pending.extend(adj[name]-component)
        remaining-=component;components.append(sorted(component))
    return {'method':'Evaluated surface nearest-normal interior test plus three-direction odd ray parity; witness at least 0.2 mm from both boundaries. Missing edges are inconclusive. Individually closed outward meshes are required.','edges':edges,'components':components}
