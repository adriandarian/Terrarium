"""Read prior Ember instances and occupied counter bounds before placement."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
rows=[]
for a in actors:
    p=a.get_actor_location()
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        mesh=c.static_mesh
        if not mesh:continue
        if 'Ember' in mesh.get_name() or (280<p.x<400 and 610<p.y<640 and p.z>630):
            origin,extent=a.get_actor_bounds(False)
            rows.append({'actor':a.get_actor_label(),'mesh':mesh.get_path_name(),'location_cm':[p.x,p.y,p.z],'bounds_origin':[origin.x,origin.y,origin.z],'bounds_extent':[extent.x,extent.y,extent.z]})
(root/'Docs/BlenderRebuild/Ember/prior-instances.json').write_text(json.dumps(rows,indent=2))
