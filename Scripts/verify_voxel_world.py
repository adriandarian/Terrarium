"""Save/reopen verification and matching native render for the voxel pass."""
import unreal, json
from pathlib import Path
from collections import Counter
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/VoxelPass'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for name in ('M_VoxelGround','M_VoxelSurface'):
    mat=unreal.load_asset('/Game/Terrarium/Materials/'+name)
    mat.set_editor_property('used_with_instanced_static_meshes',True)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
mat=None
def snapshot():
    counts=Counter();materials={};landmarks={}
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            name=c.static_mesh.get_name()
            count=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
            if not count:continue
            counts[name]+=count
            materials[name]=c.get_material(0).get_path_name() if c.get_material(0) else None
        if isinstance(a,unreal.StaticMeshActor):landmarks[a.get_actor_label()]=str(a.get_actor_transform())
    return {'counts':dict(counts),'materials':materials,'landmarks':landmarks}
before=snapshot()
levels.eject_pilot_level_actor()
assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadBeforeVoxelPass')
original=snapshot()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
after=snapshot()
report={'before_reload':before,'after_reload':after,'original':original,'reload_matches':before==after,
        'landmarks_unchanged':original['landmarks']==after['landmarks']}
(out/'verification.json').write_text(json.dumps(report,indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert unreal.AutomationLibrary.take_high_res_screenshot(962,1618,str(out/'voxel-world.png'),camera=camera,delay=1.0)
assert report['reload_matches'], 'Saved component replacements did not persist'
assert report['landmarks_unchanged']
assert sum(after['counts'].values())==sum(original['counts'].values())
for name in ('SM_VoxelCliffStepped_A','SM_VoxelCliffStepped_B','SM_VoxelCliffStepped_C','SM_VoxelTree','SM_VoxelBush'):
    assert after['counts'][name]>0
    evidence=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
    assert evidence['saved_normal_errors']==0
unreal.log('VOXEL_SAVE_REOPEN_VERIFIED')
