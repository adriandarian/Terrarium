"""Remove inherited bank flattening so authored rock proportions survive placement."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Game/Terrarium/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
folder=root/'Docs/BlenderRebuild/Environment';path=folder/'instance-placement.json';record=json.loads(path.read_text())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
changes=[]
for row in record['rocks']:
    a=scene[row['actor']];assert a.static_mesh_component.static_mesh.get_path_name()==record['rock_mesh']
    s=a.get_actor_scale3d();changes.append({'actor':row['actor'],'before_scale':[s.x,s.y,s.z],'uniform_scale':s.z})
    a.set_actor_scale3d(unreal.Vector(s.z,s.z,s.z));row['after']['scale']=[s.z,s.z,s.z]
assert levels.save_current_level()
record['rock_scale_policy']='Uniform scale preserves source proportions and preceding world height.'
path.write_text(json.dumps(record,indent=2));(folder/'rock-proportion-refinement.json').write_text(json.dumps(changes,indent=2))
