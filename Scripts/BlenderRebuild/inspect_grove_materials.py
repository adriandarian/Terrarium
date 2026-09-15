"""Record imported color settings and current materials for the Grove mismatch."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
base='/Game/Terrarium/Blender/Grove';rows=[]
for kind in ['BaseColor','Roughness','Emission']:
    tex=unreal.load_asset(base+'/T_Grove_'+kind)
    props={}
    for name in ['srgb','compression_settings','adjust_brightness','adjust_saturation','adjust_rgb_curve','adjust_brightness_curve','lod_group','source_color_settings']:
        props[name]=str(tex.get_editor_property(name))
    rows.append({'kind':kind,'properties':props})
    if kind=='BaseColor':
        task=unreal.AssetExportTask();task.object=tex;task.filename=str(root/'Docs/BlenderRebuild/Grove/unreal-imported-basecolor.png')
        task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.TextureExporterPNG()
        assert unreal.Exporter.run_asset_export_task(task)
materials=[]
for role in ['Leaf','Stem','Soil']:
    mat=unreal.load_asset(base+'/M_Grove_'+role);pins={}
    for name,prop in [('BaseColor',unreal.MaterialProperty.MP_BASE_COLOR),('Roughness',unreal.MaterialProperty.MP_ROUGHNESS)]:
        node=unreal.MaterialEditingLibrary.get_material_property_input_node(mat,prop)
        pins[name]={'node':node.get_path_name(),'texture':node.texture.get_path_name(),'sampler':str(node.sampler_type)}
    materials.append({'role':role,'pins':pins})
(root/'Docs/BlenderRebuild/Grove/texture-settings.json').write_text(json.dumps({'textures':rows,'materials':materials},indent=2))
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'viewmode lit')
