"""Restore the user's preferred soft scene using the native comparison map."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/DetailPass';out.mkdir(parents=True,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.eject_pilot_level_actor()
camera=None;world=None
assert levels.load_level('/Game/Terrarium/Maps/HomesteadBeforeVoxelPass')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Terrarium/Maps/HomesteadFidelity')
world=None
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def snapshot():
    counts={};materials={};landmarks={}
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            n=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
            if not n:continue
            name=c.static_mesh.get_name();assert 'Voxel' not in name
            counts[name]=counts.get(name,0)+n
            materials[name]=c.get_material(0).get_path_name()
            assert 'Voxel' not in materials[name]
        if isinstance(a,unreal.StaticMeshActor):landmarks[a.get_actor_label()]=str(a.get_actor_transform())
    return {'counts':counts,'materials':materials,'landmarks':landmarks}
state=snapshot()
(out/'restored.json').write_text(json.dumps(state,indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
task=unreal.AutomationLibrary.take_high_res_screenshot(962,1618,str(out/'restored.png'),camera=camera,delay=1.0)
assert levels.save_current_level()
unreal.log('SOFT_WORLD_RESTORED')
