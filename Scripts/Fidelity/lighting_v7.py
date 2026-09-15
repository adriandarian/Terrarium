"""Reference lighting pass: warm sunlight with a restrained cool ambient fill.

Run apply() inside the verified Terrarium HomesteadFidelity editor world.
This changes only existing light/post-process actors; the caller saves the map
and must inspect a native render before treating the visual gap as resolved.
"""
import json

import unreal


def _color(component):
    value = component.get_editor_property('light_color')
    return [int(value.r), int(value.g), int(value.b), int(value.a)]


def _readback(sun, sky, volume):
    rotation = sun.get_actor_rotation()
    settings = volume.get_editor_property('settings')
    saturation = settings.get_editor_property('color_saturation')
    return {
        'sun_rotation': {'pitch': rotation.pitch, 'yaw': rotation.yaw,
                         'roll': rotation.roll},
        'sun_lux': sun.light_component.get_editor_property('intensity'),
        'sun_color_srgb8': _color(sun.light_component),
        'sun_source_angle_degrees': sun.light_component.get_editor_property(
            'light_source_angle'),
        'sky_intensity': sky.get_editor_property('intensity'),
        'sky_color_srgb8': _color(sky),
        'exposure_compensation': settings.get_editor_property('auto_exposure_bias'),
        'global_saturation': [saturation.x, saturation.y, saturation.z,
                              saturation.w],
    }


def apply():
    assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert '/HomesteadFidelity.' in str(levels.get_current_level()), (
        'Lighting pass requires the HomesteadFidelity map')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    scene = {actor.get_actor_label(): actor
             for actor in actors.get_all_level_actors()}
    sun = scene['Baseline_WarmSun']
    sky = scene['Baseline_SkyLight'].light_component
    volume = scene['Baseline_FixedExposure_EV12']
    before = _readback(sun, sky, volume)

    # Preserve the direction proven to illuminate both visible cottage walls.
    # Less amber in the source lets green foliage and turquoise water retain
    # their own color. Slightly more direct light restores golden highlights.
    sun.set_actor_rotation(unreal.Rotator(pitch=-50, yaw=145, roll=0), False)
    sun.light_component.set_intensity(22500.0)
    sun.light_component.set_light_color(unreal.LinearColor(1.0, .93, .81, 1.0))
    sun.light_component.set_editor_property('light_source_angle', 5.5)

    # Native pass-7 comparison: upper-land bright pixels already match the
    # reference closely, while the dark decile is substantially too bright.
    # Reduce ambient fill rather than reducing the sun and losing highlights.
    # Both visible cottage walls retain direct light at the preserved yaw.
    sky.set_intensity(2.2)
    sky.set_light_color(unreal.LinearColor(.87, .94, 1.0, 1.0))
    sky.recapture_sky()

    settings = volume.get_editor_property('settings')
    for key, value in (
        ('auto_exposure_bias', -.80),
        ('color_saturation', unreal.Vector4(1.0, 1.0, 1.0, 1.0)),
        ('lumen_scene_lighting_quality', 4.0),
        ('lumen_final_gather_quality', 4.0),
    ):
        settings.set_editor_property('override_' + key, True)
        settings.set_editor_property(key, value)
    volume.set_editor_property('settings', settings)

    report = {
        'gap': 2,
        'project': unreal.Paths.get_project_file_path(),
        'map': str(levels.get_current_level()),
        'before': before,
        'actual': _readback(sun, sky, volume),
        'visual_acceptance': 'pending native rendered comparison',
        'saved_by_this_module': False,
        'revision': 'native-pass7-shadow-fill-refinement',
    }
    unreal.log('PASS7_LIGHTING ' + json.dumps(report, sort_keys=True))
    return report
