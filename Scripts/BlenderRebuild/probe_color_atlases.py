"""Sample imported atlases through a transient material, leaving production shaders intact."""
import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
args=json.loads((root/'Saved/color-atlas-probe-args.json').read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mel=unreal.MaterialEditingLibrary;rows=[]
for key in args['assets']:
    tex=unreal.load_asset(f'/Game/Terrarium/Blender/{key}/T_{key}_BaseColor');assert tex
    mat=unreal.new_object(unreal.Material)
    tx=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0);tx.texture=tex
    assert mel.connect_material_property(tx,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    rt=unreal.RenderingLibrary.create_render_target2d(world,256,256,unreal.TextureRenderTargetFormat.RTF_RGBA32F)
    unreal.RenderingLibrary.draw_material_to_render_target(world,rt,mat)
    samples=[]
    for index in range(32):
        x=index%8*32+16;y=(7-index//8)*32+16
        c=unreal.RenderingLibrary.read_render_target_raw_pixel(world,rt,x,y,False)
        samples.append({'index':index,'source_pixel':[x*2+1,y*2+1],'linear_rgb':[c.r,c.g,c.b]})
    png=root/f'SourceAssets/Blender/{key}/{key}_BaseColor.png'
    rows.append({'asset':key,'srgb':tex.get_editor_property('srgb'),'source_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'source_bit_depth':png.read_bytes()[24],'samples':samples})
out=root/'Docs/BlenderRebuild/ColorManagement'/args['output'];out.write_text(json.dumps(rows,indent=2))
