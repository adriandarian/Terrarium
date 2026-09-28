"""Read/reopen finished pilot sources in a disposable background Blender."""
import bpy,bmesh,json,sys
from pathlib import Path
ROOT=Path('C:/Users/hello/Projects/Terrarium')
folder=ROOT/'SourceAssets/Blender/HomesteadPilot/Landscape'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
manifest_path=ROOT/args[0] if args else folder/'manifest.json'
output=ROOT/args[1] if len(args)>1 else ROOT/'Docs/HomesteadPilot/Landscape/reopen-validation.json'
manifest=json.loads(manifest_path.read_text())
rows=[]
for asset in manifest['assets']:
    path=ROOT/asset['blend_path']
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    assert Path(bpy.context.scene.get('terrarium_project','')).resolve()==ROOT.resolve()
    ob=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
    row={'name':asset['name'],'reopened':True,'scene':bpy.context.scene.name,
        'triangles':len(me.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),
        'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
        'signed_volume_m3':bm.calc_volume(signed=True),'uv_layers':len(me.uv_layers),
        'material_slots':len(me.materials),'packed_image_count':sum(bool(i.packed_file) for i in bpy.data.images),
        'files_present':all((ROOT/asset[k]).is_file() for k in ('fbx_path','blend_path','preview_path'))}
    bm.free();assert row['triangles']==asset['triangles'] and row['files_present']
    assert row['boundary_edges']==0 and row['signed_volume_m3']>0
    rows.append(row)
output.write_text(json.dumps({'assets':rows,'status':'sources reopened and geometry inspected; Unreal validation remains separate'},indent=2))
print('LANDSCAPE_REOPEN_VALIDATED '+str(len(rows)))
