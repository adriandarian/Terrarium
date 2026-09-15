"""Phase 3, whole-scene pass 1: warm frontal sun, ambient fill, oblique framing."""
import unreal,sys,math,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir())
sys.path.insert(0,str(root/'Scripts/Scene'))
from placement import world
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Homestead.' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
sun=scene['Baseline_WarmSun']
sun.set_actor_rotation(unreal.Rotator(pitch=-55,yaw=115,roll=0),False)
sun.light_component.set_intensity(18000)
sun.light_component.set_light_color(unreal.LinearColor(1,.94,.83,1))
sun.light_component.set_editor_property('light_source_angle',14.0)
sky=scene['Baseline_SkyLight'].light_component
sky.set_intensity(5.0)
sky.recapture_sky()
pp=scene['Baseline_FixedExposure_EV12']
settings=pp.settings
for key,value in [('color_saturation',unreal.Vector4(.9,.9,.9,1)),('lumen_scene_lighting_quality',4.0),('lumen_final_gather_quality',4.0)]:
    settings.set_editor_property('override_'+key,True)
    settings.set_editor_property(key,value)
pp.set_editor_property('settings',settings)
camera=scene['Baseline_Orthographic_Review']
pitch=-45;yaw=112;distance=6500
forward=unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)),math.cos(math.radians(pitch))*math.sin(math.radians(yaw)),math.sin(math.radians(pitch)))
camera.set_actor_location(world(30,30,230)-forward*distance,False,False)
camera.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False)
camera.camera_component.set_ortho_width(2780)
camera.camera_component.set_editor_property('aspect_ratio',.68)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
p=root/'Docs/Phase3';p.mkdir(parents=True,exist_ok=True)
(p/'pass-1-settings.json').write_text(json.dumps({'pass':1,'sun_lux':18000,'sun_source_angle':14,'sky_intensity':5,'camera_pitch':pitch,'camera_yaw':yaw,'changes':['Corrected ascending stair direction','Reduced cottage scale to 1.14','Snapped planting heights to actual terrain cells','Warmer softer frontal illumination','Oblique terrain framing']},indent=2))
unreal.log('HOMESTEAD_LIGHT_PASS_1_COMPLETE')
