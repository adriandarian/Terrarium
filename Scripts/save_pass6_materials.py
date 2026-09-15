import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
for name in ['M_WeatheredDetails','M_QuietRiverPalette','M_MeadowAltitudePalette']:
    assert unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset('/Game/Terrarium/Materials/'+name))
