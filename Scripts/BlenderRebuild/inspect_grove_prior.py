"""Inspect existing Grove instances and nearby props without changing them."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor):continue
    mesh=a.static_mesh_component.static_mesh
    if not mesh:continue
    p=a.get_actor_location()
    if 'Grove' in mesh.get_name() or (290<p.x<420 and 600<p.y<660):
        o,e=a.get_actor_bounds(False)
        rows.append({'actor':a.get_actor_label(),'mesh':mesh.get_path_name(),'location':[p.x,p.y,p.z],'bounds_origin':[o.x,o.y,o.z],'bounds_extent':[e.x,e.y,e.z]})
(root/'Docs/BlenderRebuild/Grove/prior-instances.json').write_text(json.dumps(rows,indent=2))
