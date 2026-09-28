"""One tree-only refinement: embed bark accents into the actual tapered trunk."""
import bpy,bmesh,math,random,json,sys,subprocess,hashlib,ast
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium')
assert Path(bpy.context.scene.get('terrarium_project','')).resolve()==ROOT.resolve()
OUT=ROOT/'SourceAssets/Blender/HomesteadPilot/Landscape';DOC=ROOT/'Docs/HomesteadPilot/Landscape'
source=ROOT/'Scripts/HomesteadPilot/Landscape/build_landscape.py';tree_ast=ast.parse(source.read_text())
R=random.Random(4708)
for node in tree_ast.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PALETTE' for t in node.targets):
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),globals())
    if isinstance(node,ast.ClassDef) and node.name=='Mesh' or isinstance(node,ast.FunctionDef) and node.name in ('cliff','cliff_column','tree','write_asset'):
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),globals())
MATERIALS={name:bpy.data.materials.get('M_PilotLandscape_'+name) for name in PALETTE}
TEXTURES={name:str((OUT/'Textures'/(name+'_BaseColor.png')).relative_to(ROOT)).replace('\\','/') for name in PALETTE}
# Tree source contains its five used materials; append other material dependencies
# from the cliff only if needed by this recipe (all current tree materials exist).
for name in ('Bark','StoneShade','Moss','Leaf','LeafLight','LeafShade'):assert MATERIALS[name],name
cliff();cliff_column() # preserve deterministic random sequence of the original batch
def revised_tree():
    m=tree();m.name='BroadTree5mV2';return m
report=write_asset(revised_tree)
manifest=json.loads((OUT/'manifest.json').read_text());manifest['assets']=[report]
manifest['source_blend']=[report['blend_path']]
(OUT/'tree-v2-manifest.json').write_text(json.dumps(manifest,indent=2))
(DOC/'tree-v2-manifest.json').write_text(json.dumps(manifest,indent=2))
(DOC/'tree-refinement.json').write_text(json.dumps({'pass':2,'change':'Bark accents positioned against actual tapered, leaning trunk; no floating accents','asset':report},indent=2))
print('LANDSCAPE_TREE_CONTACTS_REFINED')
