import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
rows=[]
for actor in actors:
    meshes=actor.get_components_by_class(unreal.StaticMeshComponent)
    if 'brambit' not in actor.get_actor_label().lower() and not any(c.static_mesh and 'brambit' in c.static_mesh.get_path_name().lower() for c in meshes):continue
    p=actor.get_actor_location();r=actor.get_actor_rotation();s=actor.get_actor_scale3d();center,extent=actor.get_actor_bounds(False)
    rows.append({'label':actor.get_actor_label(),'path':actor.get_path_name(),'location':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z],'bounds_center':[center.x,center.y,center.z],'bounds_extent':[extent.x,extent.y,extent.z],'meshes':[c.static_mesh.get_path_name() for c in meshes if c.static_mesh]})
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
(root/'Docs/BlenderRebuild/Brambit/prior-world.json').write_text(json.dumps({'world':world.get_path_name(),'actors':rows},indent=2))
