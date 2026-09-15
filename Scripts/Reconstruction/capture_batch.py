"""Sequential Lit views of the current saved reconstruction receipts."""
import json
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir())
request=json.loads((root/'Saved/reconstruction-capture-batch.json').read_text())
capture_code=(root/'Scripts/Reconstruction/capture.py').read_text()
rows=[json.loads(p.read_text()) for p in (root/'Docs/Reconstruction/Builds').glob('*.json')]
latest={}
for row in rows:
    if row['key'] not in latest or row['revision']>latest[row['key']]['revision']:latest[row['key']]=row
for key in request['keys']:
    row=latest[key]
    if key=='kindlehorn' and row['revision']>=4:
        exec(compile((root/'Scripts/Reconstruction/capture_kindlehorn.py').read_text(),'capture_kindlehorn.py','exec'),{'__name__':'__main__'})
        continue
    if key=='homestead_tree_v2' and row['revision']>=4:
        exec(compile((root/'Scripts/Reconstruction/capture_homestead_tree.py').read_text(),'capture_homestead_tree.py','exec'),{'__name__':'__main__'})
        continue
    if key=='homestead_riverbank_v2' and row['revision']>=4:
        exec(compile((root/'Scripts/Reconstruction/capture_riverbank.py').read_text(),'capture_riverbank.py','exec'),{'__name__':'__main__'})
        continue
    if key=='grove' and row['revision']>=4:
        exec(compile((root/'Scripts/Reconstruction/capture_grove.py').read_text(),'capture_grove.py','exec'),{'__name__':'__main__'})
        continue
    if key=='deep_delver_mark' and row['revision']>=8:
        exec(compile((root/'Scripts/Reconstruction/capture_delver.py').read_text(),'capture_delver.py','exec'),{'__name__':'__main__'})
        continue
    if key=='ember_crest' and row['revision']>=6:
        exec(compile((root/'Scripts/Reconstruction/capture_crest.py').read_text(),'capture_crest.py','exec'),{'__name__':'__main__'})
        continue
    for view in request.get('views',['front']):
        yaw=115 if row['module'] in ['architecture','surfaces'] else 65
        settings={'asset':row['asset'],'name':row['name']+'-'+view,'yaw':yaw if view=='front' else yaw+180,'pitch':-24}
        if row['module']=='compound':settings['pitch']=-30
        if row['module']=='surfaces':settings['pitch']=-55
        (root/'Saved/reconstruction-capture.json').write_text(json.dumps(settings))
        exec(compile(capture_code,'capture.py','exec'),{'__name__':'__main__'})
