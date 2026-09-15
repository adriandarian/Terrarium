import unreal
from pathlib import Path
assert Path(unreal.Paths.project_dir()).resolve()==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if a.get_actor_label()=='Blender_Tree_RenderDiagnostic':
        assert a.static_mesh_component.static_mesh.get_name()=='SM_Blender_HomesteadTree'
        assert actors.destroy_actor(a)
