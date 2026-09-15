"""Verify bearing samples inside actual closed Blender parts under live UE transforms."""
import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
root=Path('C:/Users/hello/Projects/Terrarium');assert Path(bpy.context.scene.get('terrarium_project',''))==root
folder=root/'Docs/BlenderRebuild/BridgeThreshold';r=json.loads((folder/'clearance-inspection.json').read_text())
def frame(t):
    x,y,z,w=t['rotation_xyzw'];return Matrix.Translation(Vector(t['translation']))@Quaternion((w,x,y,z)).to_matrix().to_4x4()@Matrix.Diagonal((*t['scale'],1))@Matrix.Diagonal((100,-100,100,1))
threshold=frame(r['threshold_transform']);bridge=frame(r['bridge_transform'])
scene=bpy.data.scenes['Terrarium_BridgeThreshold'];dg=bpy.context.evaluated_depsgraph_get()
cache={}
def tree(ob):
    if ob not in cache:
        # Each authoring object carries the same mesh/modifiers used by export.
        ev=ob.evaluated_get(dg);me=ev.to_mesh();cache[ob]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
    return cache[ob]
def interior(ob,point):
    nearest=tree(ob).find_nearest(point)
    return nearest[0] is not None and (point-nearest[0]).dot(nearest[1])<-.0001
core=next(o for o in bpy.data.scenes['Terrarium_CliffColumn'].objects if o.get('part')=='Solid cliff core')
bridge_beams=[o for o in bpy.data.scenes['Terrarium_RiverBridge'].objects if o.get('part')=='Under-deck beam'];assert len(bridge_beams)==2
checks=[]
for runner,(xb,xd) in enumerate([(.26,-.53),(.84,.74)]):
    y=.40;x=xd+(xb-xd)*(y+.43)/.86;point=Vector((x,y,-.121))
    ob=next(o for o in scene.objects if o.get('part')=='Bearing runner %d segment 2'%(runner+1));assert interior(ob,point)
    world=threshold@point;matches=[]
    for row in r['nearby_cliffs']:
        local=frame(row['transform']).inverted()@world
        if interior(core,local):matches.append({'component':row['component'],'index':row['index']})
    assert matches,('runner has no solid bank bearing',runner,list(world))
    checks.append({'kind':'bank_runner','runner':runner+1,'sample_world_cm':list(world),'inside_runner':True,'inside_live_cliff_cores':matches})
cross=next(o for o in scene.objects if o.get('part')=='Bridge beam bearing crosspiece')
for side in [-1,1]:
    point=Vector((side*.993,-.37,-.20));assert interior(cross,point);world=threshold@point;local=bridge.inverted()@world
    matches=[o.name for o in bridge_beams if interior(o,local)];assert matches,('crosspiece misses bridge beam',side,list(local))
    checks.append({'kind':'bridge_crosspiece','sample_world_cm':list(world),'inside_crosspiece':True,'inside_bridge_beams':matches})
# Independent expected-height probes from the merged export, including the ramp.
merged=scene.objects['SM_Blender_BridgeThreshold'];samples=[]
for y in [-.35,-.29,-.23,-.15,-.05,.05,.15,.25,.35]:
    left=-.8+.8*(y+.39)/.78
    for x in [left+.18,(left+1)/2,.82]:
        hit=tree(merged).ray_cast(Vector((x,y,.2)),Vector((0,0,-1)),1);assert hit[0] is not None
        samples.append({'blender_xy_cm':[x*100,y*100],'height_cm':hit[0].z*100})
(folder/'bearing-verification.json').write_text(json.dumps({'method':'Nearest oriented surface on individually closed Blender bearing parts; sample points are transformed using current Unreal placements, including FBX Y conversion.','checks':checks,'all_four_bearings_verified':True,'limits':'Four interior contact samples prove geometric intersections at bearings, not structural engineering, gameplay traversal or complete surface contact.'},indent=2))
(folder/'collision-samples.json').write_text(json.dumps({'source':'Actual evaluated merged Blender mesh','samples':samples},indent=2))
result={'bearing_checks':len(checks),'surface_samples':len(samples)}
