import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    if c and c.static_mesh and any(k in c.static_mesh.get_name().lower() for k in ['lantern','sign']):
        p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
        rows.append({'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'location':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z],'bounds':str(a.get_actor_bounds(False))})
(Path(unreal.Paths.project_dir())/'Docs/BlenderRebuild/props-before.json').write_text(json.dumps(rows,indent=2))
