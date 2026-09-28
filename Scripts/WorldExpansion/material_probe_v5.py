import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/Terrarium/WorldExpansion/TerrainV5/Materials/M_VoxelGrass')
rows={}
for cls in [unreal.MaterialExpressionTextureSampleParameter2D,unreal.MaterialExpressionComponentMask,unreal.MaterialExpressionPower,unreal.MaterialExpressionLinearInterpolate,unreal.MaterialExpressionAbs,unreal.MaterialExpressionSaturate]:
 n=M.create_material_expression(mat,cls)
 rows[cls.__name__]=list(M.get_material_expression_input_names(n))
 M.delete_material_expression(mat,n)
Path(unreal.Paths.project_dir(),'Docs/WorldExpansion/V5/material-inputs.json').write_text(json.dumps(rows,default=str,indent=2))
