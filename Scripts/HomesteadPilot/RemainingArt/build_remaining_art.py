"""Background-only pilot copies of the inherited architecture/prop collection.

Keeps the source design, physical bounds, UVs, material slots and every part.
LOD1 reduces edge bevel tessellation; LOD2 removes subpixel bevels. No component
is randomly decimated or deleted, so awnings, frames and ornaments remain whole.
"""
import bpy, json, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'SourceAssets/Blender/HomesteadPilot/RemainingArt'
DOC = ROOT / 'Docs/HomesteadPilot/RemainingArt'
KEYS = ['Lodge', 'CivicHall', 'HomesteadCompound', 'MarketStall', 'Sign', 'Lantern',
        'MossTonic', 'TrailPrism', 'EmberCrest', 'DeepDelverMark', 'Grove', 'Tide', 'Ember', 'Storm', 'BridgeThreshold']
assert bpy.app.background, 'Never run this batch in the live authoring editor'
OUT.mkdir(parents=True, exist_ok=True); DOC.mkdir(parents=True, exist_ok=True)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def relative(p): return p.relative_to(ROOT).as_posix()
def bounds(mesh):
    return {op: [fn(v.co[i] for v in mesh.vertices) for i in range(3)] for op, fn in [('min', min), ('max', max)]}

def evaluate(parts, materials, level, scene):
    vertices, faces, faceuvs, slots = [], [], [], []
    source_names = []
    for part in parts:
        for material in part.data.materials:
            if material.name not in source_names: source_names.append(material.name)
    assert len(source_names) == len(materials), (source_names, [m.name for m in materials])
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    for part in parts:
        ev = part.evaluated_get(dg); me = ev.to_mesh(); start = len(vertices)
        assert me.uv_layers.active, part.name
        vertices.extend(tuple(part.matrix_world @ v.co) for v in me.vertices)
        for face in me.polygons:
            faces.append(tuple(start + v for v in face.vertices))
            faceuvs.append([tuple(me.uv_layers.active.data[i].uv) for i in face.loop_indices])
            slot_material = me.materials[face.material_index]
            slots.append(source_names.index(slot_material.name))
        ev.to_mesh_clear()
    mesh = bpy.data.meshes.new('Pilot_LOD%d' % level)
    mesh.from_pydata(vertices, [], faces); mesh.update()
    for material in materials: mesh.materials.append(material)
    uv = mesh.uv_layers.new(name='UVMap')
    for poly, us, slot in zip(mesh.polygons, faceuvs, slots):
        poly.material_index = slot
        for i, value in zip(poly.loop_indices, us): uv.data[i].uv = value
    return mesh

