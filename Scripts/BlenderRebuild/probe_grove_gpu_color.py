"""Read the color atlas through Unreal's shader path into a floating-point target.

Temporarily connects soil albedo to emission; restore setup_grove_materials.py.
"""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mel=unreal.MaterialEditingLibrary;mat=unreal.load_asset('/Game/Terrarium/Blender/Grove/M_Grove_Soil')
tx=mel.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
assert mel.connect_material_property(tx,'RGB' if isinstance(tx,unreal.MaterialExpressionTextureSample) else '',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat)
rt=unreal.RenderingLibrary.create_render_target2d(world,256,256,unreal.TextureRenderTargetFormat.RTF_RGBA32F)
unreal.RenderingLibrary.draw_material_to_render_target(world,rt,mat)
rows=[]
for index in [0,5,6,8,12,13,14,15]:
    x=(index%8)*32+16;y=(7-index//8)*32+16
    c=unreal.RenderingLibrary.read_render_target_raw_pixel(world,rt,x,y,False)
    rows.append({'palette_index':index,'pixel':[x,y],'linear_rgb':[c.r,c.g,c.b]})
(root/'Docs/BlenderRebuild/Grove/gpu-color-probe.json').write_text(json.dumps(rows,indent=2))
