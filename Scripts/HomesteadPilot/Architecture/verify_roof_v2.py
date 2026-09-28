import bpy,json,hashlib,struct
from pathlib import Path
ROOT=Path('C:/Users/hello/Projects/Terrarium');DOC=ROOT/'Docs/HomesteadPilot/Architecture/RoofRepairV2';r=json.loads((DOC/'manifest.json').read_text());s=bpy.context.scene
assert bpy.app.background and s.name==r['scene'] and Path(s['terrarium_project'])==ROOT and len(bpy.data.scenes)==1
h=hashlib.sha256()
for o in sorted([o for o in s.objects if o.get('asset')=='Cottage' and o.get('lod')==0],key=lambda o:o.get('part','')):
    for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
    for uv in o.data.uv_layers.active.data:h.update(struct.pack('<2f',*uv.uv))
assert h.hexdigest()==r['lod0_geometry_uv_fingerprint']
assert hashlib.sha256(Path(r['original_source']).read_bytes()).hexdigest()==r['original_source_sha256']
checks=[]
for repair in r['repairs']:
    obs=[o for o in s.objects if o.get('asset')=='Cottage' and o.get('lod')==repair['level']];points=[v.co for o in obs for v in o.data.vertices]
    dims=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
    assert all(abs(a-b)<.00001 for a,b in zip(dims,repair['dimensions_m']))
    roof=next(o for o in obs if o['part']=='RoofTiles');vertices=list(roof.data.vertices)
    for i in range(0,len(vertices),8):
        depth=max(v.co.z for v in vertices[i:i+8])-min(v.co.z for v in vertices[i:i+8])
        assert min(abs(depth-repair['roof_thickness_m']),abs(depth-repair['cross_gable_thickness_m']))<.00001
    checks.append({'lod':repair['level'],'source_dimensions_m':dims,'roof_thickness_verified':True,'uvs_present':all(o.data.uv_layers.active is not None for o in obs)})
verify=bpy.data.scenes.new('RoofV2Roundtrip');verify.unit_settings.system='METRIC';verify.unit_settings.scale_length=1;bpy.context.window.scene=verify
for repair,check in zip(r['repairs'],checks):
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=repair['fbx']);added=set(bpy.data.objects)-before;o=next(o for o in added if o.type=='MESH');bpy.context.view_layer.update()
    dims=list(o.dimensions);assert all(abs(a-b)<.0001 for a,b in zip(dims,repair['dimensions_m']))
    assert len(o.material_slots)==8 and o.data.uv_layers.active
    check['fbx_roundtrip_dimensions_m']=dims;check['fbx_8_slots_uvs_pass']=True;bpy.data.batch_remove(ids=list(added))
result={'normal_source_reopened':True,'original_source_unchanged':True,'lod0_geometry_uv_unchanged':True,'repaired_lods':checks,'limits':'Source and exported static mesh validation. Root owns Unreal import, forcedLOD screenshots and automatic distance-transition validation.'}
(DOC/'verification.json').write_text(json.dumps(result,indent=2));print('ROOF_V2_REOPEN_ROUNDTRIP_PASS',flush=True)
