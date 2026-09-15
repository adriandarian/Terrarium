"""Evaluate Blender bevels into a single UV-mapped, metre-scale export mesh."""
import bpy,bmesh,json,hashlib,shutil
from pathlib import Path
ROOT=Path('C:/Users/hello/Projects/Terrarium')
OUT=ROOT/'SourceAssets/Blender/Cottage';REVIEW=ROOT/'Docs/BlenderRebuild/Cottage'
s=bpy.context.scene
assert s.get('terrarium_project')==str(ROOT) and s.name=='Terrarium_Cottage'
parts=[o for o in s.objects if o.get('part')]
dg=bpy.context.evaluated_depsgraph_get()
verts=[];faces=[];uvs=[];volumes=[]
for o in parts:
    ev=o.evaluated_get(dg);me=ev.to_mesh();start=len(verts)
    bm=bmesh.new();bm.from_mesh(me)
    volumes.append({'part':o.name,'volume':bm.calc_volume(signed=True),'boundary_edges':sum(not e.is_manifold for e in bm.edges)})
    bm.free()
    verts.extend([tuple(o.matrix_world@v.co) for v in me.vertices])
    for p in me.polygons:
        faces.append(tuple(start+i for i in p.vertices))
        uvs.append([tuple(me.uv_layers.active.data[i].uv) for i in p.loop_indices])
    ev.to_mesh_clear()
assert all(v['volume']>0 and v['boundary_edges']==0 for v in volumes)
name='SM_Blender_Cottage'
if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();uv=me.uv_layers.new(name='UVMap')
for p,us in zip(me.polygons,uvs):
    for i,u in zip(p.loop_indices,us):uv.data[i].uv=u
ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);me.materials.append(parts[0].data.materials[0])
for o in s.objects:o.select_set(False)
ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=False)
bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),use_selection=True,use_active_scene=True,export_format='GLB',export_yup=True)
me.calc_loop_triangles()
report={'asset':name,'authoring':'Blender 5.2.1 via Blender Lab MCP','parts':len(parts),'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'uv_layers':len(me.uv_layers),'material_slots':len(me.materials),'all_parts_closed_positive_volume':True,'bounds_m':{'min':[min(v[i] for v in verts) for i in range(3)],'max':[max(v[i] for v in verts) for i in range(3)]},'source_sha256':hashlib.sha256((ROOT/'SourceAssets/Voxel/cottage.png').read_bytes()).hexdigest(),'files':{},'fidelity':'In progress. Importability and mesh checks do not establish concept parity.'}
for p in OUT.iterdir():
    if p.suffix in ('.fbx','.glb','.png'):report['files'][p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
ob.hide_render=True;ob.hide_set(True)
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Cottage.blend'))
(REVIEW/'mesh-validation.json').write_text(json.dumps(report,indent=2))
result=report
