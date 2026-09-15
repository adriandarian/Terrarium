"""Restrained native aerial perspective beyond the cottage and river.

No depth-of-field blur: near surfaces retain their authored detail. Integration
must inspect the rendered result because ortho fog origin correction can change
the visual start relative to the geometric distances reported below.
"""
import math
import unreal
import reference as ref


LABEL = 'Pass7_DistantAtmosphere'
SOFTNESS_PATH = '/Game/Terrarium/Materials/M_Pass7_DistantSoftness'


def _softness(camera):
    """Camera-specific miniature background softness, independent of ortho DOF."""
    lib = unreal.MaterialEditingLibrary
    material = unreal.load_asset(SOFTNESS_PATH)
    if material:
        lib.delete_all_material_expressions(material)
    else:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            'M_Pass7_DistantSoftness', '/Game/Terrarium/Materials',
            unreal.Material, unreal.MaterialFactoryNew())
    assert material
    material.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
    material.set_editor_property('blendable_location', unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
    source = lib.create_material_expression(material, unreal.MaterialExpressionSceneTexture, -400, 0)
    source.set_editor_property('scene_texture_id', unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
    custom = lib.create_material_expression(material, unreal.MaterialExpressionCustom, 0, 0)
    custom.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    source_input=unreal.CustomInput()
    source_input.set_editor_property('input_name','SourceColor')
    custom.set_editor_property('inputs', [source_input])
    # SceneTexture node both supplies the original color and declares the scene
    # texture dependency needed by SceneTextureLookup in the generated shader.
    # Native helpers use each input's buffer size and viewport transform, so
    # resizing the editor or letterboxing does not change the sampling footprint.
    custom.set_editor_property('code', '''
float2 viewportUV = GetViewportUV(Parameters);
float amount = 0.90 * (1.0 - smoothstep(0.02, 0.32, viewportUV.y));
float2 uv = GetDefaultSceneTextureUV(Parameters, 14);
float2 texel = GetSceneTextureBufferSize(14).zw;
float radius = 0.85 * View.ViewSizeAndInvSize.x / 481.0;
float3 soft = SourceColor.rgb * 0.25;
soft += SceneTextureLookup(ClampSceneTextureUV(uv + float2(texel.x * radius, 0), 14), 14, true).rgb * 0.125;
soft += SceneTextureLookup(ClampSceneTextureUV(uv - float2(texel.x * radius, 0), 14), 14, true).rgb * 0.125;
soft += SceneTextureLookup(ClampSceneTextureUV(uv + float2(0, texel.y * radius), 14), 14, true).rgb * 0.125;
soft += SceneTextureLookup(ClampSceneTextureUV(uv - float2(0, texel.y * radius), 14), 14, true).rgb * 0.125;
soft += SceneTextureLookup(ClampSceneTextureUV(uv + texel * radius, 14), 14, true).rgb * 0.0625;
soft += SceneTextureLookup(ClampSceneTextureUV(uv - texel * radius, 14), 14, true).rgb * 0.0625;
soft += SceneTextureLookup(ClampSceneTextureUV(uv + float2(texel.x, -texel.y) * radius, 14), 14, true).rgb * 0.0625;
soft += SceneTextureLookup(ClampSceneTextureUV(uv + float2(-texel.x, texel.y) * radius, 14), 14, true).rgb * 0.0625;
return lerp(SourceColor.rgb, soft, amount);
''')
    assert lib.connect_material_expressions(source, 'Color', custom, 'SourceColor')
    assert lib.connect_material_property(custom, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    lib.recompile_material(material)
    assert unreal.EditorAssetLibrary.save_loaded_asset(material)
    camera.camera_component.set_editor_property('post_process_blend_weight', 1.0)
    camera.camera_component.add_or_update_blendable(material, 1.0)
    return {'material': material.get_path_name(), 'scope': 'fixed portrait camera upper background',
            'mask_end_viewport_y': 0.32, 'maximum_mix': 0.90,
            'sample_radius_at_reference_width_px': 0.85, 'color_tint': 'none',
            'validation': 'Requires material compile and matched A/B editor captures.'}


def set_softness_enabled(enabled):
    """A/B toggle; does not change exposure, geometry, lighting, or fog."""
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    camera = next(a for a in actors.get_all_level_actors()
                  if a.get_actor_label() == 'Baseline_Orthographic_Review')
    material = unreal.load_asset(SOFTNESS_PATH)
    assert material
    camera.camera_component.set_editor_property('post_process_blend_weight', 1.0)
    camera.camera_component.add_or_update_blendable(material, 1.0 if enabled else 0.0)


def apply():
    assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert '/HomesteadFidelity.' in str(levels.get_current_level())
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    camera = scene['Baseline_Orthographic_Review']
    assert camera.camera_component.projection_mode == unreal.CameraProjectionMode.ORTHOGRAPHIC
    fog = scene.get(LABEL)
    if fog is None:
        fog = actors.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 880))
        assert fog
        fog.set_actor_label(LABEL)
    fog.set_folder_path('HomesteadFidelity/Atmosphere')
    fog.set_actor_location(unreal.Vector(0, 0, 880), False, False)
    comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    assert comp
    # Native component setters trigger the render-state updates. Non-volumetric
    # fog is essential: the engine explicitly excludes start/max-opacity support
    # from volumetric fog (ExponentialHeightFogComponent.h).
    comp.set_volumetric_fog(False)
    comp.set_second_fog_density(0.0)
    comp.set_fog_density(0.05)
    comp.set_fog_height_falloff(0.001)
    comp.set_start_distance(6800.0)
    comp.set_fog_max_opacity(0.04)
    # Daylight radiance for the established fixed EV100 exposure. An ordinary
    # 0..1 fog color would become almost black under this physical exposure.
    comp.set_fog_inscattering_color(unreal.LinearColor(1000.0, 1150.0, 780.0, 1.0))
    comp.set_directional_inscattering_color(unreal.LinearColor(0, 0, 0, 1))
    comp.set_editor_property('sky_atmosphere_ambient_contribution_color_scale', unreal.LinearColor(0, 0, 0, 1))
    comp.set_editor_property('sky_light_capture_affects_height_fog_strength', 0.0)
    names = ['fog_density', 'fog_height_falloff', 'start_distance', 'fog_max_opacity', 'enable_volumetric_fog']
    settings = {name: comp.get_editor_property(name) for name in names}
    color = comp.get_editor_property('fog_inscattering_luminance')
    settings['fog_inscattering_luminance'] = [color.r, color.g, color.b]
    assert abs(settings['start_distance'] - 6800) < 0.01
    assert abs(settings['fog_max_opacity'] - 0.04) < 0.0001
    assert settings['enable_volumetric_fog'] is False
    origin = camera.get_actor_location()
    forward = camera.get_actor_forward_vector()
    distances = {}
    for name, point in {
        'cottage_ground': ref.BUILDINGS['cottage'],
        'bridge_deck': ref.BUILDINGS['bridge_deck'],
        'upper_wheat_ground': (350, 115, 880),
        'distant_upper_ground': (240, 0, 880),
    }.items():
        xyz = ref.world(*point)
        delta = [xyz[0] - origin.x, xyz[1] - origin.y, xyz[2] - origin.z]
        distances[name] = {
            'camera_distance_cm': round(math.sqrt(sum(v*v for v in delta)), 2),
            'camera_forward_depth_cm': round(delta[0]*forward.x + delta[1]*forward.y + delta[2]*forward.z, 2),
        }
    other_fog = [a.get_actor_label() for a in actors.get_all_level_actors()
                 if isinstance(a, unreal.ExponentialHeightFog) and a != fog]
    return {
        'actor': fog.get_actor_label(), 'native_class': 'ExponentialHeightFog',
        'readback': settings, 'landmark_geometric_distances': distances,
        'other_fog_actors': other_fog,
        'background_softness': _softness(camera),
        'intent': 'At most four percent aerial perspective, restricted to distant upper landscape; cottage and river stay crisp.',
        'visual_validation': 'Pending direct editor render; geometric distances do not prove fog placement in an orthographic view.',
    }
