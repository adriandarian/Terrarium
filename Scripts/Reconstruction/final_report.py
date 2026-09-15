"""Cross-check all current sources, saved receipts, gallery bindings and renders."""
import hashlib,json,struct
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'Docs/Reconstruction'
original=Path('C:/Users/hello/Projects/Pokemon/assets/voxel')
sources=sorted((root/'SourceAssets/Voxel').glob('*.png'));assert len(sources)==77
assert {p.name for p in original.glob('*.png')}=={p.name for p in sources}
for p in sources:assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((original/p.name).read_bytes()).digest(),p.name
latest={}
for p in (out/'Builds').glob('*.json'):
    row=json.loads(p.read_text())
    if row['key'] not in latest or row['revision']>latest[row['key']][1]['revision']:latest[row['key']]=(p,row)
assert len(latest)==72
groups=Counter(row['module'] for _,row in latest.values())
assert dict(groups)=={'architecture':6,'compound':1,'creatures_items':11,'environment':7,'humanoids':2,'surfaces':45},groups
gallery_bindings={}
for category in ['Architecture','Characters','Collectibles','Environment','Surfaces']:
    report=json.loads((out/'Galleries'/(category+'.json')).read_text())
    assert report['all_models_grounded'] and report['all_model_footprints_separate']
    for r in report['models']:
        assert r['key'] not in gallery_bindings
        gallery_bindings[r['key']]=r
    assert (out/'Galleries'/(category+'.png')).exists()
assert len(gallery_bindings)==72
rows=[]
for key,(path,row) in latest.items():
    assert row['saved_normal_errors']==0
    assert row['recipe_sha256']==hashlib.sha256((root/'Scripts/Reconstruction'/(row['module']+'.py')).read_bytes()).hexdigest(),key
    assert (root/'Content'/Path(row['asset'].removeprefix('/Game/')+'.uasset')).exists()
    binding=gallery_bindings[key];assert binding['mesh']==row['asset'] and binding['revision']==row['revision'],key
    assert abs(binding['reopened_ground_error_cm'])<.02
    for view in ['front','back']:
        data=(out/'Renders'/(row['name']+'-'+view+'.png')).read_bytes()
        assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(960,960)
    row['visual_acceptance']='reviewed_original_texture_on_authored_relief' if row['module']=='surfaces' else 'reviewed_reconstruction_not_exact_parity'
    row['visual_review_document']='Docs/Reconstruction/visual-review.md'
    path.write_text(json.dumps(row,indent=2))
    rows.append({'key':key,'asset':row['asset'],'revision':row['revision'],'triangles':row['triangles'],'materials':binding['materials'],'ground_error_cm':binding['reopened_ground_error_cm']})
report={'verified_utc':datetime.now(timezone.utc).isoformat(),'original_pngs':77,'all_original_hashes_match':True,'distinct_models':72,'models_by_module':dict(groups),
        'current_front_renders':72,'current_back_renders':72,'gallery_maps':5,'gallery_model_bindings':72,'all_gallery_bindings_current':True,
        'all_recipe_hashes_current':True,'all_saved_normal_errors_zero':True,'maximum_ground_error_cm':max(abs(r['ground_error_cm']) for r in rows),
        'current_model_triangles':sum(r['triangles'] for r in rows),'visual_review':'Main agent inspected source comparisons, front/back contact sheets and focused full-size captures; visible reconstruction differences remain documented.',
        'exact_source_parity_claimed':False,'rigging_animation_collision_gameplay_tested':False,'models':sorted(rows,key=lambda r:r['key'])}
(out/'verification.json').write_text(json.dumps(report,indent=2))
old=root/'Docs/AssetMigration/asset-map.json';old_data=json.loads(old.read_text())
old_data['historical_prototype_catalog']=True;old_data['superseded_model_catalog']='Docs/Reconstruction/asset-map.json';old_data['superseded_visual_catalog']='Docs/Reconstruction/catalog.html'
old.write_text(json.dumps(old_data,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='models'},indent=2))
