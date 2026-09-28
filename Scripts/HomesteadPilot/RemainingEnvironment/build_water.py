"""Build the remaining river surface in a disposable background Blender process.

Run Blender --background --factory-startup --python build_water.py. Never uses
the live Blender editor. Coordinates are metres; source pivot matches old water.
"""
import bpy, bmesh, hashlib, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
assert (ROOT / 'Terrarium.uproject').is_file()
OUT = ROOT / 'SourceAssets/Blender/HomesteadPilot/RemainingEnvironment'
DOC = ROOT / 'Docs/HomesteadPilot/RemainingEnvironment'
OUT.mkdir(parents=True, exist_ok=True)
DOC.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.name = 'Terrarium_HomesteadRiver'
s['terrarium_project'] = str(ROOT)
s['asset_purpose'] = 'Remaining homestead river, continuous current surface'
s.unit_settings.system = 'METRIC'
s.unit_settings.scale_length = 1

mat = bpy.data.materials.new('M_HP_RiverCurrent')
mat.diffuse_color = (.055, .22, .19, 1)
mat.use_nodes = True
n = mat.node_tree.nodes
l = mat.node_tree.links
bs = n.get('Principled BSDF')
bs.inputs['Roughness'].default_value = .35
bs.inputs['Specular IOR Level'].default_value = .35
tex = n.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value = 3.5
tex.inputs['Detail'].default_value = 3
coord = n.new('ShaderNodeTexCoord')
mapping = n.new('ShaderNodeVectorMath')
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (.3, 2.8, 1)
l.new(coord.outputs['Generated'], mapping.inputs[0])
l.new(mapping.outputs[0], tex.inputs['Vector'])
ramp = n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .12
ramp.color_ramp.elements[0].color = (.018, .105, .105, 1)
ramp.color_ramp.elements[1].position = .9
ramp.color_ramp.elements[1].color = (.105, .28, .225, 1)
l.new(tex.outputs['Fac'], ramp.inputs[0])
l.new(ramp.outputs[0], bs.inputs['Base Color'])
bump = n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = .13
bump.inputs['Distance'].default_value = .012
l.new(tex.outputs['Fac'], bump.inputs['Height'])
l.new(bump.outputs[0], bs.inputs['Normal'])

lo, hi = (-1.51, -1.51, -.295), (1.51, 1.51, .021)
verts = [(x, y, z) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
mesh = bpy.data.meshes.new('SM_HP_RiverSurface3m')
mesh.from_pydata(verts, [], faces)
mesh.update()
mesh.materials.append(mat)
uv = mesh.uv_layers.new(name='UVMap')
for p in mesh.polygons:
    for i in p.loop_indices:
        v = mesh.vertices[mesh.loops[i].vertex_index].co
        uv.data[i].uv = ((v.x+1.51)/3.02, (v.y+1.51)/3.02)
ob = bpy.data.objects.new(mesh.name, mesh)
s.collection.objects.link(ob)
ob.select_set(True)
bpy.context.view_layer.objects.active = ob
fbx = OUT / (mesh.name + '.fbx')
bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'MESH'},
    apply_unit_scale=True, axis_forward='-Y', axis_up='Z', mesh_smooth_type='FACE',
    add_leaf_bones=False, bake_anim=False, path_mode='AUTO')

world = bpy.data.worlds.new('RiverWorld')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.22,.25,.19,1)
world.node_tree.nodes['Background'].inputs[1].default_value = .5
s.world = world
for name,pos,power,size in [('Key',(-4,-3,6),700,5),('Fill',(3,1,4),350,4)]:
    d = bpy.data.lights.new(name, 'AREA'); d.energy = power; d.size = size
    a = bpy.data.objects.new(name,d); s.collection.objects.link(a); a.location = pos
    a.rotation_euler = (-a.location).to_track_quat('-Z','Y').to_euler()
d = bpy.data.cameras.new('RiverCamera'); cam = bpy.data.objects.new('RiverCamera',d)
s.collection.objects.link(cam); cam.location = (4,-5,5)
cam.rotation_euler = (-cam.location).to_track_quat('-Z','Y').to_euler()
d.type = 'ORTHO'; d.ortho_scale = 4.9; s.camera = cam
s.render.engine = 'CYCLES'; s.cycles.samples = 24
s.render.resolution_x = 900; s.render.resolution_y = 700; s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'; s.render.filepath = str(DOC/'river-source-preview.png')
s.view_settings.view_transform = 'AgX'
bpy.ops.render.render(write_still=True)
blend = OUT/'RiverSurface3m.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
mesh.calc_loop_triangles()
rel = lambda p: p.relative_to(ROOT).as_posix()
manifest = {
    'project':'Terrarium', 'family':'RemainingEnvironment', 'authoring':'Locally authored Blender geometry; no external assets',
    'assets':[{'name':'RiverSurface3m','mesh_name':mesh.name,'fbx':rel(fbx),'blend_path':rel(blend),
               'dimensions_m':[3.02,3.02,.316], 'bounds_m':{'min':list(lo),'max':list(hi)},
               'triangles':len(mesh.loop_triangles),'vertices':len(mesh.vertices),
               'material_slots':['M_HP_RiverCurrent'],
               'lod_policy':'One 12-triangle watertight mesh. No redundant LODs; pixel-scale current detail fades through derivatives.',
               'collision':'NoCollision','fbx_sha256':hashlib.sha256(fbx.read_bytes()).hexdigest()}],
    'water_instances_expected':{'WaterTile_v4_Detail':11,'WaterShallow_v4_Detail':166,'WaterDeep_v4_Detail':13},
    'preservation':'Fit old local bounds to new geometry; preserve each tile world envelope, top elevation and orientation. Do not modify approved pilot families or grass.',
    'materials':{'medium':'M_HP_RiverCurrent','shallow':'M_HP_RiverShallow','deep':'M_HP_RiverDeep'},
    'render_policy':'Opaque lit water, animated world-space current and normals; no transparency, WPO, foam decals or extra actors',
    'preview_note':'Blender preview is source geometry/palette only. Exact animated Unreal material requires editor visual validation.',
    'status':'Authored and exported; independent reopen, Unreal import and visual checks are separate'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
(DOC/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('TERRARIUM_REMAINING_ENVIRONMENT_EXPORTED')