rows = []
requested = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else KEYS
for key in requested:
    assert key in KEYS
    source = ROOT / 'SourceAssets/Blender' / key / (key + '.blend')
    before = sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    assert Path(scene.get('terrarium_project', '')).resolve() == ROOT.resolve()
    assert scene.get('asset_name') == key
    target = OUT / key; target.mkdir(exist_ok=True)
    parts = [o for o in scene.objects if o.get('part')]
    assert parts and scene.camera
    old = bpy.data.objects.get('SM_Blender_' + key)
    assert old and old.type == 'MESH'
    materials = list(old.data.materials)
    assert materials
    original_mesh = old.data.copy()
    cached_material_alias = len(set(m.name for m in materials)) != len(materials)
    if cached_material_alias:
        # The compound's cached export mesh aliases its two materials after library
        # packaging. Recover the distinct authoring materials in export part order.
        authored = []
        for part in parts:
            for material in part.data.materials:
                if material not in authored: authored.append(material)
        assert len(authored) == len(materials)
        materials = authored
        original_mesh.materials.clear()
        for material in materials: original_mesh.materials.append(material)
        # The cached merged mesh also lost polygon-to-slot assignments. Restore
        # these from editable parts only after verifying the exact geometry.
        restored = evaluate(parts, materials, 0, scene)
        assert len(restored.vertices) == len(original_mesh.vertices)
        max_vertex_delta = max((a.co-b.co).length for a,b in zip(restored.vertices, original_mesh.vertices))
        assert max_vertex_delta < 1e-6, (key, 'Authored geometry differs from cached source', max_vertex_delta)
        assert [tuple(p.vertices) for p in restored.polygons] == [tuple(p.vertices) for p in original_mesh.polygons]
        original_mesh = restored
    original_bounds = bounds(original_mesh)
    bpy.data.objects.remove(old, do_unlink=True)
    modifiers = [(m, m.segments, m.show_viewport, m.show_render) for o in parts for m in o.modifiers if m.type == 'BEVEL']
    images = {n.image for m in materials if m.use_nodes for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image}
    for im in images:
        assert im.packed_file, (key, im.name)
        # Extract existing packed maps unchanged for a self-contained source package.
        filename = Path(im.filepath).name or im.name + '.png'
        if not filename.lower().endswith('.png'): filename += '.png'
        path = target / filename
        path.write_bytes(im.packed_file.data)
        im.filepath = str(path)
    lods = []; lod_objects = []
    for level in range(3):
        for mod, segments, viewport, render in modifiers:
            mod.segments = segments if level == 0 else 1
            mod.show_viewport = viewport and level != 2
            mod.show_render = render and level != 2
        mesh = original_mesh if level == 0 else evaluate(parts, materials, level, scene)
        mesh.calc_loop_triangles()
        material_face_counts = [sum(p.material_index == index for p in mesh.polygons) for index in range(len(materials))]
        assert all(material_face_counts), (key, level, 'Unused material section', material_face_counts)
        name = 'SM_HP_' + key + '_LOD' + str(level)
        ob = bpy.data.objects.new(name, mesh); scene.collection.objects.link(ob)
        for item in scene.objects: item.select_set(False)
        ob.hide_set(False); ob.hide_render = False; ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        fbx = target / (name + '.fbx')
        bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'MESH'},
            apply_unit_scale=True, axis_forward='-Y', axis_up='Z', mesh_smooth_type='FACE',
            add_leaf_bones=False, bake_anim=False, path_mode='STRIP', embed_textures=False)
        current_bounds = bounds(mesh)
        max_delta = max(abs(current_bounds[b][i] - original_bounds[b][i]) for b in ('min', 'max') for i in range(3))
        assert max_delta < .025, (key, level, 'bounds drift', max_delta)
        lods.append({'level': level, 'fbx': relative(fbx), 'triangles': len(mesh.loop_triangles),
                     'vertices': len(mesh.vertices), 'bounds_m': current_bounds, 'max_bounds_delta_m': max_delta,
                     'sha256': sha(fbx), 'material_slots': [m.name for m in mesh.materials]})
        lods[-1]['material_face_counts'] = material_face_counts
        ob.hide_render = True; ob.hide_set(True); ob.select_set(False); lod_objects.append(ob)
    assert lods[0]['triangles'] > lods[1]['triangles'] > lods[2]['triangles'] > 0, (key, lods)
    for mod, segments, viewport, render in modifiers:
        mod.segments = segments; mod.show_viewport = viewport; mod.show_render = render
    scene['pilot_variant'] = 'RemainingArt'
    scene['lod_policy'] = 'Source LOD0, one-segment bevel LOD1, bevel-free LOD2; every authored part retained'
    bpy.context.preferences.filepaths.save_version = 0
    for part in parts: part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    blend = target / (key + '.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    row = {'name': key, 'source_blend': relative(source), 'source_sha256': before,
           'blend': relative(blend), 'blend_sha256': sha(blend), 'parts_retained': len(parts),
           'lods': lods, 'bounds_m': original_bounds, 'materials': [m.name for m in materials],
           'baseline_mesh': '/Game/Terrarium/Blender/' + key + '/SM_Blender_' + key,
           'collision': 'complex_as_simple' if key in KEYS[:6] or key == 'BridgeThreshold' else 'none',
           'screen_sizes': [1., .22, .075] if key in KEYS[:4] else [1., .16, .045]}
    assert sha(source) == before, 'Source asset was unexpectedly modified'
    (DOC / (key + '.json')).write_text(json.dumps(row, indent=2))
    rows.append(row)
    available = [json.loads((DOC / (k + '.json')).read_text()) for k in KEYS if (DOC / (k + '.json')).exists()]
    (DOC / 'manifest.json').write_text(json.dumps({'assets': available, 'unreal_validation': 'Pending coordinator'}, indent=2))
    print('PILOT_ASSET_COMPLETE', key, [r['triangles'] for r in lods], flush=True)

available = [json.loads((DOC / (k + '.json')).read_text()) for k in KEYS if (DOC / (k + '.json')).exists()]
(DOC / 'manifest.json').write_text(json.dumps({'scope': 'Remaining inherited homestead architecture and props; characters excluded',
    'geometry_policy': 'Preserve LOD0, authored source parts, UVs, material identity, pivot, footprint and placement scale',
    'assets': available, 'unreal_validation': 'Pending coordinator import and visual inspection'}, indent=2))
print('REMAINING_ART_BATCH_COMPLETE', len(available), flush=True)
