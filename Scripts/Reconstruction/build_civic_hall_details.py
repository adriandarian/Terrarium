"""Build and scope-check the civic hall entrance/foundation refinement in Unreal."""
import importlib
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
import unreal

root=Path(unreal.Paths.project_dir())
revision=7
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
sys.path.insert(0,str(root/'Scripts/Assets'))
sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import architecture,civic_hall_details
importlib.reload(civic_hall_details);importlib.reload(architecture)
old=architecture.civic_hall(entrance_details=False)
new=architecture.civic_hall()
assert len(old.triangles)==155952

def unaffected(m):
    result=Counter()
    for t in m.triangles:
        points=[m.vertices[i] for i in t]
        # Old corner moss clusters include flower tips up to 118.46 cm.
        if any(p[2]<=125 for p in points):continue
        if all(p[1]<-145 and abs(p[0])<160 and p[2]<340 for p in points):continue
        result[tuple(tuple(round(x,6) for x in m.vertices[i]+m.colors[i]) for i in t)]+=1
    return result

old_scope,new_scope=unaffected(old),unaffected(new)
if old_scope!=new_scope:
    (root/'Saved/civic-detail-scope-diff.json').write_text(json.dumps({
        'removed':list((old_scope-new_scope).keys())[:8],
        'added':list((new_scope-old_scope).keys())[:8]}))
assert old_scope==new_scope,'Geometry or colors changed outside the entrance/foundation'
assert new.entrance_foundation_details['moss_contained_in_base_envelope']
assert new.entrance_foundation_details['door_recess_cm']>=50
assert new.entrance_foundation_details['stone_projection_beyond_timber_cm']>0
(root/'Saved/reconstruction-build.json').write_text(json.dumps({'module':'architecture','keys':['civic_hall'],'revision':revision}))
exec(compile((root/'Scripts/Reconstruction/build.py').read_text(),'build.py','exec'),{'__name__':'__main__'})
path=root/('Docs/Reconstruction/Builds/SM_Recon_CivicHall_R'+str(revision)+'.json')
row=json.loads(path.read_text())
row['detail_recipe']='Scripts/Reconstruction/civic_hall_details.py'
row['detail_recipe_sha256']=hashlib.sha256((root/row['detail_recipe']).read_bytes()).hexdigest()
row['geometry_and_colors_outside_entrance_foundation_unchanged']=True
row['visual_acceptance']='pending_user_review_entrance_and_foundation'
path.write_text(json.dumps(row,indent=2))
unreal.log('CIVIC_HALL_ENTRANCE_FOUNDATION_BUILT')
