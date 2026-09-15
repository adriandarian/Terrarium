"""Change only the existing sky fill; record the original for reversible trials."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};sky=scene['Baseline_SkyLight'].light_component;sun=scene['Baseline_WarmSun'];pp=scene['Baseline_FixedExposure_EV12']
out=root/'Docs/BlenderRebuild/Lighting';saved=out/'sky-before.json'
def read():
    color=sky.get_editor_property('light_color');s=pp.settings;r=sun.get_actor_rotation()
    return {'intensity':sky.intensity,'color_srgb8':[color.r,color.g,color.b,color.a],'sun_lux':sun.light_component.intensity,'sun_rotation':[r.pitch,r.yaw,r.roll],'exposure_bias':s.get_editor_property('auto_exposure_bias'),'physical_camera_exposure':s.get_editor_property('auto_exposure_apply_physical_camera_exposure')}
if not saved.exists():saved.write_text(json.dumps(read(),indent=2))
request=json.loads((root/'Saved/lighting-sky-trial.json').read_text())
if request.get('restore'):
    previous=json.loads(saved.read_text());sky.set_intensity(previous['intensity']);sky.set_editor_property('light_color',unreal.Color(*previous['color_srgb8']))
else:
    sky.set_intensity(request['intensity']);sky.set_light_color(unreal.LinearColor(*request['color_linear'],1))
sky.recapture_sky();assert levels.save_current_level()
(out/'sky-current.json').write_text(json.dumps({'request':request,'actual':read(),'status':'pending_native_review'},indent=2))
