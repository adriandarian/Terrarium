import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
sun=scene['Baseline_WarmSun']
sun.set_actor_rotation(unreal.Rotator(pitch=-48,yaw=-155,roll=0),False)
sun.light_component.set_editor_property('light_source_angle',6.0)
sky=scene['Baseline_SkyLight'].light_component
sky.set_intensity(2.0)
sky.recapture_sky()
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
