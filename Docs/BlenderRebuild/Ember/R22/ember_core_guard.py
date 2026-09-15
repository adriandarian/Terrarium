"""Keep inferred fill behind the measured cream cubes in the reference view."""
import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def make_core_guard(parts):
    deps=bpy.context.evaluated_depsgraph_get();verts=[];faces=[]
    for ob in parts:
        if not ob.get('reference_rect') or ob.get('palette_index',0)<6:continue
        ev=ob.evaluated_get(deps);me=ev.to_mesh();start=len(verts)
        verts.extend(ob.matrix_world@v.co for v in me.vertices)
        faces.extend([start+i for i in p.vertices] for p in me.polygons);ev.to_mesh_clear()
    assert faces
    tree=BVHTree.FromPolygons(verts,faces)
    az=math.radians(45);el=math.radians(25)
    eye=Vector((-math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))
    def occludes(center,size):
        c=Vector(center)
        for x in [-.5,0,.5]:
            for y in [-.5,0,.5]:
                for z in [-.5,0,.5]:
                    point=c+Vector((size[0]*x,size[1]*y,size[2]*z))
                    hit,normal,index,distance=tree.ray_cast(point+eye*3,-eye,6)
                    if hit is not None and distance>3.0002:return True
        return False
    return occludes
