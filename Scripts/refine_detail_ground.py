"""Keep tile surface detail shallow so paths remain clear and turf is not dotted."""
import unreal,sys,json,importlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/DetailPass'
sys.path.insert(0,str(root/'Scripts/Assets'))
import meshkit,detail_enrichment
importlib.reload(detail_enrichment)
manifest=json.loads((out/'assets.json').read_text())
for name in ('meadow_v5','meadow_edge_v6'):
    save=meshkit.Mesh.save
    try:
        meshkit.Mesh.save=lambda self:self
        module=importlib.import_module(name);importlib.reload(module);m=module.build()
    finally:meshkit.Mesh.save=save
    report=detail_enrichment.enrich(m);m.name+='2';report['asset']=m.name
    if not unreal.EditorAssetLibrary.does_asset_exist('/Game/Terrarium/Meshes/'+m.name):mesh=m.save()
    else:mesh=unreal.load_asset('/Game/Terrarium/Meshes/'+m.name)
    ft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+report['original'][3:]+'_Detail')
    ft.set_editor_property('mesh',mesh);unreal.EditorAssetLibrary.save_loaded_asset(ft)
    manifest=[report if item['original']==report['original'] else item for item in manifest]
(out/'assets.json').write_text(json.dumps(manifest,indent=2))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('DETAIL_GROUND_REFINED')
