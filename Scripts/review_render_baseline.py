"""Restore the saved Phase 0 review camera and write observed renderer settings."""
import unreal
import json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
camera=scene['Baseline_Orthographic_Review']
camera.set_actor_location(unreal.Vector(1450,-1450,1775),False,False)
camera.set_actor_rotation(unreal.Rotator(pitch=-40,yaw=135,roll=0),False)
levels.pilot_level_actor(camera)
levels.set_exact_camera_view(True)
levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
levels.save_current_level()
report={'project':unreal.Paths.get_project_file_path(),'engine':unreal.SystemLibrary.get_engine_version(),
        'camera_rotation':str(camera.get_actor_rotation()),'projection':str(camera.camera_component.projection_mode),
        'actors':list(scene), 'cvars':{}}
for name in ['r.DynamicGlobalIlluminationMethod','r.ReflectionMethod','r.GenerateMeshDistanceFields','r.Lumen.DiffuseIndirect.Allow','r.Lumen.Reflections.Allow','r.Shadow.Virtual.Enable']:
    report['cvars'][name]=unreal.SystemLibrary.get_console_variable_int_value(name)
pp=scene['Baseline_FixedExposure_EV12'].settings
report['exposure']={k:str(pp.get_editor_property(k)) for k in ['auto_exposure_method','auto_exposure_apply_physical_camera_exposure','camera_iso','camera_shutter_speed','depth_of_field_fstop','auto_exposure_bias']}
Path(unreal.Paths.project_saved_dir(),'baseline-validation.json').write_text(json.dumps(report,indent=2))
