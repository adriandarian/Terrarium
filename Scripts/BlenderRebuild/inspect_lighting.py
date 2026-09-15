import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
d={}
for o in a:
    if isinstance(o,unreal.PostProcessVolume):
        s=o.settings
        d[o.get_actor_label()]={k:str(s.get_editor_property(k)) for k in ['auto_exposure_method','auto_exposure_apply_physical_camera_exposure','auto_exposure_bias','auto_exposure_min_brightness','auto_exposure_max_brightness']}
    if isinstance(o,unreal.DirectionalLight):d[o.get_actor_label()]={'intensity':o.light_component.intensity}
camera=next(o for o in a if o.get_actor_label()=='Blender_Cottage_Review')
p=camera.get_actor_location();r=camera.get_actor_rotation()
d['capture_args']={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
root=Path(unreal.Paths.project_dir())
(root/'Docs/BlenderRebuild/Cottage/lighting.json').write_text(json.dumps(d,indent=2))
(root/'Saved/blender-capture.json').write_text(json.dumps(d['capture_args']))
