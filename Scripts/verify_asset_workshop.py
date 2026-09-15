import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
assert '/ModularGallery.' in str(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
study=[a for n,a in scene.items() if n.startswith('Study_')]
assert len(study)==15
camera=scene['Baseline_Orthographic_Review']
pp=scene['Baseline_FixedExposure_EV12'].settings
material=unreal.load_asset('/Game/Terrarium/Materials/M_SculptedPalette')
assert not material.get_editor_property('two_sided')
assert camera.camera_component.projection_mode==unreal.CameraProjectionMode.ORTHOGRAPHIC
assert pp.auto_exposure_method==unreal.AutoExposureMethod.AEM_MANUAL
cvars={n:unreal.SystemLibrary.get_console_variable_int_value(n) for n in ['r.DynamicGlobalIlluminationMethod','r.ReflectionMethod','r.GenerateMeshDistanceFields','r.Lumen.DiffuseIndirect.Allow','r.Lumen.Reflections.Allow','r.Shadow.Virtual.Enable']}
assert all(v==1 for v in cvars.values())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.save_current_level()
report={'project':unreal.Paths.get_project_file_path(),'engine':unreal.SystemLibrary.get_engine_version(),'map':str(levels.get_current_level()),'displayed_asset_count':len(study),'material_two_sided':False,'camera_projection':str(camera.camera_component.projection_mode),'manual_exposure':{'iso':pp.camera_iso,'shutter_speed':pp.camera_shutter_speed,'fstop':pp.depth_of_field_fstop,'compensation':pp.auto_exposure_bias},'cvars':cvars,'meshes':[str(a.static_mesh_component.static_mesh.get_path_name()) for a in study]}
Path(unreal.Paths.project_dir(),'Docs/Phase1/workshop-validation.json').write_text(json.dumps(report,indent=2))
