"""Unreal import for a Blender-authored asset with explicit local export receipt."""
import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
key=(root/'Saved/blender-import-asset.txt').read_text().strip();assert key.isalnum()
out=root/'SourceAssets/Blender'/key;dest='/Game/Terrarium/Blender/'+key
receipt=json.loads((root/'Docs/BlenderRebuild'/key/'mesh-validation.json').read_text())
filename='SM_Blender_'+key+'.fbx'
assert hashlib.sha256((out/filename).read_bytes()).hexdigest()==receipt['files'][filename]['sha256']
at=unreal.AssetToolsHelpers.get_asset_tools();textures={}
for kind in ['BaseColor','Emission','Roughness']:
    f=out/(key+'_'+kind+'.png')
    if not f.exists():continue
    task=unreal.AssetImportTask();task.filename=str(f);task.destination_path=dest;task.destination_name='T_'+key+'_'+kind;task.automated=True;task.replace_existing=True;task.save=True
    at.import_asset_tasks([task]);tex=unreal.load_asset(dest+'/T_'+key+'_'+kind);assert tex
    tex.set_editor_property('srgb',kind!='Roughness');textures[kind]=tex
mat=unreal.load_asset(dest+'/M_'+key) or at.create_asset('M_'+key,dest,unreal.Material,unreal.MaterialFactoryNew())
if key in ['MeadowShrub','HomesteadTree','WheatPatch','Riverbank','GrassTerrain','CliffColumn','MossFringe','TrailPatch']:mat.set_editor_property('used_with_instanced_static_meshes',True)
mel=unreal.MaterialEditingLibrary;mel.delete_all_material_expressions(mat)
for kind,tex in textures.items():
    node=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,len(textures)*100);node.texture=tex
    prop={'BaseColor':unreal.MaterialProperty.MP_BASE_COLOR,'Emission':unreal.MaterialProperty.MP_EMISSIVE_COLOR,'Roughness':unreal.MaterialProperty.MP_ROUGHNESS}[kind]
    if kind=='Roughness':node.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
    if kind=='Emission':
        mult=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-180,120)
        strength=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-350,250);strength.r=1.7
        mel.connect_material_expressions(strength,'',mult,'B');mel.connect_material_expressions(node,'RGB',mult,'A');mel.connect_material_property(mult,'',prop)
    else:mel.connect_material_property(node,'R' if kind=='Roughness' else 'RGB',prop)
spec=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-100,300);spec.r=.25;mel.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR);mel.recompile_material(mat)
opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.import_animations=False;opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
d=opts.static_mesh_import_data;d.combine_meshes=True;d.generate_lightmap_u_vs=True;d.auto_generate_collision=True;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
task=unreal.AssetImportTask();task.filename=str(out/filename);task.destination_path=dest;task.destination_name='SM_Blender_'+key;task.automated=True;task.replace_existing=True;task.save=True;task.options=opts;task.factory=unreal.FbxFactory()
at.import_asset_tasks([task]);mesh=unreal.load_asset(dest+'/SM_Blender_'+key);assert isinstance(mesh,unreal.StaticMesh)
for index in range(len(mesh.static_materials)):mesh.set_material(index,mat)
for asset in list(textures.values())+[mat,mesh]:unreal.EditorAssetLibrary.save_loaded_asset(asset)
b=mesh.get_bounding_box();dims=b.max-b.min
expected=[(receipt['bounds_m']['max'][i]-receipt['bounds_m']['min'][i])*100 for i in range(3)]
assert all(abs(v-e)<.05 for v,e in zip([dims.x,dims.y,dims.z],expected)),(str(dims),expected)
report={'asset':key,'mesh':mesh.get_path_name(),'material':mat.get_path_name(),'textures':{k:t.get_path_name() for k,t in textures.items()},'source_fbx_sha256':receipt['files'][filename]['sha256'],'dimensions_cm':[dims.x,dims.y,dims.z],'scale_verified':True,'status':'imported_saved_pending_visual_check'}
report['material_slots']=[{'index':i,'imported_name':str(slot.get_editor_property('imported_material_slot_name')),'material':mesh.get_material(i).get_path_name()} for i,slot in enumerate(mesh.static_materials)]
(root/'Docs/BlenderRebuild'/key/'unreal-import.json').write_text(json.dumps(report,indent=2))
