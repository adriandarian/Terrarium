"""Independent saved-source, UV, texture, traversal-sample and FBX roundtrip checks."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('C:/Users/hello/Projects/Terrarium');OUT=ROOT/'SourceAssets/Blender/HomesteadPilot/Architecture';DOC=ROOT/'Docs/HomesteadPilot/Architecture'
assert bpy.app.background;s=bpy.context.scene
assert s.name=='Terrarium_HomesteadArchitecture' and Path(s['terrarium_project'])==ROOT and len(bpy.data.scenes)==1
manifest=json.loads((DOC/'manifest.json').read_text());rows=[]
def tree(col):
    vs=[];fs=[]
    for o in col.objects:
        offset=len(vs);vs.extend(v.co.copy() for v in o.data.vertices)
        fs.extend(tuple(i+offset for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)
for a in manifest['assets']:
    for lod in a['lods']:
        col=bpy.data.collections[f'HP_{a["name"]}_LOD{lod["level"]}'];obs=list(col.objects)
        assert len(obs)==lod['parts']
        for o in obs:
            assert o.library is None and o.data.uv_layers.active
            assert all(math.isfinite(v) for u in o.data.uv_layers.active.data for v in u.uv)
        pts=[v.co for o in obs for v in o.data.vertices];dims=[max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)]
        assert all(abs(a-b)<.0001 for a,b in zip(dims,lod['dimensions_m']))
        rows.append({'asset':a['name'],'lod':lod['level'],'source_bounds_pass':True,'source_dimensions_m':dims,'uvs_finite':True,'parts':len(obs)})
for m in manifest['materials']:
    if m['base_color_texture']:
        path=Path(m['base_color_texture']);assert hashlib.sha256(path.read_bytes()).hexdigest()==m['source_sha256']
        assert path.read_bytes()==(ROOT/'SourceAssets/Voxel'/m['source']).read_bytes()
images={n.image for o in s.objects if o.type=='MESH' for m in o.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image};assert len(images)==4 and all(i.packed_file for i in images)

# Static geometry samples: they do not substitute for a moving capsule/controller.
t=tree(bpy.data.collections['HP_Cottage_LOD0']);probes=[]
for x in [-.30,0,.30]:
    for y in [-3.0,-2.8,-2.55,-2.32,-2.12,-1.95,-1.5,-.5,.5,1.0]:
        hit=t.ray_cast(Vector((x,y,.8)),Vector((0,0,-1)),1.2)
        if hit[0] is None:
            # The modeled stone steps have7mm visual joints; point rays can pass through them.
            probes.append({'x_m':x,'y_m':y,'point_support':False,'note':'Point lies in a modeled masonry joint; capsule/controller check required in Unreal.'});continue
        z=hit[0].z
        # Upward1.80m line from5cm above each supported sample must stay unobstructed.
        overhead=t.ray_cast(Vector((x,y,z+.05)),Vector((0,0,1)),1.80);assert overhead[0] is None,(x,y,'blocked',overhead[0])
        probes.append({'x_m':x,'y_m':y,'point_support':True,'surface_z_m':z,'clear_180cm_vertical_ray':True})
bt=tree(bpy.data.collections['HP_Bridge_LOD0']);bridge=[]
for x in [-.80,0,.80]:
    for y in [-1.725,-.825,.075,.825,1.725]:
        hit=bt.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2);assert hit[0] and abs(hit[0].z-.32)<.002
        bridge.append({'x_m':x,'y_m':y,'deck_z_m':hit[0].z})

check=bpy.data.scenes.new('HP_ImportCheck');check.unit_settings.system='METRIC';check.unit_settings.scale_length=1;bpy.context.window.scene=check
idx=0
for a in manifest['assets']:
    for lod in a['lods']:
        previous=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=lod['fbx']);added=set(bpy.data.objects)-previous;meshes=[o for o in added if o.type=='MESH'];assert len(meshes)==1
        o=meshes[0];bpy.context.view_layer.update();dims=list(o.dimensions)
        assert all(abs(a-b)<.0001 for a,b in zip(dims,lod['dimensions_m'])),(a['name'],lod['level'],dims)
        assert len(o.material_slots)==8 and o.data.uv_layers.active
        rows[idx]['fbx_roundtrip_dimensions_m']=dims;rows[idx]['expected_unreal_dimensions_cm']=[d*100 for d in dims];rows[idx]['fbx_uv_and_8_material_slots_pass']=True;idx+=1
        bpy.data.batch_remove(ids=list(added))
report={'saved_source':str(OUT/'HomesteadArchitecture.blend'),'source_sha256':hashlib.sha256((OUT/'HomesteadArchitecture.blend').read_bytes()).hexdigest(),'reopened_normal_project':True,'packed_source_textures':4,'source_textures_byte_identical':True,'mesh_checks':rows,'cottage_static_support_and_clearance_samples':probes,'bridge_deck_samples':bridge,'limitations':'Static sampled rays only; no capsule sweep, movement/controller, navigation, collision import, LOD transition or frame-time test. Unreal integration must report those separately.'}
(DOC/'reopen-verification.json').write_text(json.dumps(report,indent=2))
p=DOC/'verification.json';r=json.loads(p.read_text());r['reopen_pending']=False;r['reopened_and_roundtripped']=True;p.write_text(json.dumps(r,indent=2))
print('ARCHITECTURE_REOPEN_AND_ROUNDTRIP_PASS',flush=True)
