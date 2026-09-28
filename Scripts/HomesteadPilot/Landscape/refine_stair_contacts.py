"""Versioned stair correction: core surfaces stop below the stone tread caps."""
import bpy,bmesh,math,random,json,sys,subprocess,hashlib,ast
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium')
assert Path(bpy.context.scene.get('terrarium_project','')).resolve()==ROOT.resolve()
OUT=ROOT/'SourceAssets/Blender/HomesteadPilot/Landscape';DOC=ROOT/'Docs/HomesteadPilot/Landscape'
source=ROOT/'Scripts/HomesteadPilot/Landscape/build_landscape.py';tree_ast=ast.parse(source.read_text())
R=random.Random(4722)
for node in tree_ast.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PALETTE' for t in node.targets):
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),globals())
    if isinstance(node,ast.ClassDef) and node.name=='Mesh' or isinstance(node,ast.FunctionDef) and node.name in ('stairs','write_asset'):
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),globals())
MATERIALS={name:bpy.data.materials.get('M_PilotLandscape_'+name) for name in PALETTE}
TEXTURES={name:str((OUT/'Textures'/(name+'_BaseColor.png')).relative_to(ROOT)).replace('\\','/') for name in PALETTE}
for name in ('StoneShade','Stone','StoneLight','Moss'):assert MATERIALS[name],name
def revised_stair():
    m=stairs();m.name='StoneStairs2mRiseV2';return m
report=write_asset(revised_stair)
manifest=json.loads((OUT/'manifest.json').read_text());manifest['assets']=[report];manifest['source_blend']=[report['blend_path']]
(OUT/'stair-v2-manifest.json').write_text(json.dumps(manifest,indent=2))
(DOC/'stair-v2-manifest.json').write_text(json.dumps(manifest,indent=2))
print('LANDSCAPE_STAIR_CONTACTS_REFINED')
