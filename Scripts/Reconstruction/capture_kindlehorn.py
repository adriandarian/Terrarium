"""Reference-facing and reverse Lit captures of the selected Kindlehorn revision."""
import json
from pathlib import Path
import unreal
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
root=Path(unreal.Paths.project_dir())
rows=[json.loads(p.read_text()) for p in (root/'Docs/Reconstruction/Builds').glob('SM_Recon_Kindlehorn*.json')]
row=max(rows,key=lambda r:r['revision'])
code=(root/'Scripts/Reconstruction/capture.py').read_text()
assert '/Reconstruction/Maps/ReviewStage' in str(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
lighting={'StudioKey':3.5,'StudioFill':.75,'StudioRim':.5,'StudioAmbientSky':.35}
old_lights=[]
for name,intensity in lighting.items():
    a=scene[name]
    c=a.get_component_by_class(unreal.SkyLightComponent) if name=='StudioAmbientSky' else a.light_component
    old_lights.append((c,c.get_editor_property('intensity')))
    c.set_intensity(intensity)
old_rotation=scene['StudioKey'].get_actor_rotation()
scene['StudioKey'].set_actor_rotation(unreal.Rotator(pitch=-42,yaw=125,roll=0),False)
pp=scene['StudioExposure'];settings=pp.get_editor_property('settings')
old_ao=(settings.ambient_occlusion_intensity,settings.ambient_occlusion_radius)
old_bloom=(settings.override_bloom_intensity,settings.bloom_intensity)
settings.set_editor_property('ambient_occlusion_intensity',.75)
settings.set_editor_property('ambient_occlusion_radius',12)
pp.set_editor_property('settings',settings)
import sys,importlib
sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import kindlehorn_effects
importlib.reload(kindlehorn_effects)
kindlehorn_effects.build_blueprint(row['asset'])
scene['ReviewModel'].set_actor_location(unreal.Vector(),False,False)
for a in actors.get_all_level_actors():
    if a.get_actor_label().startswith('FX_Kindlehorn'):actors.destroy_actor(a)
fx,glow=kindlehorn_effects.spawn_effects(scene['ReviewModel'])
nc=fx.get_component_by_class(unreal.NiagaraComponent)
nc.advance_simulation(90,1/60)
nc.set_paused(True)
settings=pp.get_editor_property('settings')
settings.set_editor_property('override_bloom_intensity',True)
settings.set_editor_property('bloom_intensity',.8)
pp.set_editor_property('settings',settings)
views={}
try:
    for view,yaw in [('front',65),('back',245)]:
        request={'asset':row['asset'],'name':row['name']+'-'+view,'yaw':yaw,'pitch':-24,
                 'projection':'orthographic','ortho_width':220,'resolution':1254}
        (root/'Saved/reconstruction-capture.json').write_text(json.dumps(request))
        exec(compile(code,'capture.py','exec'),{'__name__':'__main__'})
        views[view]=request
finally:
    for c,intensity in old_lights:c.set_intensity(intensity)
    scene['StudioKey'].set_actor_rotation(old_rotation,False)
    settings=pp.get_editor_property('settings')
    settings.set_editor_property('ambient_occlusion_intensity',old_ao[0])
    settings.set_editor_property('ambient_occlusion_radius',old_ao[1])
    settings.set_editor_property('override_bloom_intensity',old_bloom[0])
    settings.set_editor_property('bloom_intensity',old_bloom[1])
    pp.set_editor_property('settings',settings)
    actors.destroy_actor(fx);actors.destroy_actor(glow)
record={'views':views,'lighting':lighting,'key_rotation_degrees':[-42,125,0],
        'ambient_occlusion_intensity':.75,'ambient_occlusion_radius_cm':12,
        'render':'native Unreal Lit; no image editing','studio_settings_restored_after_capture':True}
(root/'Docs/Reconstruction/Renders'/('Kindlehorn-R'+str(row['revision'])+'-capture.json')).write_text(json.dumps(record,indent=2))





