"""Temporary constant-albedo comparison; restore with setup_grove_materials.py."""
import unreal
from pathlib import Path
assert Path(unreal.Paths.project_dir()).resolve()==Path('C:/Users/hello/Projects/Terrarium')
mat=unreal.load_asset('/Game/Terrarium/Blender/Grove/M_Grove_Soil')
mel=unreal.MaterialEditingLibrary
node=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-700,-250)
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
node.constant=unreal.LinearColor(*[linear(c/255) for c in [115,80,34]],1)
assert mel.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
mel.recompile_material(mat)
