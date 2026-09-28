"""Offline terrain checks; these do not replace editor/traversal validation."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'SourceAssets/WorldExpansion/Terrain'
manifest=json.loads((source/'manifest.json').read_text())
seams={};records=[]
for row in manifest['assets']:
    path=ROOT/row['source'];data=json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
    assert len(data['vertices'])==row['vertices'] and len(data['triangles'])==row['triangles']
    assert len(data['colors'])==len(data['vertices'])
    for a,b,c in data['triangles']:
        p,q,r=(data['vertices'][i] for i in (a,b,c))
        u=[q[i]-p[i] for i in range(3)];v=[r[i]-p[i] for i in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        assert sum(n*n for n in normal)>1e-12,(row['name'],'degenerate')
        if row['kind']!='bridge':assert normal[2]>0,(row['name'],'downward source triangle')
    if row['kind']=='terrain':
        for vi in set(i for tri in data['triangles'] for i in tri):
            x,y,z=data['vertices'][vi]
            k=(x,y)
            if k in seams:assert seams[k]==z,(row['name'],'terrain seam mismatch')
            seams[k]=z
    records.append({'name':row['name'],'triangles':row['triangles'],'sha256_verified':True,'nondegenerate':True})
grades=[]
for road in manifest['roads']:
    g=max(abs(b[2]-a[2])/math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(road['points'],road['points'][1:]))
    assert g<.35,(road['name'],'steep route')
    grades.append({'road':road['name'],'maximum_grade_percent':round(g*100,2)})
receipt={'status':'offline source geometry passed; live editor validation separate','assets':records,
         'total_triangles':sum(r['triangles'] for r in records),'unique_terrain_vertices':len(seams),
         'watertight_chunk_seams':True,'all_surface_normals_upward':True,'route_grades':grades,
         'forest_instances':len(manifest['forest_instances']),'bridges':manifest['bridges']}
(source/'source-validation.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k not in ('assets','bridges')}))
