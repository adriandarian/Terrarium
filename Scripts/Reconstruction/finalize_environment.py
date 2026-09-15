"""Apply reviewed cliff revision and exact terrain contacts; prepare the saved hero camera."""
import unreal,json,sys
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment';sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadReference.' in str(levels.get_current_level())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();rows=[]
for variant in 'ABC':
    ft=unreal.load_asset('/Game/Terrarium/Environment/Foliage/FT_Env_CliffColumn_v6'+variant+'_Detail');assert ft
    new=unreal.load_asset('/Game/Terrarium/Environment/Meshes/SM_Env_Cliff_'+variant+'_R2');assert new
    ts=[]
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
            if c.static_mesh and c.static_mesh.get_name() in ['SM_Env_Cliff_'+variant,'SM_Env_Cliff_'+variant+'_R2']:
                ts.extend(c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count()))
    assert ts
    unreal.InstancedFoliageActor.remove_all_instances(world,ft);ft.set_editor_property('mesh',new);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.add_instances(world,ft,ts);rows.append({'mesh':new.get_path_name(),'instances':len(ts)})
grounds=[]
for a in actors.get_all_level_actors():
    if a.get_actor_label() in ['Reference_Cottage','Reference_BlueShed','Reference_Tower','Reference_Lantern','Reference_VegetableBed','Reference_FlowerBorder','Reference_Player']:
        p=a.get_actor_location();p.z=560
        if a.get_actor_label()=='Reference_Player':p=unreal.Vector(*ref.world(177,394,560))
        a.set_actor_location(p,False,False);origin,extent=a.get_actor_bounds(False)
        grounds.append({'actor':a.get_actor_label(),'ground_error_cm':origin.z-extent.z-560});assert abs(origin.z-extent.z-560)<.02
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
camera.set_editor_property('auto_activate_for_player',unreal.AutoReceiveInput.PLAYER0)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([])
assert levels.save_current_level();(out/'final-bindings.json').write_text(json.dumps({'cliffs':rows,'courtyard_grounding':grounds,'camera_auto_activation':str(camera.get_editor_property('auto_activate_for_player'))},indent=2))
