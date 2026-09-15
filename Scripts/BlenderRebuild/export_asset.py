"""Export the currently verified asset scene, preserving editable source parts."""
import bpy,bmesh,json,hashlib,subprocess
from pathlib import Path
ROOT=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene
assert Path(s.get('terrarium_project',''))==ROOT
key=s['asset_name'];source=ROOT/s['concept'];assert source.is_file()
out=ROOT/'SourceAssets/Blender'/key;review=ROOT/'Docs/BlenderRebuild'/key
import sys
sys.path.insert(0,str(ROOT/'Scripts/BlenderRebuild'))
from texture_export import normalize_maps
normalize_maps(s,out,review,key)
parts=[o for o in s.objects if o.get('part')];assert parts
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];uvs=[];failures=[];materials=[];face_materials=[]
for o in parts:
    ev=o.evaluated_get(dg);me=ev.to_mesh();start=len(verts)
    bm=bmesh.new();bm.from_mesh(me)
    if bm.calc_volume(signed=True)<=0 or any(not e.is_manifold for e in bm.edges):failures.append(o.name)
    bm.free();verts.extend(tuple(o.matrix_world@v.co) for v in me.vertices)
    for p in me.polygons:
        faces.append(tuple(start+i for i in p.vertices));uvs.append([tuple(me.uv_layers.active.data[i].uv) for i in p.loop_indices])
        material=me.materials[p.material_index]
        if material not in materials:materials.append(material)
        face_materials.append(materials.index(material))
    ev.to_mesh_clear()
assert not failures,failures
name='SM_Blender_'+key
if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();uv=me.uv_layers.new(name='UVMap')
for material in materials:me.materials.append(material)
for p,us,mi in zip(me.polygons,uvs,face_materials):
    p.material_index=mi
    for i,u in zip(p.loop_indices,us):uv.data[i].uv=u
ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob)
for o in s.objects:o.select_set(False)
ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='COPY')
bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),use_selection=True,use_active_scene=True,export_format='GLB',export_yup=True)
me.calc_loop_triangles()
report={'asset':key,'mesh':name,'source':s['concept'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'parts':len(parts),'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'all_parts_closed_positive_volume':True,'uv_layers':len(me.uv_layers),'material_slots':len(me.materials),'bounds_m':{'min':[min(v[i] for v in verts) for i in range(3)],'max':[max(v[i] for v in verts) for i in range(3)]},'files':{},'fidelity':'pending_visual_refinement_and_acceptance'}
for p in out.iterdir():
    if p.suffix in ['.fbx','.glb','.png']:report['files'][p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
report['materials']=[m.name for m in materials]
if s.get('variant_of'):report['variant_of']=s['variant_of'];report['variant_purpose']=s.get('variant_purpose','')
ob.hide_render=True;ob.hide_set(True)
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.data.libraries.write(str(out/(key+'.blend')),{s},path_remap='RELATIVE',fake_user=True,compress=True)
(review/'mesh-validation.json').write_text(json.dumps(report,indent=2))
# Package the isolated scene as a normal project without saving other live scenes.
proc=subprocess.run([bpy.app.binary_path,'--background','--factory-startup','--python-exit-code','1','--python',str(ROOT/'Scripts/BlenderRebuild/package_blend.py'),'--',key],capture_output=True,text=True,timeout=120,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
assert proc.returncode==0 and 'PACKAGED_NORMAL_BLEND '+key in proc.stdout,(proc.stdout,proc.stderr)
result=report
