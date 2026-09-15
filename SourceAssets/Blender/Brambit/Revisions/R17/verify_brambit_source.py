import bpy,bmesh,sys,json,hashlib,math,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene
assert Path(s.get('terrarium_project',''))==ROOT and s['asset_name']=='Brambit'
sys.path.insert(0,str(ROOT/'Scripts/BlenderRebuild'))
from storm_structure import inspect,shape,interior
parts=[o for o in s.objects if o.get('part')];construction=[o for o in s.objects if o.get('construction_part')]
assert len(parts)==5 and len(construction)==185 and all(o.hide_render for o in construction)
out=ROOT/'Docs/BlenderRebuild/Brambit';source=ROOT/'SourceAssets/Blender/Brambit/Brambit.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
shoot_rows=[]
for name in ['Central','Left','Right']:
    shoot=s.objects[name+' leafy shoot']
    assert shoot.get('union_method')=='Axis-aligned cell occupancy; shared internal faces omitted'
    assert all(len(p.vertices)==4 and max(abs(v) for v in p.normal)>.99999 for p in shoot.data.polygons)
    blocks=[o for o in construction if o.get('construction_part','').startswith(name+' shoot')]
    authored=[o.matrix_world@v.co for o in blocks for v in o.data.vertices]
    actual=[shoot.matrix_world@v.co for v in shoot.data.vertices]
    bounds_error=max(abs(op(v[i] for v in authored)-op(v[i] for v in actual)) for i in range(3) for op in [min,max])
    assert bounds_error<.0000011
    ev=shoot.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
    unseen=set(bm.verts);components=[]
    while unseen:
        pending=[unseen.pop()];count=0
        while pending:
            vertex=pending.pop();count+=1
            for edge in vertex.link_edges:
                other=edge.other_vert(vertex)
                if other in unseen:unseen.remove(other);pending.append(other)
        components.append(count)
    assert len(components)==1 and all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
    shoot_rows.append({'part':shoot.name,'authored_blocks':len(blocks),'planar_boundary_quads':len(shoot.data.polygons),'evaluated_connected_components':len(components),'authored_bounds_error_m':bounds_error,'closed_positive_volume':True})
    bm.free();ev.to_mesh_clear()
(out/'shoot-topology-verification.json').write_text(json.dumps({'source_blend_sha256':digest,'shoots':shoot_rows,'limits':'Planar surfaces, connected closed topology and authored bounds. Does not establish concept fidelity.'},indent=2))
uv_rows=[]
for ob in parts:
    assert ob.get('surface_uv_mapping')=='Planar pigment-cell coverage in authored bounds'
    data=ob.data.uv_layers.active.data;areas=[]
    for face in ob.data.polygons:
        coords=[data[i].uv for i in face.loop_indices]
        area=abs(sum(p.x*q.y-q.x*p.y for p,q in zip(coords,coords[1:]+coords[:1])))/2
        areas.append(area)
    covered=sum(area>1e-12 for area in areas)
    assert covered==len(areas) and sum(areas)>1e-5
    uv_rows.append({'part':ob.name,'surface_faces':len(areas),'faces_with_texture_area':covered,'total_uv_area':sum(areas),'numerical_cleanup_merged_vertices':ob.get('numerical_cleanup_merged_vertices',0)})
(out/'surface-uv-verification.json').write_text(json.dumps({'source_blend_sha256':digest,'parts':uv_rows,'limits':'Usable planar texture coverage; does not measure likeness to the source.'},indent=2))
report=inspect(parts)
# The global box grid can miss the central shoot's shallow root overlap.
# Sample the measured stem base directly, retaining the same two independent
# interior tests used for every other connection witness.
for name in ['Central','Left','Right']:
    stem=next(o for o in construction if o.get('construction_part')==name+' shoot stem')
    verts=[stem.matrix_world@v.co for v in stem.data.vertices]
    lo=Vector([min(v[i] for v in verts) for i in range(3)]);hi=Vector([max(v[i] for v in verts) for i in range(3)])
    shoot=shape(s.objects[name+' leafy shoot']);found=None
    for target in ['Joined moss crown','Joined body face and feet']:
        other=shape(s.objects[target])
        for fx,fy,dz in itertools.product([.1,.3,.5,.7,.9],[.1,.3,.5,.7,.9],[.001,.003,.006,.010,.015]):
            p=Vector((lo.x+(hi.x-lo.x)*fx,lo.y+(hi.y-lo.y)*fy,lo.z+dz))
            if interior(shoot,p) and interior(other,p):found=(target,list(p));break
        if found:break
    assert found,('No root overlap witness',name)
    report['edges'].append({'a':name+' leafy shoot','b':found[0],'interior_witness_m':found[1],'sampling':'Measured stem base'})
