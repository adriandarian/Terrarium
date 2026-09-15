import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene
assert Path(s.get('terrarium_project',''))==r and s['asset_name']=='Brambit'
cores=[o for o in s.objects if o.get('construction_part','').startswith('Rounded')]
assert len(cores)==4
core_trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in cores]
rows=[]
for ob in [o for o in s.objects if o.get('construction_part') and o.get('surface_following_bark')]:
 side=ob.get('bark_side',0);axis=0 if side else 1;sign=side or 1;samples=[]
 for face in ob.data.polygons:
  if face.normal[axis]*sign<.99999:continue
  p=ob.matrix_world@face.center;start=p.copy();start[axis]=sign*2;direction=Vector((0,0,0));direction[axis]=-sign
  hits=[tree.ray_cast(start,direction) for tree in core_trees];hits=[h for h in hits if h[0] is not None]
  assert hits,ob.name
  hit=min(hits,key=lambda h:h[3])[0];relief=(p[axis]-hit[axis])*sign
  assert abs(relief-ob['bark_relief_m'])<.000002,(ob.name,list(p),relief)
  samples.append(relief)
 assert samples,ob.name
 rows.append({'patch':ob.name,'side':side,'outward_face_samples':len(samples),'minimum_relief_m':min(samples),'maximum_relief_m':max(samples)})
assert len(rows)==44 and sum(row['side']!=0 for row in rows)==30
result={'source_blend_sha256':hashlib.sha256((r/'SourceAssets/Blender/Brambit/Brambit.blend').read_bytes()).hexdigest(),'patches':rows,'samples':sum(row['outward_face_samples'] for row in rows),'maximum_relief_m':max(row['maximum_relief_m'] for row in rows),'line_faces_removed':s.objects['Joined body face and feet'].get('numerical_cleanup_line_faces',0),'method':'Each outward patch face center is compared with the nearest ray hit on the four original closed body sections, without bevels.','limits':'Physical envelope conformity of 44 authored bark regions. Does not prove concept colors, visible boundary layout or final character fidelity.'}
(r/'Docs/BlenderRebuild/Brambit/bark-envelope-verification.json').write_text(json.dumps(result,indent=2))
