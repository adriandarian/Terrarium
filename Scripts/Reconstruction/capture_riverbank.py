"""Reference-facing and reverse Lit captures of the selected Riverbank revision."""
import json
from pathlib import Path
import unreal
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
root=Path(unreal.Paths.project_dir())
rows=[json.loads(p.read_text()) for p in (root/'Docs/Reconstruction/Builds').glob('SM_Recon_Riverbank*.json')]
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
settings.set_editor_property('ambient_occlusion_intensity',.75)
settings.set_editor_property('ambient_occlusion_radius',12)
pp.set_editor_property('settings',settings)
views={}
try:
    for view,yaw in [('front',45),('back',225)]:
        request={'asset':row['asset'],'name':row['name']+'-'+view,'yaw':yaw,'pitch':-30,
                 'projection':'orthographic','ortho_width':290,'width':1402,'height':1122}
        (root/'Saved/reconstruction-capture.json').write_text(json.dumps(request))
        exec(compile(code,'capture.py','exec'),{'__name__':'__main__'})
        views[view]=request
finally:
    for c,intensity in old_lights:c.set_intensity(intensity)
    scene['StudioKey'].set_actor_rotation(old_rotation,False)
    settings=pp.get_editor_property('settings')
    settings.set_editor_property('ambient_occlusion_intensity',old_ao[0])
    settings.set_editor_property('ambient_occlusion_radius',old_ao[1])
    pp.set_editor_property('settings',settings)
record={'views':views,'lighting':lighting,'key_rotation_degrees':[-42,125,0],
        'ambient_occlusion_intensity':.75,'ambient_occlusion_radius_cm':12,
        'render':'native Unreal Lit; no image editing','studio_settings_restored_after_capture':True}
(root/'Docs/Reconstruction/Renders'/('Riverbank-R'+str(row['revision'])+'-capture.json')).write_text(json.dumps(record,indent=2))


