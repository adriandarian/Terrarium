"""Native saved-state verification for the collection-wide detail refinement."""
import unreal,json
from pathlib import Path
from collections import Counter
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/DetailPass'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def snapshot():
    counts=Counter();materials={};landmarks={};transforms={}
    for actor in actors.get_all_level_actors():
        for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
            if not comp.static_mesh:continue
            name=comp.static_mesh.get_name()
            n=comp.get_instance_count() if isinstance(comp,unreal.InstancedStaticMeshComponent) else 1
            if not n:continue
            counts[name]+=n;materials[name]=comp.get_material(0).get_path_name()
            if isinstance(comp,unreal.InstancedStaticMeshComponent):
                transforms[name]=[str(comp.get_instance_transform(i,world_space=True)) for i in range(n)]
        if isinstance(actor,unreal.StaticMeshActor):landmarks[actor.get_actor_label()]=str(actor.get_actor_transform())
    return {'counts':dict(counts),'materials':materials,'landmarks':landmarks,'transforms':transforms}
before=snapshot()
camera=None;world=None;levels.eject_pilot_level_actor()
assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadBeforeVoxelPass')
original=snapshot()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
after=snapshot()
manifest=json.loads((out/'assets.json').read_text())
mapping={r['original']:r['asset'] for r in manifest}
expected={mapping[n]:v for n,v in original['counts'].items() if n.startswith('SM_')}
actual={n:v for n,v in after['counts'].items() if n.startswith('SM_')}
assert actual==expected,(set(actual)^set(expected))
assert before==after,'Save/reopen mismatch'
assert original['landmarks']==after['landmarks']
assert all(after['transforms'][mapping[n]]==v for n,v in original['transforms'].items())
assert all('Voxel' not in n for n in after['counts'])
assert all('Voxel' not in p for p in after['materials'].values())
manifest=json.loads((out/'assets.json').read_text())
geometry={}
for r in manifest:
    check=json.loads((root/'Docs/Phase1/Validation'/(r['asset']+'.json')).read_text())
    assert check['saved_normal_errors']==0
    geometry[r['asset']]={'triangles':check['triangles'],'saved_normal_errors':0}
report={'all_32_types_replaced':True,'saved_reopened':True,'instance_transforms_unchanged':True,
        'static_landmarks_unchanged':True,'counts':actual,'materials':after['materials'],'geometry':geometry,
        'testing':'Native editor state and geometry checks; rendered review is separate; no gameplay testing.'}
(out/'verification.json').write_text(json.dumps(report,indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
unreal.log('ALL_32_DETAIL_ASSETS_SAVE_REOPEN_VERIFIED')
