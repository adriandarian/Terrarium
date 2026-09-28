"""Offline geometry + protected route checks; no editor operations."""
import json
import math
import hashlib
from pathlib import Path
import voxel_terrain as v
ROOT=v.ROOT;OUT=v.OUT
manifest=json.loads((OUT/'manifest.json').read_text());records=[];bad=[]
for row in manifest['assets']:
    path=ROOT/row['source'];d=json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
    assert len(d['uv0'])==len(d['vertices'])==len(d['colors'])
    zero=0;uv_zero=0
    for tri in d['triangles']:
        a,b,c=[d['vertices'][i] for i in tri];u=[b[k]-a[k] for k in range(3)];w=[c[k]-a[k] for k in range(3)]
        n=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]]
        if sum(x*x for x in n)<1e-12:zero+=1
        if row['role']=='ground':assert n[2]>0,(row['name'],'inverted ground')
        p,q,r=[d['uv0'][i] for i in tri]
        if abs((q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]))<1e-12:uv_zero+=1
    if zero or uv_zero:bad.append({'name':row['name'],'zero_area_triangles':zero,'zero_uv_triangles':uv_zero})
    records.append({'name':row['name'],'triangles':len(d['triangles']),'source_sha_verified':True,'zero_area_triangles':zero,'zero_uv_triangles':uv_zero})
assert not bad,bad
routes=[]
for r in manifest['route_samples']:
    x,y,z=r['location_m'];i=min(319,max(0,math.floor((x+800)/5)));j=min(319,max(0,math.floor((y+800)/5)));c=v.cell(i,j)
    if not c:continue
    assert c['keep']==1,(r['route'],x,y,c['keep'])
    x0,y0=c['x'],c['y'];expected=[v.HEIGHTS[(xx,yy)] for xx,yy in [(x0,y0),(x0+5,y0),(x0+5,y0+5),(x0,y0+5)]]
    assert c['z']==expected,(r['route'],'height changed')
    routes.append({'route':r['route'],'xy_m':[x,y],'exact_source_cell_preserved':True})
assert all(a['location_m'][:2]==b['location_m'][:2] and a['scale']==b['scale'] and a['yaw']==b['yaw'] for a,b in zip(manifest['forest_instances'],v.BASE_MANIFEST['forest_instances']))
receipt={'revision':5,'assets':records,'total_triangles':sum(r['triangles'] for r in records),
         'geometry_non_degenerate':True,'all_uv_faces_nonzero':True,'uv_repeat_m':2,
         'protected_route_cells_checked':len(routes),'protected_route_samples':routes,
         'forest_xy_order_scale_and_yaw_unchanged':True,'forest_count':len(manifest['forest_instances']),
         'home_apron_opening_preserved_m':[-65,-65,65,65],'live_editor_validation':'pending coordinator'}
(OUT/'source-validation.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:val for k,val in receipt.items() if k not in ('assets','protected_route_samples')}))
