"""Independent background reopen, FBX roundtrip and representative LOD previews."""
import bpy, json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'Docs/HomesteadPilot/RemainingArt'
data = json.loads((DOC / 'manifest.json').read_text())
assert bpy.app.background and len(data['assets']) == 15
rows = []
for spec in data['assets']:
    key = spec['name']; path = ROOT / spec['blend']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == spec['blend_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    assert Path(scene.get('terrarium_project', '')).resolve() == ROOT
    assert scene.camera and len([o for o in scene.objects if o.get('part')]) == spec['parts_retained']
    lod_objects = [bpy.data.objects['SM_HP_' + key + '_LOD' + str(i)] for i in range(3)]
    for level, obj in enumerate(lod_objects):
        obj.data.calc_loop_triangles()
        assert len(obj.data.loop_triangles) == spec['lods'][level]['triangles']
        assert len(obj.data.materials) == len(spec['materials'])
    render_paths = []
    if key in ['Lodge', 'CivicHall', 'HomesteadCompound', 'MarketStall', 'Sign', 'Lantern']:
        # Render the actual exported mesh, not different authoring geometry.
        for obj in scene.objects:
            if obj.type == 'MESH': obj.hide_render = True
        scene.render.engine = 'CYCLES'; scene.cycles.samples = 12
        scene.cycles.use_denoising = True
        scene.render.resolution_x = 512; scene.render.resolution_y = 512
        scene.render.resolution_percentage = 100
        for level in (0, 2):
            obj = lod_objects[level]; obj.hide_render = False; obj.hide_set(False)
            image = DOC / (key + '-LOD' + str(level) + '.png')
            scene.render.filepath = str(image); bpy.ops.render.render(write_still=True)
            render_paths.append(image.relative_to(ROOT).as_posix())
            obj.hide_render = True; obj.hide_set(True)
    roundtrip = []
    for lod in spec['lods']:
        # Import into a fresh isolated scene, keeping the source project untouched.
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(ROOT / lod['fbx']))
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        assert len(meshes) == 1
        obj = meshes[0]; me = obj.data; me.calc_loop_triangles()
        assert len(me.loop_triangles) == lod['triangles'], (key, lod['level'])
        assert len(me.materials) == len(spec['materials']), (key, lod['level'], [m.name for m in me.materials], spec['materials'])
        material_face_counts = [sum(p.material_index == index for p in me.polygons) for index in range(len(me.materials))]
        assert all(material_face_counts), (key, lod['level'], 'Unused material slot', material_face_counts)
        assert len(me.uv_layers) == 1
        roundtrip.append({'level': lod['level'], 'triangles': len(me.loop_triangles),
                          'materials': [m.name for m in me.materials], 'material_face_counts': material_face_counts, 'uv_layers': len(me.uv_layers)})
    rows.append({'name': key, 'independent_blend_reopen': True, 'parts': spec['parts_retained'],
                 'fbx_roundtrip': roundtrip, 'previews': render_paths})
    (DOC / 'source-verification.json').write_text(json.dumps({'assets': rows,
        'scope': 'Independent source reopening, 45 FBX triangle/material/UV roundtrips, representative LOD0/LOD2 renders. Unreal verification separate.'}, indent=2))
    print('VERIFIED_REMAINING_ART', key, flush=True)
