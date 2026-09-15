"""Check saved courtyard composition and preservation outside the edited yard."""
import unreal,json,re,math,gc
from pathlib import Path
from collections import defaultdict,Counter
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/CourtyardParity'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='HouseFence_Review_Transient':actors.destroy_actor(a)
world=None;review=None;camera=None;baseline=None;a=None;c=None;gc.collect()
def transform(t):
    numbers=[float(v) for v in re.findall(r'[xyzw]: (-?\d+\.\d+)',str(t))]
    assert len(numbers)==10 and all(math.isfinite(n) for n in numbers)
    return tuple(numbers)
def snapshot():
    records=defaultdict(list);counts=Counter()
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            name=c.static_mesh.get_name()
            if name=='MatineeCam_SM':continue
            ts=[c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count())] if isinstance(c,unreal.InstancedStaticMeshComponent) else [a.get_actor_transform()]
            for t in ts:
                records[name].append((c.get_material(0).get_path_name(),transform(t)))
                counts[name]+=1
    return {name:sorted(rows) for name,rows in records.items()},dict(counts)
before,counts=snapshot();assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadBeforeCourtyardParity')
original,original_counts=snapshot()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
after,after_counts=snapshot()
assert before==after and counts==after_counts,'Saved state differs after reopening'
changed={'SM_PathTile_v4_Detail','SM_FencePost_Reference','SM_FenceRails_Reference','SM_GardenWell_v2_Detail',
 'SM_GardenBed_v3_Detail','SM_GardenBed_v2_Detail','SM_RockCluster_Detail','SM_Bush_v2_Detail',
 'SM_MeadowGrass_v2_Detail','SM_GroundPlants_v2_Detail','SM_MeadowFlowers_v2_Detail','SM_Shed_v2_Detail'}
preserved=[]
for name,rows in original.items():
    if name not in changed:
        assert after[name]==rows,name+' unexpectedly changed'
        preserved.append(name)
has_blue_context='SM_Shed_Context_Reference' in after
if not has_blue_context:
    assert all(row in after['SM_RockCluster_Detail'] for row in original['SM_RockCluster_Detail'])
shed_name='SM_Shed_Context_Reference' if has_blue_context else 'SM_Shed_v2_Detail'
assert original['SM_Shed_v2_Detail'][0][1][4:]==after[shed_name][0][1][4:],'Shed location or scale changed'
assert original['SM_Shed_v2_Detail'][0][0]==after[shed_name][0][0],'Shed material changed'
assert after[shed_name][0][1][:4]==(0.0,0.0,0.0,1.0),'Shed does not face the right courtyard approach'
assert after_counts['SM_CourtyardTower_Reference']==1
assert after_counts['SM_CourtyardFlowerBed_Reference']==1
assert 'SM_GardenWell_v2_Detail' not in after_counts
layout=json.loads((out/'layout.json').read_text())
assert after_counts['SM_FencePost_Reference']==layout['fence_posts']
assert after_counts['SM_FenceRails_Reference']==layout['rail_sections']
if not has_blue_context:
    assert after_counts['SM_PathTile_v4_Detail']==layout['preserved_path_instances']+layout['new_path_instances']
geometry={}
for name in ('SM_CourtyardTower_Reference','SM_CourtyardFlowerBed_Reference'):
    report=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
    assert report['saved_normal_errors']==0 and report['all_components_closed']
    geometry[name]={'triangles':report['triangles'],'saved_normal_errors':0,'closed_components':True}
(out/'verification.json').write_text(json.dumps({'saved_reopened':True,'preserved_asset_types':preserved,
 'house_transform_unchanged':True,'shed_position_and_scale_preserved':True,'shed_yaw':0,'blue_house_context':has_blue_context,
 'counts':after_counts,'geometry':geometry,'validation_scope':'Native editor rendering, geometry and saved composition. No packaged gameplay or collision validation.'},indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
unreal.log('COURTYARD_PARITY_SAVE_REOPEN_VERIFIED')
if has_blue_context:
    exec(compile((root/'Scripts/verify_blue_house_context.py').read_text(),str(root/'Scripts/verify_blue_house_context.py'),'exec'),globals())
