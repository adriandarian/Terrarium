"""Package or independently reopen the isolated material-library project."""
import bpy,sys,json,hashlib,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2];source=root/'SourceAssets/Blender/SurfaceLibrary/SurfaceLibrary.blend'
assert bpy.app.background
if not bpy.data.filepath:
    original=list(bpy.data.scenes);objects=list(bpy.data.objects)
    copy=root/'Saved/BlenderRebuild/packaging/SurfaceLibrary_source.blend';copy.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,copy)
    with bpy.data.libraries.load(str(copy),link=False) as (src,dst):dst.scenes=['Terrarium_SurfaceLibrary']
    bpy.context.window.scene=dst.scenes[0]
    bpy.data.batch_remove(ids=objects)
    for scene in original:bpy.data.scenes.remove(scene)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
else:
    s=bpy.context.scene;assert s.name=='Terrarium_SurfaceLibrary' and len(bpy.data.scenes)==1
    assert Path(s['terrarium_project'])==root
    meshes=[o for o in s.objects if o.type=='MESH'];assert len(meshes)==45
    mats={o.data.materials[0] for o in meshes};assert len(mats)==45
    images={n.image for m in mats for n in m.node_tree.nodes if n.type=='TEX_IMAGE'}
    assert len(images)==45 and all(i.packed_file for i in images)
    assert all(len(o.data.polygons)==6 and o.data.uv_layers for o in meshes)
    (root/'Docs/BlenderRebuild/SurfaceLibrary/saved-blend-verification.json').write_text(json.dumps({'direct_project_open_in_independent_process':True,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'materials':45,'packed_images':45,'closed_sample_slabs':45},indent=2))
    print('SURFACE_LIBRARY_VERIFIED')
