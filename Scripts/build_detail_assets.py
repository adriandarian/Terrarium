"""Build every used scene asset as a new native detailed version, sequentially."""
import unreal,sys,json,importlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/DetailPass'
sys.path.insert(0,str(root/'Scripts/Assets'))
import meshkit,detail_enrichment
importlib.reload(detail_enrichment)
specs=[('cottage_v6','build',()),('shed_v2','build',()),('plank_bridge_v4','build',()),
 ('garden_well_v2','build',()),('garden_v3','build',()),('garden_v2','build',()),
 ('lantern_post','build',()),('fence_post','build',()),('fence_rail','build',()),
 ('traveler_v2','build',()),('meadow_v5','build',()),('meadow_edge_v6','build',()),
 ('tree_v3','build',()),('bush_v2','build',()),('wheat_v2','build',()),
 ('ground_plants_v2','recipe',('grass',)),('ground_plants_v2','recipe',('flowers',)),
 ('ground_plants_v2','recipe',('fern',)),('cliff_moss_v1','build',()),
 ('cliff_column_v6','recipe',('A',)),('cliff_column_v6','recipe',('B',)),('cliff_column_v6','recipe',('C',)),
 ('stairs_v3','build',()),('rock_cluster','build',()),('shore_outcrop','build',()),
 ('shore_outcrop_v2','build',()),('river_stones_v2','build',()),('reeds','build',()),
 ('path_v4','build',()),('water_v4','recipe',('medium',)),('water_v4','recipe',('shallow',)),('water_v4','recipe',('deep',))]
reports=[]
for module,method,args in specs:
    original_save=meshkit.Mesh.save
    try:
        meshkit.Mesh.save=lambda self:self
        mod=importlib.import_module(module);importlib.reload(mod)
        m=getattr(mod,method)(*args)
        assert isinstance(m,meshkit.Mesh)
    finally:meshkit.Mesh.save=original_save
    report=detail_enrichment.enrich(m)
    path='/Game/Terrarium/Meshes/'+m.name
    if not unreal.EditorAssetLibrary.does_asset_exist(path):m.save()
    evidence=json.loads((root/'Docs/Phase1/Validation'/(m.name+'.json')).read_text())
    assert evidence['saved_normal_errors']==0
    reports.append(report)
    (out/'assets.json').write_text(json.dumps(reports,indent=2))
    unreal.log('DETAIL_ASSET_BUILT '+m.name)
expected={n for n in json.loads((out/'restored.json').read_text())['counts'] if n.startswith('SM_')}
assert expected=={r['original'] for r in reports},expected^{r['original'] for r in reports}
unreal.log('ALL_32_DETAIL_ASSETS_BUILT')
