"""Build only the revised source-aligned cottage roof swatch in Terrarium."""
import hashlib,importlib,json,sys
from pathlib import Path
import unreal
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
root=Path(unreal.Paths.project_dir())
key=globals().get('ROOF_KEY','cottage_roof_tile_v5')
assert key in ('cottage_roof_tile_v5','cottage_roof_tile_v6_candidate')
doc_stem='roof-tile' if key=='cottage_roof_tile_v5' else 'roof-tile-v6'
sys.path.insert(0,str(root/'Scripts/Assets'));sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import roof_surface
importlib.reload(roof_surface)
(root/'Saved/reconstruction-build.json').write_text(json.dumps({'module':'surfaces','keys':[key],'revision':2}))
exec(compile((root/'Scripts/Reconstruction/build.py').read_text(),'build.py','exec'),{'__name__':'__main__'})
path=root/'Docs/Reconstruction/Builds'/('SM_Recon_'+key+'_R2.json')
row=json.loads(path.read_text())
row.update(visual_acceptance='pending_user_review_source_aligned_tiles',
           visual_review_document='Docs/Reconstruction/'+doc_stem+'-review.md',
           detail_recipe='Scripts/Reconstruction/roof_surface.py',
           detail_recipe_sha256=hashlib.sha256((root/'Scripts/Reconstruction/roof_surface.py').read_bytes()).hexdigest())
path.write_text(json.dumps(row,indent=2))
unreal.log('SOURCE_ALIGNED_ROOF_BUILT')
