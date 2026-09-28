"""Quantify FBX degenerate triangles; no Unreal changes."""
import bpy, json, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'Docs/HomesteadPilot/RemainingArt'
manifest = json.loads((DOC / 'manifest.json').read_text())
rows = []
assert bpy.app.background
for spec in manifest['assets']:
    if spec['name'] not in ('DeepDelverMark', 'Storm'): continue
    for lod in spec['lods']:
        source = ROOT / lod['fbx']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == lod['sha256']
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(source))
        mesh = next(o.data for o in bpy.context.scene.objects if o.type == 'MESH')
        mesh.calc_loop_triangles()
        areas = []; edge_min = []
        for tri in mesh.loop_triangles:
            a,b,c = [mesh.vertices[i].co.copy() for i in tri.vertices]
            areas.append(float((b-a).cross(c-a).length / 2))
            edge_min.append(min((a-b).length, (b-c).length, (c-a).length))
        thresholds = [0, 1e-16, 1e-14, 1e-12, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6]
        tiny = sorted(range(len(areas)), key=lambda i:areas[i])[:80]
        rows.append({'name': spec['name'], 'level': lod['level'], 'fbx_sha256': lod['sha256'],
            'source_triangles': len(areas), 'zero_area_triangles': sum(a == 0 for a in areas),
            'area_thresholds_m2': {str(t):sum(a <= t for a in areas) for t in thresholds},
            'edge_thresholds_m': {str(t):sum(e <= t for e in edge_min) for t in thresholds},
            'smallest_triangles': [{'index':i, 'area_m2':areas[i], 'min_edge_m':edge_min[i],
                'vertices_m':[list(mesh.vertices[v].co) for v in mesh.loop_triangles[i].vertices]} for i in tiny]})
(DOC / 'degenerate-source-diagnostic.json').write_text(json.dumps({'method': 'Independent FBX import; per-loop-triangle area and edge-length analysis in metres', 'assets': rows}, indent=2))
print('DEGENERATE_ANALYSIS', [(r['name'],r['level'],r['zero_area_triangles']) for r in rows])
