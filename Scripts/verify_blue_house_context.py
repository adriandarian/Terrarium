"""Save/reopen and scope verification for the blue-house ground correction."""
import unreal,json,re,sys,gc
from pathlib import Path
from collections import defaultdict
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/BlueHouseContext'
sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='HouseFence_Review_Transient':actors.destroy_actor(a)
a=None;c=None;camera=None;review=None;baseline=None;world=None;gc.collect()
def snapshot():
    all_rows=defaultdict(list);outside=defaultdict(list);shed=None
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            name=c.static_mesh.get_name()
            if name=='MatineeCam_SM':continue
            ts=[c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count())] if isinstance(c,unreal.InstancedStaticMeshComponent) else [a.get_actor_transform()]
            for t in ts:
                tr=tuple(float(v) for v in re.findall(r'[xyzw]: (-?\d+\.\d+)',str(t)))
                assert len(tr)==10
                row=(c.get_material(0).get_path_name(),tr);all_rows[name].append(row)
                p=t.translation;px,py=ref.pixel(p.x,p.y,560)
                if not (99<px<173 and 307<py<378 and abs(p.z-560)<30):outside[name].append(row)
                if name.startswith('SM_Shed_') and 'FlatStones' not in name:shed=row
    return {k:sorted(v) for k,v in all_rows.items()},{k:sorted(v) for k,v in outside.items()},shed
before,_,shed_before=snapshot();assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadBeforeBlueHouseContext')
original,outside_original,original_shed=snapshot()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
after,outside_after,final_shed=snapshot()
assert before==after,'Save/reopen changed state'
assert original_shed==final_shed,'Shed transform or material changed'
scope_diff={}
for name in set(outside_original)|set(outside_after):
    old=outside_original.get(name,[]);new=outside_after.get(name,[])
    if old!=new:scope_diff[name]={'removed':[r for r in old if r not in new][:4],'added':[r for r in new if r not in old][:4]}
(out/'scope-diff.json').write_text(json.dumps(scope_diff,indent=2))
assert outside_original==outside_after,'An object outside the blue-house region changed'
terrain=[n for n in original if n.startswith(('SM_MeadowTile','SM_Cliff','SM_Water'))]
assert all(original[n]==after[n] for n in terrain),'Underlying terrain changed'
geometry={}
for name in ('SM_Shed_Context_Reference','SM_Shed_FlatStones'):
    r=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
    assert r['saved_normal_errors']==0 and r['all_components_closed']
    geometry[name]={'triangles':r['triangles'],'saved_normal_errors':0}
(out/'verification.json').write_text(json.dumps({'saved_reopened':True,'outside_region_unchanged':True,
 'underlying_terrain_unchanged':True,'shed_transform_and_material_preserved':True,'geometry':geometry},indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
unreal.log('BLUE_HOUSE_CONTEXT_VERIFIED')