adj={o.name:set() for o in parts}
for edge in report['edges']:adj[edge['a']].add(edge['b']);adj[edge['b']].add(edge['a'])
seen=set();pending=[parts[0].name]
while pending:
    name=pending.pop()
    if name in seen:continue
    seen.add(name);pending.extend(adj[name]-seen)
assert len(seen)==5;report['components']=[sorted(seen)]
report.update(source_blend_sha256=digest,parts=5,editable_construction_blocks=185,limits='Five closed union volumes overlap at their joins. Static geometry only; no character rig or physics simulation.')
(out/'connection-verification.json').write_text(json.dumps(report,indent=2))
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in parts:
    ev=ob.evaluated_get(dg);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
    assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
    assert all(0<loop.uv.x<1 and 0<loop.uv.y<.25 for loop in me.uv_layers.active.data)
    rows.append({'part':ob.name,'vertices':len(me.vertices),'closed':True,'volume_m3':bm.calc_volume(signed=True)})
    bm.free();ev.to_mesh_clear()
body=s.objects['Joined body face and feet'];tree=BVHTree.FromObject(body,dg)
feet=[o for o in construction if o.get('anatomy')=='foot'];assert len(feet)==4
samples=[]
for foot in feet:
    for dx,dy in [(0,0),(-.023,-.026),(-.023,.026),(.023,-.026),(.023,.026)]:
        x=foot.location.x+dx;y=foot.location.y+dy
        hit=tree.ray_cast(Vector((x,y,-.1)),Vector((0,0,1)))
        assert hit[0] is not None and abs(hit[0].z-.117)<.0001
        samples.append({'foot':foot.name,'point_m':[x,y,hit[0].z]})
(out/'base-support-source.json').write_text(json.dumps({'source_blend_sha256':digest,'foot_count':4,'samples':samples,'method':'Five upward ray samples under each of the four unioned feet, compared with its intended sole plane.'},indent=2))
offset=s.camera.location-Vector(s['reference_focus']);elevation=math.degrees(math.atan2(offset.z,math.hypot(offset.x,offset.y)))
assert abs(elevation-20)<.001
from bpy_extras.object_utils import world_to_camera_view
landmarks=[]
for x,y,target in [(-.286,-.231,(525,1155)),(-.260,.075,(362,1066)),(.060,-.250,(813,1089))]:
    foot=min(feet,key=lambda ob:abs(ob.location.x-x)+abs(ob.location.y-y))
    corners=[foot.matrix_world@Vector(corner) for corner in foot.bound_box]
    corner=Vector((min(p.x for p in corners),min(p.y for p in corners),min(p.z for p in corners)))
    uv=world_to_camera_view(s,s.camera,corner)
    pixel=(uv.x*s.render.resolution_x,(1-uv.y)*s.render.resolution_y)
    error=math.dist(pixel,target)
    assert error<2, (foot.name,pixel,target,error)
    landmarks.append({'foot':foot.name,'reference_pixel':target,'projected_pixel':pixel,'error_pixels':error})
(out/'foot-landmark-verification.json').write_text(json.dumps({'source_blend_sha256':digest,'landmarks':landmarks,'method':'Unbeveled lower front-left corner of each visible authored foot, projected through the saved reference camera.','limits':'Three manually read approximate concept landmarks only. Does not prove whole-foot shape, hidden fourth foot or overall asset fidelity.'},indent=2))
(out/'source-validation.json').write_text(json.dumps({'source_blend_sha256':digest,'union_volumes':rows,'construction_blocks':185,'feet':4,'foot_samples':20,'camera_elevation_deg':elevation,'palette_uv_bounds_valid':True,'limits':'Topology, source usability and sole geometry checks do not establish concept fidelity. Rear anatomy is inferred.'},indent=2))
result={'volumes':5,'construction_blocks':185,'joins':len(report['edges']),'feet':4,'sole_samples':20}
