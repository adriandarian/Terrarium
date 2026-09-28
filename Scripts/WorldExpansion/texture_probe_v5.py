import unreal,json
from pathlib import Path
names=[x for x in dir(unreal.TexturePowerOfTwoSetting) if x.isupper()]
t=unreal.load_asset('/Game/Terrarium/WorldExpansion/TerrainV5/Textures/T_VoxelMeadow')
props={}
for key in ['power_of_two_mode','mip_gen_settings','never_stream','filter','lod_group']:
 try:props[key]=str(t.get_editor_property(key))
 except Exception as e:props[key]=str(e)
Path(unreal.Paths.project_dir(),'Docs/WorldExpansion/V5/texture-settings.json').write_text(json.dumps({'modes':names,'properties':props},indent=2))
