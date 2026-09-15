"""Phase 0 only. Run inside Terrarium's Unreal Editor through its MCP console."""
import unreal
import json
from pathlib import Path

assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
LEVEL = '/Game/Terrarium/Maps/RenderBaseline'
assert not unreal.EditorAssetLibrary.does_asset_exist(LEVEL), 'Baseline exists; inspect rather than rebuild.'
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.new_level(LEVEL)

def spawn(cls, label, location=(0,0,0), rotation=(0,0,0)):
    actor = actors.spawn_actor_from_class(cls, unreal.Vector(*location), unreal.Rotator(pitch=rotation[0],yaw=rotation[1],roll=rotation[2]))
    actor.set_actor_label(label)
    return actor

def matte(name, rgb):
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, '/Game/Terrarium/Materials', unreal.Material, unreal.MaterialFactoryNew())
    lib = unreal.MaterialEditingLibrary
    color = lib.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
    color.set_editor_property('constant', unreal.LinearColor(*rgb, 1))
    lib.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,0.92,160),(unreal.MaterialProperty.MP_SPECULAR,0.15,280)]:
        node = lib.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, y)
        node.set_editor_property('r',value)
        lib.connect_material_property(node,'',prop)
    lib.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat

olive = matte('M_Baseline_Olive', (0.25,0.31,0.105))
stone = matte('M_Baseline_Tan', (0.54,0.41,0.25))
clay = matte('M_Baseline_Terracotta', (0.5,0.15,0.07))
for label,mesh,loc,scale,mat in [
    ('Baseline_Ground','Cube',(0,0,-50),(12,10,1),olive),
    ('Baseline_StoneCube','Cube',(-180,-100,110),(2.2,2.2,2.2),stone),
    ('Baseline_ClaySphere','Sphere',(190,90,110),(2.2,2.2,2.2),clay)]:
    a=spawn(unreal.StaticMeshActor,label,loc)
    a.set_actor_scale3d(unreal.Vector(*scale))
    comp=a.static_mesh_component
    comp.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/'+mesh))
    comp.set_material(0,mat)
    a.set_folder_path('Phase0/Placeholders')

sun=spawn(unreal.DirectionalLight,'Baseline_WarmSun',(0,0,800),(-48,-155,0))
sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sun.light_component.set_intensity(30000)
sun.light_component.set_light_color(unreal.LinearColor(1,0.88,0.69,1))
sun.light_component.set_editor_property('light_source_angle',6.0)
sun.light_component.set_editor_property('atmosphere_sun_light',True)
sky=spawn(unreal.SkyAtmosphere,'Baseline_SkyAtmosphere')
fill=spawn(unreal.SkyLight,'Baseline_SkyLight',(0,0,500))
fill.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
fill.light_component.set_editor_property('real_time_capture',True)
fill.light_component.set_intensity(2.0)

pp=spawn(unreal.PostProcessVolume,'Baseline_FixedExposure_EV12')
pp.set_editor_property('unbound',True)
settings=pp.get_editor_property('settings')
def override(key,value):
    settings.set_editor_property('override_'+key,True)
    settings.set_editor_property(key,value)
override('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL)
override('auto_exposure_apply_physical_camera_exposure',True)
override('camera_iso',100.0)
override('camera_shutter_speed',64.0)
override('depth_of_field_fstop',8.0)
override('auto_exposure_bias',0.0)
override('dynamic_global_illumination_method',unreal.DynamicGlobalIlluminationMethod.LUMEN)
override('reflection_method',unreal.ReflectionMethod.LUMEN)
override('motion_blur_amount',0.0)
override('vignette_intensity',0.0)
override('bloom_intensity',0.0)
pp.set_editor_property('settings',settings)
for a in [sun,sky,fill,pp]: a.set_folder_path('Phase0/Lighting')

camera=spawn(unreal.CameraActor,'Baseline_Orthographic_Review',(1450,-1450,1775),(-40,135,0))
cc=camera.camera_component
cc.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC)
cc.set_ortho_width(1850)
cc.set_editor_property('aspect_ratio',1.25)
cc.set_editor_property('constrain_aspect_ratio',True)
cc.set_editor_property('post_process_blend_weight',0.0)
camera.set_folder_path('Phase0/Camera')
levels.pilot_level_actor(camera)
levels.set_exact_camera_view(True)
levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
Path(unreal.Paths.project_saved_dir(),'baseline-built.json').write_text(json.dumps({'level':LEVEL,'projection':'Orthographic','width_cm':1850,'pitch':-40,'yaw':135,'EV100':12,'iso':100,'fstop':8,'shutter':64,'placeholder_count':3},indent=2))
unreal.log('TERRARIUM_PHASE0_BUILT')
