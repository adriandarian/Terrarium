"""Import the source material alternatives without changing world assignments."""
import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
record=json.loads((root/'Docs/BlenderRebuild/SurfaceLibrary/materials.json').read_text());dest='/Game/Terrarium/Blender/SurfaceLibrary'
at=unreal.AssetToolsHelpers.get_asset_tools();mel=unreal.MaterialEditingLibrary;rows=[];materials={}
for row in record['materials']:
    source=root/'SourceAssets/Voxel'/row['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
    stem=source.stem;task=unreal.AssetImportTask();task.filename=str(source);task.destination_path=dest;task.destination_name='T_Source_'+stem;task.automated=True;task.save=True;task.replace_existing=True
    at.import_asset_tasks([task]);tex=unreal.load_asset(dest+'/T_Source_'+stem);assert tex
    tex.set_editor_property('srgb',True)
    name='M_Source_'+stem;mat=unreal.load_asset(dest+'/'+name) or at.create_asset(name,dest,unreal.Material,unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    node=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0);node.texture=tex;mel.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
    rough=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,160);rough.r=.22 if 'water' in stem else .82;mel.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    for asset in [tex,mat]:unreal.EditorAssetLibrary.save_loaded_asset(asset)
    materials[name]=mat;rows.append({'source':row['source'],'material':mat.get_path_name(),'texture':tex.get_path_name(),'srgb':tex.get_editor_property('srgb'),'status':'saved_material_alternative'})
opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.import_animations=False;opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
opts.static_mesh_import_data.combine_meshes=False;opts.static_mesh_import_data.generate_lightmap_u_vs=True
task=unreal.AssetImportTask();task.filename=str(root/'SourceAssets/Blender/SurfaceLibrary/SurfaceLibrary.fbx');task.destination_path=dest+'/Samples';task.automated=True;task.replace_existing=True;task.save=True;task.options=opts;task.factory=unreal.FbxFactory()
at.import_asset_tasks([task]);samples=[]
for path in task.imported_object_paths:
    mesh=unreal.load_asset(path)
    if not isinstance(mesh,unreal.StaticMesh):continue
    assert len(mesh.static_materials)==1
    name=str(mesh.static_materials[0].get_editor_property('imported_material_slot_name'));assert name in materials,name
    mesh.set_material(0,materials[name]);unreal.EditorAssetLibrary.save_loaded_asset(mesh);samples.append({'mesh':mesh.get_path_name(),'material':materials[name].get_path_name()})
assert len(samples)==45,len(samples)
(root/'Docs/BlenderRebuild/SurfaceLibrary/unreal-import.json').write_text(json.dumps({'materials':rows,'samples':samples,'material_count':len(rows),'sample_count':len(samples),'world_material_assignments_changed':False},indent=2))
