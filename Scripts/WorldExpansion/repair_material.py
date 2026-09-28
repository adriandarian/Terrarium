"""Coordinator-only repair of private valley material; all graph links checked."""
import json
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
assert not E.get_game_world()
M=unreal.MaterialEditingLibrary
path='/Game/Terrarium/WorldExpansion/Terrain/Materials/M_ValleySculpted'
mat=unreal.load_asset(path);assert mat
texture=unreal.load_asset('/Game/Terrarium/WorldExpansion/Terrain/Textures/T_ValleyMineral');assert texture
M.delete_all_material_expressions(mat)
links=[]
def node(cls,x,y):return M.create_material_expression(mat,cls,x,y)
def link(a,out,b,pin):
    okay=M.connect_material_expressions(a,out,b,pin)
    assert okay,(a.get_class().get_name(),out,b.get_class().get_name(),pin)
    links.append([a.get_class().get_name(),out,b.get_class().get_name(),pin])
def prop(n,p):
    assert M.connect_material_property(n,'',p),str(p)
    links.append([n.get_class().get_name(),'',str(p)])
def constant(value,x,y):
    n=node(unreal.MaterialExpressionConstant,x,y);n.set_editor_property('r',value);return n

# VertexColor's first output is unnamed in this engine binding. 'RGB' silently
# failed in the initial unchecked graph, leaving Multiply A at its zero default.
vc=node(unreal.MaterialExpressionVertexColor,-700,-150)
tex=node(unreal.MaterialExpressionTextureSample,-700,100);tex.texture=texture
strength=constant(.35,-700,340)
scale=node(unreal.MaterialExpressionMultiply,-440,140)
link(tex,'',scale,'A');link(strength,'',scale,'B')
base=constant(.65,-440,340)
lift=node(unreal.MaterialExpressionAdd,-230,140)
link(scale,'',lift,'A');link(base,'',lift,'B')
mul=node(unreal.MaterialExpressionMultiply,0,0)
link(vc,'',mul,'A');link(lift,'',mul,'B')
prop(mul,unreal.MaterialProperty.MP_BASE_COLOR)
prop(constant(.92,0,250),unreal.MaterialProperty.MP_ROUGHNESS)
prop(constant(.12,0,350),unreal.MaterialProperty.MP_SPECULAR)
M.recompile_material(mat)
unreal.EditorAssetLibrary.set_metadata_tag(mat,'TerrariumComplete','2')
unreal.EditorAssetLibrary.set_metadata_tag(mat,'TerrariumGraphLinksVerified',str(len(links)))
assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
receipt={'material':mat.get_path_name(),'cause':'VertexColor unnamed output was addressed as RGB without checking the connection result',
         'graph_connections_checked':links,'material_saved':True,'visual_review':'requires fresh editor capture'}
(ROOT/'Docs/WorldExpansion/material-repair.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
