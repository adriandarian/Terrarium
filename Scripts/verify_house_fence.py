"""Verify the targeted house/fence change and preservation of other scenery."""
import unreal,json,math,re
from pathlib import Path
from collections import Counter
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/HouseFence'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='HouseFence_Review_Transient':actors.destroy_actor(a)
house=None;review=None;baseline=None;camera=None;world=None;a=None;c=None
def transform(value):
    # Unreal's repr includes a temporary memory address, which is not state.
    values=[float(v) for v in re.findall(r'[xyzw]: (-?\d+\.\d+)',str(value))]
    assert len(values)==10 and all(math.isfinite(v) for v in values)
    return values
def snapshot():
    result={};counts=Counter()
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            n=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
            if not n:continue
            name=c.static_mesh.get_name();counts[name]+=n
            if name.startswith(('SM_Fence','SM_Cottage')):continue
            result[name]={'count':n,'material':c.get_material(0).get_path_name(),
                          'transforms':[transform(c.get_instance_transform(i,world_space=True)) for i in range(n)] if isinstance(c,unreal.InstancedStaticMeshComponent) else [transform(a.get_actor_transform())]}
    house=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and 'Cottage' in a.static_mesh_component.static_mesh.get_name())
    return {'other_assets':result,'counts':dict(counts),'house_transform':transform(house.get_actor_transform()),
            'fence_transforms':{a.get_actor_label():transform(a.get_actor_transform()) for a in actors.get_all_level_actors() if a.get_actor_label().startswith('ReferenceFence_')}}
before=snapshot()
assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadBeforeHouseFence')
original=snapshot()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
after=snapshot()
(out/'state-debug.json').write_text(json.dumps({'before':before,'after':after,'original':original},indent=2))
assert before==after,'Save/reopen differs'
assert original['other_assets']==after['other_assets'],'Unrelated scenery changed'
assert original['house_transform']==after['house_transform'],'House contact anchor moved'
layout=json.loads((out/'layout.json').read_text())
assert after['counts']['SM_FencePost_Reference']==layout['posts']
assert after['counts']['SM_FenceRails_Reference']==layout['rail_sections']
assert after['counts']['SM_Cottage_Reference_v2']==1
assert 'SM_FencePost_Detail' not in after['counts'] and 'SM_FenceRails_Detail' not in after['counts']
geometry={}
for name in ('SM_Cottage_Reference_v2','SM_FencePost_Reference','SM_FenceRails_Reference'):
    e=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
    assert e['saved_normal_errors']==0
    geometry[name]={'triangles':e['triangles'],'saved_normal_errors':0}
(out/'verification.json').write_text(json.dumps({'saved_reopened':True,'unrelated_scenery_unchanged':True,
    'house_anchor_unchanged':True,'counts':after['counts'],'geometry':geometry,'fence_transforms':after['fence_transforms']},indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
unreal.log('HOUSE_FENCE_SAVE_REOPEN_VERIFIED')
