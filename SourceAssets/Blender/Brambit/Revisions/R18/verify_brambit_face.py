"""Check face-course depth on the saved, evaluated physical body."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene
assert Path(s.get('terrarium_project',''))==r and s['asset_name']=='Brambit'
source=r/'SourceAssets/Blender/Brambit/Brambit.blend'
tree=BVHTree.FromObject(s.objects['Joined body face and feet'],bpy.context.evaluated_depsgraph_get())
rows=[];planes=[];bark_index=0
for ob in s.objects:
    name=ob.get('construction_part','')
    if name not in ['Front bark course','Forehead brown peak','Tan belly step']:continue
    vertices=[ob.matrix_world@v.co for v in ob.data.vertices]
    plane=min(v.y for v in vertices)
    expected=-.2933 if name=='Forehead brown peak' else -.293
    assert abs(plane-expected)<.000002
    planes.append({'object':ob.name,'front_plane_m':plane,'offset_from_tan_face_m':-.292-plane})
    if name=='Front bark course':
        index=bark_index;bark_index+=1
        # These centers are intentionally occluded by the separate projecting
        # burrs. Their construction-plane checks remain in the receipt.
        if index in [11,14,16]:continue
    point=Vector(tuple((min(v[i] for v in vertices)+max(v[i] for v in vertices))/2 for i in range(3)))
    point.y=-2
    hit=tree.ray_cast(point,Vector((0,1,0)))
    assert hit[0] is not None
    offset=-.292-hit[0].y
    assert .000998<=offset<=.001302,(ob.name,offset)
    rows.append({'object':ob.name,'probe_xz_m':[point.x,point.z],'surface_y_m':hit[0].y,'offset_from_tan_face_m':offset})
assert bark_index==18 and len(planes)==22 and len(rows)==19
result={'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'construction_planes':planes,'evaluated_surface_samples':rows,'maximum_sampled_offset_m':max(row['offset_from_tan_face_m'] for row in rows),'method':'Compare the 22 authored front planes and ray-cast 19 unobstructed course centers against the evaluated joined body. Three bark centers behind projecting burrs are excluded from the ray test.','limits':'Measured front depths only. Does not establish reference color, seam layout, full surface continuity or concept fidelity.'}
(r/'Docs/BlenderRebuild/Brambit/face-depth-verification.json').write_text(json.dumps(result,indent=2))
