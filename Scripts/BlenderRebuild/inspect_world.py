import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve()
assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
rows=[]
for a in actors.get_all_level_actors():
    if any(t in a.get_actor_label().lower() for t in ['cottage','house','shed','camera','exposure','light']):
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        rows.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'mesh':c.static_mesh.get_path_name() if c and c.static_mesh else None,'location':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'scale':str(a.get_actor_scale3d()),'bounds':str(a.get_actor_bounds(False))})
dest=root/'Docs/BlenderRebuild';dest.mkdir(parents=True,exist_ok=True)
(dest/'world-before.json').write_text(json.dumps({'project':str(root),'level':str(levels.get_current_level()),'actors':rows},indent=2))
