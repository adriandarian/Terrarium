"""Keep both visible cottage faces lit, with soft warm directional light."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
sun=scene['Baseline_WarmSun']
sun.set_actor_rotation(unreal.Rotator(pitch=-50,yaw=145,roll=0),False)
sun.light_component.set_intensity(20500)
sun.light_component.set_light_color(unreal.LinearColor(1,.87,.68,1))
sun.light_component.set_editor_property('light_source_angle',16.0)
sky=scene['Baseline_SkyLight'].light_component;sky.set_intensity(5.0);sky.recapture_sky()
assert levels.save_current_level()
p=Path(unreal.Paths.project_dir(),'Docs/Fidelity/Pass6/lighting.json')
p.write_text(json.dumps({'sun_pitch':-50,'sun_yaw':145,'sun_lux':20500,'sun_source_angle':16,'sky_intensity':5,'exposure_compensation':-.65,'reason':'The initial yaw 220 test over-shadowed both the cottage and wheat.'},indent=2))
