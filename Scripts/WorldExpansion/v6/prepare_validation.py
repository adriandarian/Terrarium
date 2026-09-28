import json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[3];D=R/'Docs/WorldExpansion/V6'
shutil.copy2(R/'Docs/WorldExpansion/original-baseline.json',D/'original-baseline.json')
cfg=json.loads((R/'Docs/WorldExpansion/V5/traversal-request.json').read_text())
reed=next(r for r in cfg['test_routes'] if r['name']=='Reedbank village street');reed['start_cm']=[28000,-24800,1292];reed['waypoints_cm']=[[28000,-27700,1292],[27200,-29600,1292]];reed['segment_timeout_s']=25
cfg['test_routes'].append({'name':'Civic ramp and raised court','start_cm':[30000,27200,2498],'waypoints_cm':[[30000,28100,2577],[30000,29200,2648]],'xy_tolerance_cm':35,'z_tolerance_cm':35,'segment_timeout_s':20})
cfg['test_routes'].append({'name':'Mill stair descent to landing','start_cm':[5900,-27500,802],'waypoints_cm':[[5740,-28200,522],[5580,-28900,242]],'xy_tolerance_cm':22,'z_tolerance_cm':40,'segment_timeout_s':20})
cfg['test_routes'].append({'name':'Mill stair ascent from landing','start_cm':[5580,-28900,242],'waypoints_cm':[[5740,-28200,522],[5910,-27480,802]],'xy_tolerance_cm':22,'z_tolerance_cm':40,'segment_timeout_s':20})
landmarks=json.loads((D/'landmark-integration.json').read_text())
for path in landmarks['paths']:
 line=path['native_ground_centerline'];points=line[::12]+line[-1:]
 # Travel toward the landmark; stop before structure footprints.
 if path['name']=='MillTrack':points=list(reversed(points))
 if path['name']=='AqueductTrail':points=points[:-2]
 cfg['test_routes'].append({'name':path['name']+' connected approach','start_cm':[points[0][0]*100,points[0][1]*100,points[0][2]*100+98],'waypoints_cm':[[p[0]*100,p[1]*100,p[2]*100+98] for p in points[1:]],'xy_tolerance_cm':45,'z_tolerance_cm':45,'segment_timeout_s':30})
(D/'traversal-request.json').write_text(json.dumps(cfg,indent=2));(D/'snapshot-request.json').write_text('{"name":"admitted"}')
print('Prepared',len(cfg['test_routes']),'routes')
