"""Validate the rear-only recipe change, then build civic hall R5 in Unreal."""
import importlib
import json
import sys
from collections import Counter
from pathlib import Path
import unreal

root=Path(unreal.Paths.project_dir())
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
sys.path.insert(0,str(root/'Scripts/Assets'))
sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import architecture
importlib.reload(architecture)
old=architecture.civic_hall(rear_center_windows=False,entrance_details=False)
new=architecture.civic_hall(entrance_details=False)
assert len(old.triangles)==150672

def unaffected_triangles(m):
    result=Counter()
    for t in m.triangles:
        points=[m.vertices[i] for i in t]
        # Only the two rear facade stories may change.
        if all(p[1]>140 and 100<p[2]<555 for p in points):
            continue
        result[tuple(tuple(round(x,6) for x in m.vertices[i]+m.colors[i]) for i in t)]+=1
    return result

assert unaffected_triangles(old)==unaffected_triangles(new),'Geometry or colors changed outside the rear facade'
(root/'Saved/reconstruction-build.json').write_text(json.dumps({'module':'architecture','keys':['civic_hall'],'revision':5}))
exec(compile((root/'Scripts/Reconstruction/build.py').read_text(),'build.py','exec'),{'__name__':'__main__'})
row=json.loads((root/'Docs/Reconstruction/Builds/SM_Recon_CivicHall_R5.json').read_text())
row['geometry_and_colors_outside_rear_facade_unchanged']=True
row['visual_acceptance']='pending_user_review_rear_center_windows'
(root/'Docs/Reconstruction/Builds/SM_Recon_CivicHall_R5.json').write_text(json.dumps(row,indent=2))
unreal.log('CIVIC_HALL_REAR_WINDOWS_BUILT')
