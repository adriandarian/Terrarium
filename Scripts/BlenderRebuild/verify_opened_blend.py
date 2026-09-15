"""Check the file Blender actually opened in an independent background process."""
import bpy,json,hashlib
from pathlib import Path
assert bpy.app.background
source=Path(bpy.data.filepath);key=source.stem;root=Path(__file__).resolve().parents[2]
assert source==root/'SourceAssets/Blender'/key/(key+'.blend')
out=root/'Docs/BlenderRebuild'/key;expected=json.loads((out/'mesh-validation.json').read_text())
scene=bpy.context.scene;assert scene.name=='Terrarium_'+key and len(bpy.data.scenes)==1
assert Path(scene.get('terrarium_project',''))==root and scene.camera
parts=[o for o in scene.objects if o.get('part')];assert len(parts)==expected['parts']
images={n.image for o in parts for m in o.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
expected_images=sum(Path(name).suffix=='.png' for name in expected['files'])
assert len(images)==expected_images and all(i.packed_file for i in images)
mesh=next(o for o in scene.objects if o.name=='SM_Blender_'+key)
assert len(mesh.data.materials)==expected['material_slots'] and len(mesh.data.uv_layers)==expected['uv_layers']
mesh.data.calc_loop_triangles();assert len(mesh.data.loop_triangles)==expected['triangles']
result={'asset':key,'direct_project_open_in_independent_process':True,'active_scene':scene.name,'parts':len(parts),'packed_images':len(images),'material_slots':len(mesh.data.materials),'triangles':len(mesh.data.loop_triangles),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'active_camera':scene.camera.name}
(out/'saved-blend-verification.json').write_text(json.dumps(result,indent=2))
print('VERIFIED_NORMAL_BLEND '+key,flush=True)
