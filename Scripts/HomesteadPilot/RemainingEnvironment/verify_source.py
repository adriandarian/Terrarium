"""Independently reopen source, then import exported FBX into another scene."""
import bpy,bmesh,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
DOC=ROOT/'Docs/HomesteadPilot/RemainingEnvironment'
asset=json.loads((DOC/'manifest.json').read_text())['assets'][0]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/asset['blend_path']),load_ui=False)
assert Path(bpy.context.scene['terrarium_project']).resolve()==ROOT
def inspect(ob):
    me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
    row={'triangles':len(me.loop_triangles),'vertices':len(me.vertices),
         'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
         'volume_m3':bm.calc_volume(signed=True),'dimensions_m':list(ob.dimensions),'uv_layers':len(me.uv_layers)}
    bm.free()
    assert row['triangles']==12 and row['boundary_edges']==0 and row['nonmanifold_edges']==0 and row['volume_m3']>0
    assert max(abs(a-b) for a,b in zip(row['dimensions_m'],asset['dimensions_m']))<.00001
    return row
source=inspect(next(o for o in bpy.context.scene.objects if o.type=='MESH'))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/asset['fbx']))
export=inspect(next(o for o in bpy.context.scene.objects if o.type=='MESH'))
assert hashlib.sha256((ROOT/asset['fbx']).read_bytes()).hexdigest()==asset['fbx_sha256']
(DOC/'source-validation.json').write_text(json.dumps({'source_reopened':True,'fbx_reimported':True,'source':source,'fbx':export,
 'scope':'Source geometry only. Unreal compile, appearance and animation remain coordinator checks.'},indent=2))
print('REMAINING_ENVIRONMENT_SOURCE_VERIFIED')
