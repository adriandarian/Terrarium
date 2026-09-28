"""Write finite validation requests from the final authored layout/terrain contract."""
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Docs/WorldExpansion'
layout = json.loads((OUT / 'settlement-layout.json').read_text())
terrain = json.loads((ROOT / 'SourceAssets/WorldExpansion/Terrain/manifest.json').read_text())
spec = importlib.util.spec_from_file_location('terrarium_terrain_source', ROOT / 'Scripts/WorldExpansion/terrain_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Workers supplied clear street centerlines. Short disjoint checks deliberately
# establish local collision coverage rather than claiming inter-settlement travel.
segments = [
    ('Alderhaven south avenue', (300, 170), (300, 185)),
    ('Stonegate gate street', (-320, 315), (-320, 330)),
    ('Brookmere market approach', (-250, 180), (-235, 180)),
    ('Reedbank village street', (280, -345), (280, -330)),
    ('City road rising grade', (43, 65), (59, 65)),
    ('Brookmere road rising grade', (-49, 53), (-61, 52)),
]
routes, probes = [], []
for name, start, end in segments:
    samples = []
    for part, (x, y) in zip(('start', 'end'), (start, end)):
        distance, road_z, width, road_name = module.road_info(x, y)
        # Authored collidable ribbons are 8 cm above the road profile. Elsewhere
        # settlement paving has no collision and the terrain supplies the floor.
        ground_z = road_z + .08 if distance <= width / 2 else module.height_m(x, y)
        ground = [round(x * 100, 4), round(y * 100, 4), round(ground_z * 100, 4)]
        probes.append({'name': name + ' ' + part, 'ground_cm': ground,
                       'height_tolerance_cm': 40, 'minimum_normal_z': .7})
        samples.append([ground[0], ground[1], round(ground[2] + 92, 4)])
    routes.append({'name': name, 'start_cm': samples[0], 'waypoints_cm': [samples[1]],
                   'xy_tolerance_cm': 40, 'z_tolerance_cm': 45, 'segment_timeout_s': 15})


def add_authored_route(name, ground_points_m, timeout=30):
    capsule_points = []
    for index, (x, y, z) in enumerate(ground_points_m):
        ground = [round(x * 100, 4), round(y * 100, 4), round(z * 100, 4)]
        probes.append({'name': name + ' checkpoint ' + str(index), 'ground_cm': ground,
                       'height_tolerance_cm': 40, 'minimum_normal_z': .7})
        capsule_points.append([ground[0], ground[1], round(ground[2] + 92, 4)])
    routes.append({'name': name, 'start_cm': capsule_points[0], 'waypoints_cm': capsule_points[1:],
                   'xy_tolerance_cm': 40, 'z_tolerance_cm': 45, 'segment_timeout_s': timeout})


home_approach = next(r for r in terrain['roads'] if r['name'] == 'HomeApproach')
home_start = home_approach['points'][0]
home_end_xy = (-24, 52)
home_end_road_z = module.road_info(*home_end_xy)[1]
add_authored_route('Home exit to regional road hub',
    [(home_start[0], home_start[1], home_start[2] + .08),
     (home_end_xy[0], home_end_xy[1], home_end_road_z + .08)])
bridge = next(b for b in terrain['bridges'] if b['road'] == 'CityRoad')
a, b = bridge['from_m'], bridge['to_m']
span_length = math.hypot(b[0] - a[0], b[1] - a[1])
assert span_length > 1
points = []
# Two metres before and beyond the bridge establish both transitions; a centre
# waypoint records support above the river. Ribbon top is 8cm above road profile.
for t in (-2 / span_length, .5, 1 + 2 / span_length):
    point = [a[k] + (b[k] - a[k]) * t for k in range(3)]
    point[2] += .08
    points.append(point)
add_authored_route('City river bridge approach span and exit', points)

counts = Counter(row['settlement'] for row in layout['placements'])
request = {'map': layout['map'], 'actor_prefixes': ['WX_'],
    'required_labels': [row['label'] for row in layout['placements']],
    'expected_counts_by_prefix': {'WX_' + name + '_': count for name, count in counts.items()},
    'ground_probes': probes, 'output_tag': 'validation',
    'source': 'Final settlement manifest and analytic terrain road profile; native collision readback is authoritative.'}
request['expected_counts_by_prefix']['WX_Terrain_'] = sum(a['kind'] == 'terrain' for a in terrain['assets'])
dressing_path = OUT / 'settlement-dressing-layout.json'
if dressing_path.exists():
    dressing = json.loads(dressing_path.read_text())
    request['required_labels'].extend(row['label'] for row in dressing['placements'])
    request['expected_counts_by_prefix']['WX_Dressing_'] = len(dressing['placements'])
(OUT / 'validation-request.json').write_text(json.dumps(request, indent=2), encoding='utf-8')
(OUT / 'traversal-request.json').write_text(json.dumps({'test_routes': routes,
    'scope': 'Six short street/road checks plus the home-to-hub approach and complete city river bridge with both bank transitions. The pawn is teleported only to each route initial start.'}, indent=2), encoding='utf-8')
(OUT / 'observation-request.json').write_text(json.dumps({'name': 'idle',
    'scope': 'Fresh default Play; no movement injection, imports, capture or other concurrent profiling.'}, indent=2), encoding='utf-8')
print(json.dumps({'ground_probes': len(probes), 'traversal_routes': len(routes), 'required_actors': len(request['required_labels'])}))
