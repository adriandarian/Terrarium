"""Inspect the existing reference environment before integrating rebuilt assets."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment';out.mkdir(exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.eject_pilot_level_actor()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=[]
for a in actors.get_all_level_actors():
    cs=[]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh:
            cs.append({'mesh':c.static_mesh.get_path_name(),'materials':[str(c.get_material(i)) for i in range(c.get_num_materials())],
                       'instances':c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1})
    if cs:rows.append({'label':a.get_actor_label(),'position':str(a.get_actor_location()),'scale':str(a.get_actor_scale3d()),'rotation':str(a.get_actor_rotation()),'components':cs})
(out/'before.json').write_text(json.dumps(rows,indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
task=unreal.AutomationLibrary.take_high_res_screenshot(962,1618,str(out/'before.png'),camera=camera,delay=1.0)
assert task
