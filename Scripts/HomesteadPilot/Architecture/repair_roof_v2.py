"""Versioned cottage LOD1/2 repair. Original source/exports and LOD0 stay intact."""
import bpy,bmesh,json,hashlib,struct
from pathlib import Path
ROOT=Path('C:/Users/hello/Projects/Terrarium');BASE=ROOT/'SourceAssets/Blender/HomesteadPilot/Architecture';OUT=BASE/'RoofRepairV2';DOC=ROOT/'Docs/HomesteadPilot/Architecture/RoofRepairV2'
assert Path(bpy.context.scene.get('terrarium_project',''))==ROOT
assert 'Terrarium_ArchitectureRoofRepairV2' not in bpy.data.scenes
prior=bpy.context.window.scene;old_path=BASE/'HomesteadArchitecture.blend';original_sha=hashlib.sha256(old_path.read_bytes()).hexdigest()
with bpy.data.libraries.load(str(old_path),link=False) as (a,b):b.scenes=['Terrarium_HomesteadArchitecture']
s=b.scenes[0];s.name='Terrarium_ArchitectureRoofRepairV2';s['repair']='LOD1/2 deep overlapping roof courses and lowered gable infill; LOD0 unchanged';bpy.context.window.scene=s
manifest=json.loads((ROOT/'Docs/HomesteadPilot/Architecture/manifest.json').read_text());cottage=next(a for a in manifest['assets'] if a['name']=='Cottage');mats=[bpy.data.materials[m['name']] for m in manifest['materials']]
def fingerprint(obs):
    h=hashlib.sha256()
    for o in sorted(obs,key=lambda o:o.get('part','')):
        for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
        for uv in o.data.uv_layers.active.data:h.update(struct.pack('<2f',*uv.uv))
    return h.hexdigest()
original_lod0=fingerprint([o for o in s.objects if o.get('asset')=='Cottage' and o.get('lod')==0]);reports=[]
for level,n in [(1,12),(2,8)]:
    obs=[o for o in s.objects if o.get('asset')=='Cottage' and o.get('lod')==level]
    roof=next(o for o in obs if o['part']=='RoofTiles');infill=next(o for o in obs if o['part']=='GableInfill')
    thickness=max(.095,1.62/n+.04);cross_thickness=max(thickness,(5.54/(21 if level==1 else 13))/1.16+.04);allowance=(2.45/n)*1.62/2.45/2+.07;changed=0;tops=[];cross_tiles=0
    assert len(roof.data.vertices)%8==0
    for i in range(0,len(roof.data.vertices),8):
        vertices=list(roof.data.vertices)[i:i+8];zs=sorted(set(round(v.co.z,6) for v in vertices));assert len(zs)==2
        top=max(v.co.z for v in vertices);bottom=min(v.co.z for v in vertices);tops.append(top)
        assert abs(top-bottom-.095)<.00001
        x=sum(v.co.x for v in vertices)/8;y=sum(v.co.y for v in vertices)/8
        main=2.98+1.62*(1-abs(y)/2.45);cross=2.97+max(0,1-abs(x)/1.16) if y<-.60 else 0
        depth=cross_thickness if cross>main+.03 else thickness
        if cross>main+.03:cross_tiles+=1
        for v in vertices:
            if abs(v.co.z-bottom)<.00001:v.co.z=top-depth;changed+=1
    for v in infill.data.vertices:
        if v.co.z>2.80001:v.co.z-=allowance
    for o in [roof,infill]:
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.data.update()
    assert all(abs(max(v.co.z for v in list(roof.data.vertices)[i:i+8])-top)<.000001 for i,top in zip(range(0,len(roof.data.vertices),8),tops))
    # Merge for export, retaining source part meshes and explicit UVs.
    vs=[];fs=[];mis=[];uvs=[]
    for o in obs:
        offset=len(vs);vs.extend(tuple(v.co) for v in o.data.vertices)
        for p in o.data.polygons:fs.append(tuple(i+offset for i in p.vertices));mis.append(p.material_index);uvs.append([tuple(o.data.uv_layers.active.data[i].uv) for i in p.loop_indices])
    name=f'SM_HP_Cottage_RoofV2_LOD{level}';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();layer=me.uv_layers.new(name='UVMap')
    for m in mats:me.materials.append(m)
    for p,mi,uv in zip(me.polygons,mis,uvs):
        p.material_index=mi
        for li,co in zip(p.loop_indices,uv):layer.data[li].uv=co
    export=bpy.data.objects.new(name,me);s.collection.objects.link(export)
    for c in s.collection.children:c.hide_viewport=False
    for o in s.objects:o.select_set(False)
    export.select_set(True);bpy.context.view_layer.objects.active=export
    path=OUT/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE')
    me.calc_loop_triangles();lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];expected=cottage['lods'][level]
    assert all(abs(a-b)<.00001 for a,b in zip(lo,expected['bounds_m']['min'])) and all(abs(a-b)<.00001 for a,b in zip(hi,expected['bounds_m']['max']))
    assert len(me.loop_triangles)==expected['triangles']
    reports.append({'level':level,'fbx':str(path),'triangles':len(me.loop_triangles),'bounds_m':{'min':lo,'max':hi},'dimensions_m':[hi[i]-lo[i] for i in range(3)],'roof_thickness_m':thickness,'cross_gable_thickness_m':cross_thickness,'cross_gable_tiles':cross_tiles,'gable_top_lowering_m':allowance,'tile_top_vertices_preserved':True,'changed_bottom_vertices':changed,'material_slots':[m.name for m in mats]})
    bpy.data.objects.remove(export,do_unlink=True)
assert fingerprint([o for o in s.objects if o.get('asset')=='Cottage' and o.get('lod')==0])==original_lod0
for o in s.objects:
    if o.type=='MESH':
        for i,m in enumerate(mats):o.data.materials[i]=m
for c in s.collection.children:c.hide_render=not any(o.get('asset')=='Cottage' and o.get('lod')==2 for o in c.objects)
source=OUT/'HomesteadArchitecture_RoofV2.blend';library=OUT/'ArchitectureRoofV2.library.blend'
bpy.data.libraries.write(str(library),{s},path_remap='RELATIVE',fake_user=True,compress=True)
report={'source_blend':str(source),'library':str(library),'original_source':str(old_path),'original_source_sha256':original_sha,'original_source_unchanged':hashlib.sha256(old_path.read_bytes()).hexdigest()==original_sha,'lod0_geometry_uv_fingerprint':original_lod0,'lod0_unchanged':True,'lod0_fbx':cottage['lods'][0]['fbx'],'repairs':reports,'scene':s.name,'purpose':'Restore continuous terracotta roof surfaces at authored LOD1/2 without changing visible tile highpoints or ridge dimensions.'}
(DOC/'manifest.json').write_text(json.dumps(report,indent=2));bpy.context.window.scene=prior
result=report
