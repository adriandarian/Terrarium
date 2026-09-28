"""Import completed pilot manifests into isolated Unreal asset folders."""
import unreal, json, hashlib
from pathlib import Path

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
receipts = []

def import_file(source, dest, name, options=None, factory=None):
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_path = dest
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = True
    if options: task.options = options
    if factory: task.factory = factory
    tools.import_asset_tasks([task])
    asset = unreal.load_asset(dest + '/' + name)
    assert asset, (source, dest, name)
    return asset

for family in ('Architecture', 'Landscape'):
    manifest_path = OUT / family / 'manifest.json'
    if not manifest_path.exists():
        continue
    data = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    dest = '/Game/Terrarium/HomesteadPilot/' + family
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    receipt_path = OUT / family / 'unreal-import.json'
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_text())
        if previous.get('manifest_sha256') == manifest_sha:
            receipts.append(previous)
            continue
    materials = {}
    material_records = []
    for row in data['materials']:
        name = row['name']
        m = unreal.load_asset(dest + '/Materials/' + name)
        if not m:
            m = tools.create_asset(name, dest + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
        assert m
        mel.delete_all_material_expressions(m)
        texture_path = row.get('base_color_texture')
        if texture_path:
            source = Path(texture_path)
            if not source.is_absolute(): source = ROOT / source
            assert source.is_file() and source.resolve().is_relative_to(ROOT)
            t = import_file(source, dest + '/Textures', 'T_' + name + '_BaseColor')
            t.set_editor_property('srgb', True)
            t.set_editor_property('filter', unreal.TextureFilter.TF_DEFAULT)
            unreal.EditorAssetLibrary.save_loaded_asset(t)
            n = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -320, 0)
            n.texture = t
            mel.connect_material_property(n, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
        else:
            n = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -320, 0)
            rgb = row.get('base_color_linear', [.3, .3, .3])
            n.set_editor_property('constant', unreal.LinearColor(*rgb[:3], 1))
            mel.connect_material_property(n, '', unreal.MaterialProperty.MP_BASE_COLOR)
        for prop, value, y in ((unreal.MaterialProperty.MP_ROUGHNESS, row.get('roughness', .88), 200),
                               (unreal.MaterialProperty.MP_SPECULAR, .15, 300)):
            n = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -320, y)
            n.r = value
            mel.connect_material_property(n, '', prop)
        mel.recompile_material(m)
        assert unreal.EditorAssetLibrary.save_loaded_asset(m)
        materials[name] = m
        material_records.append({'name': name, 'material': m.get_path_name(), 'texture_source': texture_path})
    records = []
    for row in data['assets']:
        source = Path(row['fbx'])
        if not source.is_absolute(): source = ROOT / source
        assert source.is_file() and source.resolve().is_relative_to(ROOT / 'SourceAssets/Blender/HomesteadPilot')
        name = row['name'] if row['name'].startswith('SM_') else 'SM_' + row['name']
        opts = unreal.FbxImportUI()
        opts.import_mesh = True
        opts.import_materials = False
        opts.import_textures = False
        opts.import_as_skeletal = False
        opts.import_animations = False
        opts.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        d = opts.static_mesh_import_data
        d.combine_meshes = True
        d.generate_lightmap_u_vs = False
        d.auto_generate_collision = False
        d.convert_scene = True
        d.convert_scene_unit = True
        d.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        mesh = import_file(source, dest + '/Meshes', name, opts, unreal.FbxFactory())
        assert isinstance(mesh, unreal.StaticMesh)
        assigned = []
        for i, slot in enumerate(mesh.static_materials):
            slotname = str(slot.get_editor_property('imported_material_slot_name'))
            matches = [key for key in materials if slotname == key or slotname.startswith(key + '.') or slotname.startswith(key + '_')]
            assert matches, (name, 'unrecognized material', slotname)
            key = max(matches, key=len)
            mesh.set_material(i, materials[key])
            assigned.append(key)
        b = mesh.get_bounding_box()
        size = b.max - b.min
        actual = [size.x, size.y, size.z]
        expected = [v * 100 for v in row['dimensions_m']]
        assert max(abs(a - e) for a, e in zip(actual, expected)) < .15, (name, actual, expected)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        records.append({'name': row['name'], 'mesh': mesh.get_path_name(), 'dimensions_cm': actual,
                        'bounds_cm': {'min': [b.min.x,b.min.y,b.min.z], 'max': [b.max.x,b.max.y,b.max.z]},
                        'materials': assigned, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'lod_sources': row.get('lods', []), 'traversal': row.get('traversal', {})})
    receipt = {'family': family, 'manifest_sha256': manifest_sha, 'meshes': records, 'materials': material_records,
               'import_dimension_checks_passed': True, 'status': 'imported; placement and runtime validation separate'}
    receipt_path.write_text(json.dumps(receipt, indent=2))
    receipts.append(receipt)
assert receipts, 'No completed pilot manifest available yet'
(OUT / 'imports.json').write_text(json.dumps(receipts, indent=2))
