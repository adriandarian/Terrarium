"""Read active world lighting, exposure and renderer configuration before tuning."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
out=root/'Docs/BlenderRebuild/Lighting';out.mkdir(exist_ok=True)
def properties(obj,keys):
    result={}
    for key in keys:
        try:
            value=obj.get_editor_property(key)
            result[key]=value if isinstance(value,(str,int,float,bool)) else str(value)
        except Exception as error:result[key]={'unavailable':str(error)}
    return result
rows=[]
for a in actors.get_all_level_actors():
    if isinstance(a,(unreal.DirectionalLight,unreal.SkyLight,unreal.PointLight,unreal.RectLight,unreal.SpotLight)):
        c=a.light_component
        keys=['intensity','light_color','indirect_lighting_intensity','volumetric_scattering_intensity','cast_shadows','mobility','affects_world']
        if isinstance(a,unreal.SkyLight):keys+=['source_type','cubemap','real_time_capture','lower_hemisphere_is_solid_color','lower_hemisphere_color','occlusion_max_distance','occlusion_contrast','occlusion_exponent','min_occlusion','sky_distance_threshold']
        rows.append({'actor':a.get_actor_label(),'class':a.get_class().get_name(),'rotation':str(a.get_actor_rotation()),'properties':properties(c,keys)})
    elif isinstance(a,unreal.PostProcessVolume):
        keys=['auto_exposure_method','auto_exposure_apply_physical_camera_exposure','auto_exposure_bias','camera_iso','camera_shutter_speed','depth_of_field_fstop','dynamic_global_illumination_method','reflection_method','lumen_scene_lighting_quality','lumen_final_gather_quality','indirect_lighting_intensity','indirect_lighting_color','color_saturation','color_contrast','color_gamma','color_gain','color_offset','ambient_cubemap_intensity']
        rows.append({'actor':a.get_actor_label(),'class':'PostProcessVolume','volume':properties(a,['unbound','priority','blend_weight']),'settings':properties(a.settings,keys+['override_'+k for k in keys])})
cvars={k:unreal.SystemLibrary.get_console_variable_int_value(k) for k in ['r.DynamicGlobalIlluminationMethod','r.ReflectionMethod','r.GenerateMeshDistanceFields','r.Lumen.DiffuseIndirect.Allow','r.Lumen.HardwareRayTracing','sg.GlobalIlluminationQuality','sg.ReflectionQuality']}
(out/'live-diagnostics.json').write_text(json.dumps({'world':str(levels.get_current_level()),'dirty_maps':[str(p) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'actors':rows,'console_variables':cvars},indent=2))
