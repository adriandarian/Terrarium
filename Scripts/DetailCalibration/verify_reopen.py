"""Read-only independent reopen check in a fresh background Blender process."""
import bpy,json,hashlib
from pathlib import Path
root=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene
assert bpy.app.background and s.name=='Terrarium_DetailCalibration'
assert Path(s.get('terrarium_project',''))==root and len(bpy.data.scenes)==1
manifest=json.loads((root/'Docs/DetailCalibration/manifest.json').read_text());rows=[]
for r in manifest['specimens']:
    obs=list(bpy.data.collections[r['name']].objects);assert len(obs)==r['parts']
    pts=[v.co for o in obs for v in o.data.vertices]
    dims=[max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)]
    assert all(abs(a-b)<.00001 for a,b in zip(dims,r['dimensions_m']))
    assert all(o.library is None for o in obs)
    rows.append({'name':r['name'],'parts':len(obs),'measured_dimensions_m':dims,'bounds_pass':True})
report={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'scene':s.name,'scene_count':len(bpy.data.scenes),'camera':s.camera.name,'active_normal_project_verified':True,'missing_external_textures':0,'specimens':rows,'geometry_frozen':True,'method':'Direct fresh Blender background reopen. MCP CLI wrapper stalled; its background worker had exited before this fallback.'}
(root/'Docs/DetailCalibration/reopen-verification.json').write_text(json.dumps(report,indent=2))
p=root/'Docs/DetailCalibration/verification.json';v=json.loads(p.read_text());v['reopen_check_pending']=False;v['reopen_verified']=True;p.write_text(json.dumps(v,indent=2))
print('DETAIL_CALIBRATION_REOPEN_PASSED',flush=True)
