"""Softer reference studio illumination, preserving Lit PBR rendering."""
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Reconstruction/Maps/ReviewStage' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
for name,intensity,rgb,shadows in [('Key',3.5,(1,.95,.88),True),('Fill',2.5,(.92,.96,1),False),('Rim',1.0,(1,1,1),False)]:
    c=scene['Studio'+name].light_component
    c.set_intensity(intensity);c.set_light_color(unreal.LinearColor(*rgb,1))
    c.set_editor_property('cast_shadows',shadows)
    c.set_editor_property('light_source_angle',12.0)
scene['StudioFloor'].set_actor_scale3d(unreal.Vector(1500,1500,.2))
s=scene['StudioExposure'].get_editor_property('settings')
s.set_editor_property('ambient_occlusion_intensity',.25)
scene['StudioExposure'].set_editor_property('settings',s)
assert levels.save_current_level()
