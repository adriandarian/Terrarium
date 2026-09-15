"""Inspect evaluated Storm joins and derive the actual lowest support edge."""
import bpy,bmesh,json,hashlib,sys,math
from mathutils import Vector
from pathlib import Path
ROOT=Path('C:/Users/hello/Projects/Terrarium')
assert Path(bpy.context.scene.get('terrarium_project',''))==ROOT
assert bpy.context.scene.get('asset_name')=='Storm'
sys.path.insert(0,str(ROOT/'Scripts/BlenderRebuild'))
from storm_structure import inspect
parts=[o for o in bpy.context.scene.objects if o.get('part')]
report=inspect(parts)
body={o.name for o in parts if not o.get('detached_reference_feature')}
sparks={o.name for o in parts if o.get('detached_reference_feature')}
assert len(parts)==53 and len(body)==43 and len(sparks)==10
assert sorted(map(len,report['components']))==[1]*10+[43]
assert any(set(c)==body for c in report['components'])
assert all(any(c==[name] for c in report['components']) for name in sparks)
path=ROOT/'SourceAssets/Blender/Storm/Storm.blend'
report.update(body_parts=len(body),detached_sparks=len(sparks),source_blend_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),limits='Connected overlapping closed solids, not a Boolean-unioned manifold or a rigid-body balance certification.')
out=ROOT/'Docs/BlenderRebuild/Storm'
(out/'connection-verification.json').write_text(json.dumps(report,indent=2))
core=bpy.context.scene.objects['Golden lightning body']
ev=core.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
bm=bmesh.new();bm.from_mesh(me)
assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
core_audit={'source_blend_sha256':report['source_blend_sha256'],'evaluated_closed':True,
            'evaluated_volume_m3':bm.calc_volume(signed=True),
            'control_bounds_x_m':[min(v.co.x for v in core.data.vertices),max(v.co.x for v in core.data.vertices)],
            'ridge_nodes':json.loads(core['inferred_back_ridge']),
            'limits':'The back is inferred from the longitudinal front structure; closure and volume do not establish concept fidelity.'}
bm.free();ev.to_mesh_clear()
(out/'core-volume-verification.json').write_text(json.dumps(core_audit,indent=2))
s=bpy.context.scene
camera_offset=s.camera.location-Vector(s['reference_focus'])
elevation=math.degrees(math.atan2(camera_offset.z,math.hypot(camera_offset.x,camera_offset.y)))
assert abs(elevation-30)<.0001
anchors=[]
for ob in parts:
    if 'reference_seam' not in ob:continue
    p=ob.matrix_world@ob.data.vertices[4].co
    u=627+(math.cos(math.pi/4)*p.x-math.sin(math.pi/4)*p.y)/.0012
    v=1160-(math.cos(math.pi/6)*p.z+math.sin(math.pi/6)*(math.sin(math.pi/4)*p.x+math.cos(math.pi/4)*p.y))/.0012
    error=max(abs(u-ob['reference_seam'][0]),abs(v-ob['reference_seam'][1]))
    assert error<.2,(ob.name,error)
    anchors.append({'part':ob.name,'max_control_corner_error_px':error})
assert len(anchors)==42
for name in ['Cream upper block','Cream middle block']:
    ob=s.objects[name];assert len(ob.data.vertices)==8 and len(ob.data.polygons)==6
gold=s.objects['Gold upper broad column'];assert len(gold.data.vertices)==8 and len(gold.data.polygons)==6
corners=[]
for i,expected in enumerate(json.loads(gold['reference_outline'])):
    p=gold.matrix_world@gold.data.vertices[i].co
    actual=[627+(math.cos(math.pi/4)*p.x-math.sin(math.pi/4)*p.y)/.0012,
            1160-(math.cos(math.pi/6)*p.z+math.sin(math.pi/6)*(math.sin(math.pi/4)*p.x+math.cos(math.pi/4)*p.y))/.0012]
    error=max(abs(a-b) for a,b in zip(actual,expected));assert error<.001
    corners.append({'expected_pixel':expected,'actual_pixel':actual,'max_error_px':error})
(out/'reference-projection-verification.json').write_text(json.dumps({'source_blend_sha256':report['source_blend_sha256'],'camera_elevation_deg':elevation,'cube_anchors':anchors,'cream_hexahedra':2,'gold_hexahedra':1,'gold_column_corners':corners,'limits':'Control-corner agreement with authored measurements, not proof that every authored measurement matches the source. Bevels and occlusion alter visible pixels.'},indent=2))
verts=[];dg=bpy.context.evaluated_depsgraph_get()
palette_rows=[]
for ob in parts:
    ev=ob.evaluated_get(dg);me=ev.to_mesh()
    idx=ob['palette_index'];u0=idx%8/8;v0=idx//8/8
    bad=[i for i,loop in enumerate(me.uv_layers.active.data) if not(u0+.001<loop.uv.x<u0+.124 and v0+.001<loop.uv.y<v0+.124)]
    assert not bad,('Evaluated bevel UVs leave the assigned palette cell',ob.name,bad[:5])
    palette_rows.append({'part':ob.name,'palette_index':idx,'evaluated_uv_loops':len(me.uv_layers.active.data)})
    verts.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
(out/'palette-uv-verification.json').write_text(json.dumps({'source_blend_sha256':report['source_blend_sha256'],'parts':palette_rows,'evaluated_loops':sum(row['evaluated_uv_loops'] for row in palette_rows),'outside_palette_cell':0,'method':'Each evaluated UV, including bevel-generated corners, remains within the assigned uniform palette cell with an inset margin.'},indent=2))
lowest=min(v.z for v in verts)
points=sorted(set(tuple(round(v[i],9) for i in range(3)) for v in verts if v.z-lowest<.0001))
# The planar prism terminates at a narrow two-endpoint edge.
assert len(points)==2,points
(out/'base-support-source.json').write_text(json.dumps({'minimum_z_m':lowest,'samples_m':points,'source_blend_sha256':report['source_blend_sha256'],'method':'Two evaluated lowest gold-tip edge endpoints within 0.1 mm of minimum Z. Unreal additionally checks their midpoint.'},indent=2))
result={'parts':len(parts),'components':len(report['components']),'interior_joins':len(report['edges']),'minimum_z_m':lowest,'base_samples':len(points)}
