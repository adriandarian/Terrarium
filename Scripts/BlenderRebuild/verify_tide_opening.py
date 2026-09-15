"""Check reference-camera rays through the curl and neighboring solid blocks."""
import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
assert s['asset_name']=='Tide' and s.get('terrarium_project')=='C:\\Users\\hello\\Projects\\Terrarium'
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
cam=s.camera;rot=cam.matrix_world.to_3x3();direction=rot@Vector((0,0,-1));rows=[]
for u,v,expected in [(665,745,False),(680,790,False),(650,815,False),(610,125,True),(850,700,True),(550,1010,True)]:
    start=cam.location+rot@Vector(((u-627)*.0012,(627-v)*.0012,0))
    hit=s.ray_cast(dg,start,direction,distance=20)
    assert hit[0]==expected,(u,v,expected,hit)
    rows.append({'reference_pixel':[u,v],'local_start_m':list(start),'local_end_m':list(start+direction*20),'hits_solid':hit[0],'expected':expected,'part':hit[4].name if hit[0] else None})
result={'samples':rows,'method':'Rays through three reference curl-opening pixels and three neighboring solid blocks in evaluated Blender geometry. No transparency or alpha mask is used on the model.','limits':'Sampled opening verification only; not a complete collision or character-clearance test.'}
Path('C:/Users/hello/Projects/Terrarium/Docs/BlenderRebuild/Tide/opening-verification.json').write_text(json.dumps(result,indent=2))
