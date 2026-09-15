"""Read actual export geometry for independent imported-height comparisons."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('C:/Users/hello/Projects/Terrarium');reports=[]
assert Path(bpy.context.scene.get('terrarium_project',''))==root
for key in ['TrailTerrain','TrailPatch']:
    s=bpy.data.scenes['Terrarium_'+key];ob=next(o for o in s.objects if o.name=='SM_Blender_'+key);me=ob.data
    tree=BVHTree.FromPolygons([v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);samples=[]
    for part in [o for o in s.objects if o.get('part','').startswith('Source paver')][::11]:
        top=[v.co for v in part.data.vertices if abs(v.co.z-.009)<1e-5];center=sum(top,Vector())/len(top)
        hit=tree.ray_cast(Vector((center.x,center.y,.1)),Vector((0,0,-1)),1)
        assert hit[0] is not None and abs(hit[0].z-.009)<1e-5
        samples.append({'kind':'paver','local_xy_cm':[center.x*100,center.y*100],'expected_z_cm':hit[0].z*100})
    soils=[]
    for x in [-.9,-.6,-.3,0,.3,.6,.9]:
        for y in [-.8,-.4,0,.4,.8]:
            hit=tree.ray_cast(Vector((x,y,.1)),Vector((0,0,-1)),1)
            if hit[0] is not None and abs(hit[0].z+.002)<1e-5:soils.append({'kind':'soil','local_xy_cm':[x*100,y*100],'expected_z_cm':hit[0].z*100})
    samples+=soils[::max(1,len(soils)//12)];assert len(samples)>20
    (root/'Docs/BlenderRebuild'/key/'collision-samples.json').write_text(json.dumps({'asset':key,'method':'Ray samples from the actual merged Blender export mesh; source XY is recorded before FBX coordinate conversion.','samples':samples},indent=2));reports.append({'asset':key,'samples':len(samples)})
result={'assets':reports}
