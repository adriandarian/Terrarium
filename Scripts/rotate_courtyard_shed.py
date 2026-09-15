"""Turn only the blue shed toward the concept's screen-right approach."""
import unreal,json,sys,importlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/CourtyardParity'
sys.path.insert(0,str(root/'Scripts/Fidelity'))
import courtyard_layout;importlib.reload(courtyard_layout)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
shed=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and 'Shed_v2' in a.static_mesh_component.static_mesh.get_name())
before=shed.get_actor_rotation();location=shed.get_actor_location();scale=shed.get_actor_scale3d()
shed.set_actor_rotation(unreal.Rotator(pitch=before.pitch,yaw=courtyard_layout.SHED_YAW,roll=before.roll),False)
assert shed.get_actor_location()==location and shed.get_actor_scale3d()==scale
assert levels.save_current_level()
(out/'shed-rotation.json').write_text(json.dumps({'asset':shed.static_mesh_component.static_mesh.get_path_name(),
 'before_yaw':before.yaw,'after_yaw':shed.get_actor_rotation().yaw,'position_preserved':True,'scale_preserved':True},indent=2))
shed=None
unreal.log('COURTYARD_SHED_ROTATED')
