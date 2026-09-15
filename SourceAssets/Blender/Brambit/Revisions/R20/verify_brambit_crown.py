import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;r=Path('C:/Users/hello/Projects/Terrarium')
assert Path(s.get('terrarium_project',''))==r and s['asset_name']=='Brambit'
rows=[]
for ob in s.objects:
 if not ob.get('construction_part') or 'crown_reference_corner' not in ob:continue
 vs=[ob.matrix_world@Vector(v) for v in ob.bound_box]
 corner=Vector((min(v.x for v in vs)+.001,min(v.y for v in vs)+.001,max(v.z for v in vs)-.001))
 uv=world_to_camera_view(s,s.camera,corner);actual=[1254*uv.x,1254*(1-uv.y)];target=list(ob['crown_reference_corner'])
 error=math.dist(actual,target);assert error<.01
 rows.append({'reference_corner_px':target,'projected_corner_px':actual,'error_pixels':error,'palette_index':ob['palette_index']})
assert len(rows)==9 and sum(x['palette_index']==15 for x in rows)==2 and sum(x['palette_index']<8 for x in rows)==1
result={'source_blend_sha256':hashlib.sha256((r/'SourceAssets/Blender/Brambit/Brambit.blend').read_bytes()).hexdigest(),'courses':rows,'limits':'Nine manually read crown-course corners, including two saddle-brown blocks, their green neighbor and a rear ridge block. This only verifies intended construction placement, not full surface visibility or overall likeness.'}
(r/'Docs/BlenderRebuild/Brambit/front-crown-verification.json').write_text(json.dumps(result,indent=2))
