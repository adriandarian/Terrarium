"""Replace only two pilot meshes with independently validated V2 exports."""
import unreal,json,hashlib
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
path=R/'SourceAssets/Blender/HomesteadPilot/Landscape/revised-manifest.json'
data=json.loads(path.read_text());dest='/Game/Terrarium/HomesteadPilot/Landscape'
tools=unreal.AssetToolsHelpers.get_asset_tools();updates=[]
for row in data['assets']:
 name=row['name'].removesuffix('V2');assert name in ('BroadTree5m','StoneStairs2mRise')
 source=R/row['fbx'];assert source.is_file()
 mesh=unreal.load_asset(dest+'/Meshes/SM_'+name);assert mesh
 materials={str(s.get_editor_property('imported_material_slot_name')):s.get_editor_property('material_interface') for s in mesh.static_materials}
 opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.import_animations=False;opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opts.static_mesh_import_data;d.combine_meshes=True;d.generate_lightmap_u_vs=False;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
 task=unreal.AssetImportTask();task.filename=str(source);task.destination_path=dest+'/Meshes';task.destination_name='SM_'+name;task.automated=True;task.replace_existing=True;task.save=True;task.options=opts;task.factory=unreal.FbxFactory();tools.import_asset_tasks([task])
 mesh=unreal.load_asset(dest+'/Meshes/SM_'+name)
 for i,s in enumerate(mesh.static_materials):
  key=str(s.get_editor_property('imported_material_slot_name'));assert key in materials,key;mesh.set_material(i,materials[key])
 b=mesh.get_bounding_box();size=b.max-b.min;actual=[size.x,size.y,size.z]
 assert max(abs(a-e*100) for a,e in zip(actual,row['dimensions_m']))<.15
 assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 updates.append({'name':name,'mesh':mesh.get_path_name(),'source':str(source),'dimensions_cm':actual,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
(R/'Docs/HomesteadPilot/revision-import.json').write_text(json.dumps(updates,indent=2))
