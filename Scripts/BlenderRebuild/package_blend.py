"""Make an isolated exported scene open normally as an editable Blender project.

Run only in a fresh background Blender with --factory-startup, then -- <key>.
No geometry or texture changes are made. The input is already authorized output.
"""
import bpy,sys,json,hashlib,shutil
from pathlib import Path
assert bpy.app.background and not bpy.data.filepath
root=Path(__file__).resolve().parents[2];key=sys.argv[sys.argv.index('--')+1];assert key.isalnum()
source=root/'SourceAssets/Blender'/key/(key+'.blend');out=root/'Docs/BlenderRebuild'/key
before_hash=hashlib.sha256(source.read_bytes()).hexdigest()
copy=root/'Saved/BlenderRebuild/packaging'/(key+'_'+before_hash[:16]+'.blend');copy.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,copy)
assert source.read_bytes()==copy.read_bytes()
factory_scenes=list(bpy.data.scenes);factory_objects=list(bpy.data.objects)
with bpy.data.libraries.load(str(copy),link=False) as (data_from,data_to):
    assert data_from.scenes==['Terrarium_'+key],data_from.scenes
    data_to.scenes=data_from.scenes
scene=data_to.scenes[0];assert Path(scene.get('terrarium_project',''))==root
bpy.context.window.scene=scene
bpy.data.batch_remove(ids=factory_objects)
for old in factory_scenes:bpy.data.scenes.remove(old)
assert len(bpy.data.scenes)==1 and scene.camera
expected=json.loads((out/'mesh-validation.json').read_text())
parts=[o for o in scene.objects if o.get('part')];assert len(parts)==expected['parts']
images={n.image for o in parts for m in o.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
expected_images=sum(Path(name).suffix=='.png' for name in expected['files'])
assert len(images)==expected_images and all(i.packed_file for i in images),[(i.name,bool(i.packed_file),i.filepath) for i in images]
assert scene.library is None and all(o.library is None for o in scene.objects) and all(i.library is None for i in images)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
(out/'project-packaging.json').write_text(json.dumps({'asset':key,'method':'isolated scene library appended to fresh Blender and saved as a normal project','previous_sha256':before_hash,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scene':scene.name,'parts':len(parts),'packed_images':len(images),'active_camera':scene.camera.name,'geometry_changed':False,'reopen_verification_pending':True},indent=2))
print('PACKAGED_NORMAL_BLEND '+key,flush=True)
