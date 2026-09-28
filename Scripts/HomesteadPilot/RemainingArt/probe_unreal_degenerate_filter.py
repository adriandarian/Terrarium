"""Coordinator-only A/B native import probe; admitted assets remain untouched.

Imports four small FBXs into unique temporary packages without saving. The only
intentional geometry-build difference is remove_degenerates=False. Counts are
compared with the admitted native meshes, whose build settings use True. Every
temporary asset is deleted in finally; only the JSON evidence is retained.
"""
import unreal, json, hashlib, uuid
from pathlib import Path
ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
DOC = ROOT / 'Docs/HomesteadPilot/RemainingArt'
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
at = unreal.AssetToolsHelpers.get_asset_tools()
dest = '/Game/Terrarium/HomesteadPilot/RemainingArt/Diagnostics'
manifest = json.loads((DOC / 'manifest.json').read_text())
rows = []
for spec in manifest['assets']:
    if spec['name'] not in ('DeepDelverMark', 'Storm'): continue
    admitted = unreal.load_asset('/Game/Terrarium/HomesteadPilot/RemainingArt/Meshes/SM_HP_' + spec['name'])
    assert admitted
    for lod in spec['lods']:
        if lod['level'] == 2: continue
        source = ROOT / lod['fbx']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == lod['sha256']
        opts = unreal.FbxImportUI(); opts.import_mesh = True; opts.import_materials = False
        opts.import_textures = False; opts.import_as_skeletal = False; opts.import_animations = False
        opts.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        d = opts.static_mesh_import_data
        d.combine_meshes = True; d.generate_lightmap_u_vs = False; d.auto_generate_collision = False
        d.convert_scene = True; d.convert_scene_unit = True; d.remove_degenerates = False
        d.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        name = 'SM_FilterProbe_' + spec['name'] + '_' + str(lod['level']) + '_' + uuid.uuid4().hex[:8]
        path = dest + '/' + name
        assert not unreal.EditorAssetLibrary.does_asset_exist(path)
        temporary = None
        try:
            task = unreal.AssetImportTask(); task.filename = str(source); task.destination_path = dest
            task.destination_name = name; task.automated = True; task.replace_existing = False; task.save = False
            task.options = opts; task.factory = unreal.FbxFactory(); at.import_asset_tasks([task])
            temporary = unreal.load_asset(path); assert temporary
            no_filter = temporary.get_num_triangles(0)
            filtered = admitted.get_num_triangles(lod['level'])
            assert not sub.get_lod_build_settings(temporary, 0).get_editor_property('remove_degenerates')
            assert sub.get_lod_build_settings(admitted, lod['level']).get_editor_property('remove_degenerates')
            assert no_filter >= filtered
            rows.append({'name': spec['name'], 'level': lod['level'], 'source_sha256': lod['sha256'],
                'source_triangles': lod['triangles'], 'native_without_degenerate_filter': no_filter,
                'native_with_degenerate_filter': filtered, 'native_removed_triangles': no_filter-filtered,
                'unfiltered_matches_source': no_filter == lod['triangles'],
                'admitted_asset_unchanged': True})
        finally:
            if temporary: assert unreal.EditorAssetLibrary.delete_loaded_asset(temporary), path
        rows[-1]['temporary_asset_deleted'] = not unreal.EditorAssetLibrary.does_asset_exist(path)
        assert rows[-1]['temporary_asset_deleted']
        (DOC / 'native-degenerate-filter-probe.json').write_text(json.dumps({'method': 'Unreal FBX native A/B import: admitted filter=True versus temporary filter=False; no admitted asset edited', 'assets': rows}, indent=2))
        unreal.log('Degenerate filter probe %s LOD%d: %d -> %d' % (spec['name'], lod['level'], no_filter, filtered))
assert len(rows) == 4
