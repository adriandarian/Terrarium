"""Import Blender source into Terrarium using Unreal's asset factories."""
import unreal,json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir()).resolve()
assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
OUT=ROOT/'SourceAssets/Blender/Cottage';DEST='/Game/Terrarium/Blender/Cottage'
at=unreal.AssetToolsHelpers.get_asset_tools()
tex=unreal.AssetImportTask();tex.filename=str(OUT/'Cottage_BaseColor.png');tex.destination_path=DEST;tex.destination_name='T_Cottage_BaseColor';tex.automated=True;tex.replace_existing=True;tex.save=True
at.import_asset_tasks([tex])
t=unreal.load_asset(DEST+'/T_Cottage_BaseColor');assert t
t.set_editor_property('srgb',True)
mat=unreal.load_asset(DEST+'/M_Cottage')
if not mat:mat=at.create_asset('M_Cottage',DEST,unreal.Material,unreal.MaterialFactoryNew())
mel=unreal.MaterialEditingLibrary
mel.delete_all_material_expressions(mat)
sample=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0);sample.texture=t
mel.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
rough=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,180);rough.r=.83
mel.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
spec=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,260);spec.r=.24
mel.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
mel.recompile_material(mat)
opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.import_animations=False
opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
data=opts.static_mesh_import_data;data.combine_meshes=True;data.generate_lightmap_u_vs=True;data.auto_generate_collision=True;data.convert_scene=True;data.convert_scene_unit=True
data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
task=unreal.AssetImportTask();task.filename=str(OUT/'SM_Blender_Cottage.fbx');task.destination_path=DEST;task.destination_name='SM_Blender_Cottage';task.automated=True;task.replace_existing=True;task.save=True;task.options=opts;task.factory=unreal.FbxFactory()
at.import_asset_tasks([task])
mesh=unreal.load_asset(DEST+'/SM_Blender_Cottage');assert isinstance(mesh,unreal.StaticMesh),task.imported_object_paths
mesh.set_material(0,mat)
for asset in [t,mat,mesh]:unreal.EditorAssetLibrary.save_loaded_asset(asset)
b=mesh.get_bounding_box();size=b.max-b.min
assert 400<size.x<600 and 400<size.y<600 and 400<size.z<550,str(size)
report={'project':str(ROOT),'engine':unreal.SystemLibrary.get_engine_version(),'imported':list(task.imported_object_paths),'texture':t.get_path_name(),'material':mat.get_path_name(),'bounds_cm':{'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]},'material_slots':len(mesh.static_materials),'lods':mesh.get_num_lods(),'status':'imported_saved_pending_lit_visual_check'}
(ROOT/'Docs/BlenderRebuild/Cottage/unreal-import.json').write_text(json.dumps(report,indent=2))
