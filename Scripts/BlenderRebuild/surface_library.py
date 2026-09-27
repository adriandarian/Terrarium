"""Preserve source surface revisions as packed, named material alternatives.

The PNGs are tiling surface artwork, not object cutouts. No magenta-keyed object
reference is used as a texture. Existing world material selections are retained.
"""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium')
assert Path(bpy.context.scene.get('terrarium_project',''))==ROOT
key='SurfaceLibrary';out=ROOT/'SourceAssets/Blender'/key;out.mkdir(exist_ok=True)
review=ROOT/'Docs/BlenderRebuild'/key;review.mkdir(exist_ok=True)
assert not bpy.data.scenes.get('Terrarium_SurfaceLibrary'),'Library already exists; inspect before replacing'
s=bpy.data.scenes.new('Terrarium_SurfaceLibrary');bpy.context.window.scene=s
s['terrarium_project']=str(ROOT);s['asset_name']=key
s['purpose']='Editable material alternatives on physical closed sample slabs. No world replacement.'
files=sorted(p for p in (ROOT/'SourceAssets/Voxel').glob('*.png') if p.name.startswith(('terrain_','cottage_')))
rows=[]
for i,p in enumerate(files):
    mat=bpy.data.materials.new('M_Source_'+p.stem);mat.use_nodes=True
    image=bpy.data.images.load(str(p),check_existing=False);image.pack()
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.22 if 'water' in p.name else .82
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    bpy.ops.mesh.primitive_cube_add(size=1,location=((i%8)*1.18,(i//8)*1.18,0))
    ob=bpy.context.object;ob.name='Sample_'+p.stem;ob.scale=(1,1,.08)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat);ob['source']=str(p.relative_to(ROOT))
    # Full tile on the top face; all remaining faces also stay within [0,1].
    for face in ob.data.polygons:
        axes=[j for j in range(3) if j!=max(range(3),key=lambda j:abs(face.normal[j]))]
        for li in face.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            ob.data.uv_layers.active.data[li].uv=tuple(v[j]/(.08 if j==2 else 1)+.5 for j in axes)
    family='Cottage' if p.name.startswith('cottage_') else 'Water' if 'water' in p.name else 'CliffColumn' if 'cliff' in p.name else 'GrassTerrain' if 'grass' in p.name else 'GroundFoliage' if 'foliage' in p.name else 'StoneStairs' if 'paver' in p.name else 'RiverCrossing' if 'wood' in p.name else 'MossCap' if 'moss' in p.name else 'TrailPatch'
    rows.append({'source':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'material':mat.name,'sample':ob.name,'family':family,'status':'material_alternative_authored_not_selected_for_world'})
world=bpy.data.worlds.new('Surface library studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.world=world
light=bpy.data.lights.new('Library softbox','AREA');light.energy=1800;light.size=10;lo=bpy.data.objects.new('Library softbox',light);s.collection.objects.link(lo);lo.location=(4,3,8)
camera=bpy.data.cameras.new('Library overview');cam=bpy.data.objects.new('Library overview',camera);s.collection.objects.link(cam);cam.location=(4.13,2.95,12);camera.type='ORTHO';camera.ortho_scale=10;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
s.view_settings.view_transform='Standard';s.render.image_settings.file_format='PNG';s.render.filepath=str(review/'overview.png')
for ob in s.objects:ob.select_set(ob.type=='MESH')
bpy.ops.export_scene.fbx(filepath=str(out/'SurfaceLibrary.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',bake_anim=False)
bpy.ops.export_scene.gltf(filepath=str(out/'SurfaceLibrary.glb'),use_selection=True,use_active_scene=True,export_format='GLB')
# Isolated editable library; create a normal single-scene project in a separate process.
bpy.data.libraries.write(str(out/'SurfaceLibrary.blend'),{s},path_remap='RELATIVE',fake_user=True,compress=True)
(review/'materials.json').write_text(json.dumps({'source_count':len(rows),'packed_images':len(rows),'materials':rows,'scope':'Source-authored base-color alternatives. No invented normal or displacement maps; revisions retained independently.'},indent=2))
bpy.ops.render.render(write_still=True)
result={'asset':key,'materials':len(rows),'packed_source_images':len(rows)}
