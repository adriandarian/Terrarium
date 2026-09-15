"""Check actual evaluated shell/cavity geometry, not the authoring recipe."""
import bpy,json,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene
assert Path(s.get('terrarium_project',''))==root and s['asset_name']=='MossTonic'
dg=bpy.context.evaluated_depsgraph_get()
parts={o['part']:o for o in s.objects if o.get('part')}
def tree(ob):
    ev=ob.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
    assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
    bvh=BVHTree.FromBMesh(bm);bm.free();ev.to_mesh_clear();return bvh
shell=tree(parts['Continuous hollow glass bottle']);liquid=tree(parts['Contained teal tonic with level surface'])
def inside(bvh,p):
    ray=Vector((.913,.277,.307)).normalized();point=Vector(p);count=0
    for _ in range(100):
        hit=bvh.ray_cast(point,ray)
        if hit[0] is None:return bool(count%2)
        point=hit[0]+ray*1e-5;count+=1
    raise AssertionError('Ray did not leave closed object')
tests=[('solid bottom',(0,0,.033),True,False),('liquid filled cavity',(0,0,.3),False,True),('empty neck cavity',(0,0,.65),False,False),('body side wall',(.222,0,.3),True,False),('open mouth',(0,0,.735),False,False),('outside bottle',(.30,0,.3),False,False)]
rows=[]
for label,p,wall,fluid in tests:
    result_pair=[inside(shell,p),inside(liquid,p)];assert result_pair==[wall,fluid],(label,result_pair)
    rows.append({'probe':label,'point_m':p,'inside_glass':wall,'inside_liquid':fluid,'passed':True})
result={'actual_evaluated_geometry':True,'volume_probes':rows,'limits':'Sampled cavity and wall membership. No liquid simulation or exhaustive self-intersection certification.'}
(root/'Docs/BlenderRebuild/MossTonic/physical-volume-verification.json').write_text(json.dumps(result,indent=2))
