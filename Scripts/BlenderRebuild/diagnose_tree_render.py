"""Temporary static counterpart distinguishes foliage visibility from mesh import faults."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
record=json.loads((root/'Docs/BlenderRebuild/HomesteadTree/instance-placement.json').read_text());mesh=unreal.load_asset(record['mesh'])
t=next(c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh for i in range(c.get_instance_count()) if abs(c.get_instance_transform(i,world_space=True).translation.x+959.2766)<.1)
assert not any(a.get_actor_label()=='Blender_Tree_RenderDiagnostic' for a in actors.get_all_level_actors())
a=actors.spawn_actor_from_class(unreal.StaticMeshActor,t.translation);a.set_actor_label('Blender_Tree_RenderDiagnostic');a.static_mesh_component.set_static_mesh(mesh);a.set_actor_transform(t,False,False)
unreal.log('TEMP_TREE_RENDER_DIAGNOSTIC_CREATED_NOT_SAVED')
