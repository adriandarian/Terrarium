"""Read Storm's existing world associations before replacing its reconstruction."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
rows=[]
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    comps=actor.get_components_by_class(unreal.StaticMeshComponent)
    paths=[c.static_mesh.get_path_name() for c in comps if c.static_mesh]
    if 'storm' not in (actor.get_actor_label()+' '.join(paths)).lower():continue
    p=actor.get_actor_location();r=actor.get_actor_rotation();s=actor.get_actor_scale3d()
    rows.append({'label':actor.get_actor_label(),'path':actor.get_path_name(),'meshes':paths,'location':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z],'hidden':actor.is_hidden_ed()})
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
(root/'Docs/BlenderRebuild/Storm/prior-instances.json').write_text(json.dumps({'world':world.get_path_name(),'instances':rows},indent=2))
