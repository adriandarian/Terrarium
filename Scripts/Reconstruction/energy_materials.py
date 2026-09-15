"""Opt-in emissive cores selected by reserved palette colors, retaining Lit shading."""
import json,sys
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Assets'));sys.path.insert(0,str(root/'Scripts/Reconstruction'))
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
import meshkit,creatures_items
lib=unreal.MaterialEditingLibrary
palettes=dict(creatures_items.EMISSIVE_COLORS)
palettes['lantern']=['ffe09a','f4bf55','eaa331']
rows={}
for p in (root/'Docs/Reconstruction/Builds').glob('*.json'):
    row=json.loads(p.read_text())
    if row['key'] not in rows or row['revision']>rows[row['key']]['revision']:rows[row['key']]=row
results=[]
for key,colors in palettes.items():
    if not colors:continue
    row=rows[key];name='M_Energy_'+key;folder='/Game/Terrarium/Reconstruction/Materials';path=folder+'/'+name
    mat=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,folder,unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(mat)
    def node(cls,x=0,y=0):return lib.create_material_expression(mat,cls,x,y)
    def connect(a,out,b,pin):assert lib.connect_material_expressions(a,out,b,pin),(key,pin)
    def scalar(value):
        n=node(unreal.MaterialExpressionConstant);n.set_editor_property('r',value);return n
    vc=node(unreal.MaterialExpressionVertexColor,-900,0)
    assert lib.connect_material_property(vc,'',unreal.MaterialProperty.MP_BASE_COLOR)
    mask=None
    for index,h in enumerate(colors):
        target=node(unreal.MaterialExpressionConstant3Vector,-900,200+index*180);target.set_editor_property('constant',unreal.LinearColor(*meshkit.color(h),1))
        distance=node(unreal.MaterialExpressionDistance);connect(vc,'',distance,'A');connect(target,'',distance,'B')
        divide=node(unreal.MaterialExpressionDivide);connect(distance,'',divide,'A');connect(scalar(.04 if key=='lantern' else .008),'',divide,'B')
        saturate=node(unreal.MaterialExpressionSaturate);connect(divide,'',saturate,'')
        inverse=node(unreal.MaterialExpressionOneMinus);connect(saturate,'',inverse,'')
        if mask is None:mask=inverse
        else:
            maximum=node(unreal.MaterialExpressionMax);connect(mask,'',maximum,'A');connect(inverse,'',maximum,'B');mask=maximum
    tinted=node(unreal.MaterialExpressionMultiply);connect(vc,'',tinted,'A');connect(mask,'',tinted,'B')
    strength=node(unreal.MaterialExpressionMultiply);connect(tinted,'',strength,'A');connect(scalar(2.2 if key=='lantern' else 3.2),'',strength,'B')
    assert lib.connect_material_property(strength,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    assert lib.connect_material_property(scalar(.78),'',unreal.MaterialProperty.MP_ROUGHNESS)
    assert lib.connect_material_property(scalar(.18),'',unreal.MaterialProperty.MP_SPECULAR)
    lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    mesh=unreal.load_asset(row['asset']);mesh.set_material(0,mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    results.append({'key':key,'asset':row['asset'],'material':path,'reserved_srgb_colors':colors,'lit_base_color':True,'translucent':False})
(root/'Docs/Reconstruction/energy-materials.json').write_text(json.dumps(results,indent=2))
