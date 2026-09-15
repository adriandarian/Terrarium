"""Read current world bounds before selecting a site for the market stall."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    if not c or not c.static_mesh:continue
    p=a.get_actor_location();center,extent=a.get_actor_bounds(False)
    rows.append({'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'location':[p.x,p.y,p.z],'center':[center.x,center.y,center.z],'extent':[extent.x,extent.y,extent.z]})
(root/'Saved/blender-placement-world.json').write_text(json.dumps({'level':str(levels.get_current_level()),'actors':rows},indent=2))
