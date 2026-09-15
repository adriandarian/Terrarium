import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;r=Path('C:/Users/hello/Projects/Terrarium')
assert Path(s.get('terrarium_project',''))==r and s['asset_name']=='Brambit'
components=[]
for o in [q for q in s.objects if q.get('part')]:
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 unseen=set(bm.verts);counts=[]
 while unseen:
  pending=[unseen.pop()];count=0
  while pending:
   v=pending.pop();count+=1
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in unseen:unseen.remove(w);pending.append(w)
  counts.append(count)
 bm.free();ev.to_mesh_clear()
 assert len(counts)==1,(o.name,counts)
 components.append({'part':o.name,'connected_components':len(counts)})
rows=[]
for ob in s.objects:
 if ob.get('construction_part','')=='Bark edge bump':
  vs=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  p=Vector((min(v.x for v in vs)+.001,min(v.y for v in vs)+.001,max(v.z for v in vs)-.001))
  uv=world_to_camera_view(s,s.camera,p);actual=[uv.x*1254,(1-uv.y)*1254];target=list(ob['reference_corner'])
  error=sum((x-y)**2 for x,y in zip(actual,target))**.5
  assert error<.01,(target,actual,error)
  rows.append({'reference_corner_px':target,'projected_corner_px':actual,'error_pixels':error})
assert len(rows)==4
result={'source_blend_sha256':hashlib.sha256((r/'SourceAssets/Blender/Brambit/Brambit.blend').read_bytes()).hexdigest(),'connected_sections':components,'burrs':rows,'limits':'Four manually read visible front corners, not full silhouette or overall fidelity. Each of five evaluated sections is a single connected surface.'}
(r/'Docs/BlenderRebuild/Brambit/front-burr-verification.json').write_text(json.dumps(result,indent=2))
