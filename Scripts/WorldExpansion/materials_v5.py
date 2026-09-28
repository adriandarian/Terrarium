"""Admit imagegen albedos and build private physical-scale terrain materials."""
import json, hashlib
from pathlib import Path
import unreal
R=Path(unreal.Paths.project_dir()).resolve()
assert R==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not E.get_game_world()
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
DEST='/Game/Terrarium/WorldExpansion/TerrainV5'
AT=unreal.AssetToolsHelpers.get_asset_tools(); M=unreal.MaterialEditingLibrary
D=R/'Docs/WorldExpansion/V5';D.mkdir(exist_ok=True)
textures={};records=[]
for key,name in [('grass','T_VoxelMeadow'),('stone','T_MossLimestone'),('path','T_OchreGravel')]:
    source=R/'SourceAssets/WorldExpansion/ArtDirection'/f'{name}.png'
    path=DEST+'/Textures/'+name
    texture=unreal.load_asset(path)
    if not texture:
        task=unreal.AssetImportTask();task.filename=str(source);task.destination_path=DEST+'/Textures'
        task.destination_name=name;task.automated=True;task.save=True
        AT.import_asset_tasks([task]);texture=unreal.load_asset(path)
    assert texture
    texture.set_editor_property('srgb',True)
    texture.set_editor_property('address_x',unreal.TextureAddress.TA_WRAP)
    texture.set_editor_property('address_y',unreal.TextureAddress.TA_WRAP)
    # Retain mipmaps for stable world-scale detail, with anisotropic filtering.
    texture.set_editor_property('filter',unreal.TextureFilter.TF_DEFAULT)
    # Built-in imagegen returned 1254 square; native resampling preserves wrapping
    # and enables a full mip chain without modifying the generated source PNG.
    texture.set_editor_property('power_of_two_mode',unreal.TexturePowerOfTwoSetting.STRETCH_TO_POWER_OF_TWO)
    texture.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP)
    unreal.EditorAssetLibrary.set_metadata_tag(texture,'TerrariumImagegenSourceSHA256',hashlib.sha256(source.read_bytes()).hexdigest())
    assert unreal.EditorAssetLibrary.save_loaded_asset(texture)
    textures[key]=texture
    records.append({'source_file':str(source),'texture':texture.get_path_name(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})

materials={};graphs=[]
for kind,name in [('grass','M_VoxelGrass'),('stone','M_VoxelStone'),('path','M_VoxelPath'),('ground','M_VoxelGround')]:
    mat=unreal.load_asset(DEST+'/Materials/'+name) or AT.create_asset(name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    links=[]
    def node(cls):return M.create_material_expression(mat,cls)
    def link(a,b,pin,out=''):
        assert M.connect_material_expressions(a,out,b,pin),(name,pin,out)
        links.append([a.get_class().get_name(),out,b.get_class().get_name(),pin])
    def const(v):
        n=node(unreal.MaterialExpressionConstant);n.set_editor_property('r',v);return n
    def colorconst(r,g,b):
        n=node(unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(r,g,b,1));return n
    def op(cls,a,b):
        n=node(cls);link(a,n,'A');link(b,n,'B');return n
    def mask(a,channels):
        n=node(unreal.MaterialExpressionComponentMask)
        for channel in 'rgba':n.set_editor_property(channel,channel in channels)
        link(a,n,'');return n
    def sample(key,uv,parameter):
        n=node(unreal.MaterialExpressionTextureSampleParameter2D);n.set_editor_property('parameter_name',parameter)
        n.set_editor_property('texture',textures[key]);link(uv,n,'UVs');return n
    def lerp(a,b,t):
        n=node(unreal.MaterialExpressionLinearInterpolate);link(a,n,'A');link(b,n,'B');link(t,n,'Alpha');return n
    def saturate(a):
        n=node(unreal.MaterialExpressionSaturate);link(a,n,'');return n
    position=node(unreal.MaterialExpressionWorldPosition)
    coord=op(unreal.MaterialExpressionDivide,position,const(200))
    xy=mask(coord,'rg');xz=mask(coord,'rb');yz=mask(coord,'gb')
    normal=node(unreal.MaterialExpressionVertexNormalWS)
    absn=node(unreal.MaterialExpressionAbs);link(normal,absn,'')
    z=mask(absn,'b')
    if kind in ('ground','stone'):
        power=node(unreal.MaterialExpressionPower);link(absn,power,'Base');link(const(8),power,'Exp')
        wx,wy,wz=[mask(power,c) for c in 'rgb']
        total=op(unreal.MaterialExpressionAdd,op(unreal.MaterialExpressionAdd,wx,wy),wz)
        rock=op(unreal.MaterialExpressionDivide,
            op(unreal.MaterialExpressionAdd,
                op(unreal.MaterialExpressionAdd,op(unreal.MaterialExpressionMultiply,sample('stone',yz,'LimestoneX'),wx),op(unreal.MaterialExpressionMultiply,sample('stone',xz,'LimestoneY'),wy)),
                op(unreal.MaterialExpressionMultiply,sample('stone',xy,'LimestoneZ'),wz)),total)
    if kind in ('grass','ground'):
        grass_uv=op(unreal.MaterialExpressionDivide,xy,const(4))
        grass=sample('grass',grass_uv,'Meadow')
        # Wide natural color changes, separate from 2m fine detail.
        macro_uv=op(unreal.MaterialExpressionDivide,xy,const(30))
        macro=sample('grass',macro_uv,'MeadowMacro')
        tone=mask(macro,'g')
        factor=op(unreal.MaterialExpressionAdd,const(.75),op(unreal.MaterialExpressionMultiply,tone,const(1.25)))
        grass=op(unreal.MaterialExpressionMultiply,grass,factor)
        grass=op(unreal.MaterialExpressionMultiply,grass,colorconst(.66,.82,.50))
        grass=lerp(colorconst(.10,.135,.028),grass,const(.52))
    if kind=='ground':
        slope=saturate(op(unreal.MaterialExpressionMultiply,op(unreal.MaterialExpressionSubtract,const(.94),z),const(3.2)))
        color=lerp(grass,rock,slope)
    elif kind=='stone':color=rock
    elif kind=='grass':color=grass
    else:color=lerp(colorconst(.37,.27,.095),sample('path',op(unreal.MaterialExpressionDivide,xy,const(2)),'Gravel'),const(.46))
    assert M.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
    assert M.connect_material_property(const(.95),'',unreal.MaterialProperty.MP_ROUGHNESS)
    assert M.connect_material_property(const(.1),'',unreal.MaterialProperty.MP_SPECULAR)
    M.layout_material_expressions(mat);M.recompile_material(mat)
    unreal.EditorAssetLibrary.set_metadata_tag(mat,'TerrariumImagegenAlbedo','true')
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    materials[kind]=mat
    graphs.append({'material':mat.get_path_name(),'links_checked':len(links),'texture_parameters':[str(x) for x in M.get_texture_parameter_names(mat)]})

bindings=[]
for actor in A.get_all_level_actors():
    label=actor.get_actor_label()
    if not label.startswith('WX_'):continue
    for c in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh=c.static_mesh
        if not mesh:continue
        path=mesh.get_path_name()
        if '/WorldExpansion/Terrain/' not in path:continue
        if 'Water' in path or 'River' in path or 'Tributary' in path:continue
        if 'Road' in path or 'Approach' in path:kind='path'
        elif 'Terrain_' in path or 'HomeApron' in path:kind='ground'
        else:continue
        c.set_material(0,materials[kind]);bindings.append({'actor':label,'material':materials[kind].get_path_name()})
assert L.save_current_level()
receipt={'textures':records,'materials':graphs,'bindings':bindings,'mode':'built-in image_gen','tile_size_m':{'stone':2,'grass':8,'path':4},'get_used_textures_available':hasattr(M,'get_used_textures')}
(D/'imagegen-materials.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({'textures':len(records),'materials':len(graphs),'bindings':len(bindings)}))


