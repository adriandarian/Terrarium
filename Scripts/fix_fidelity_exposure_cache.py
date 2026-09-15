"""Keep Lumen's cached lighting range valid for the fixed artistic exposure.

UE 5.8 PostProcessEyeAdaptation.cpp documents value 8 as EV range [-4,16].
This fixes clipping; it does not alter the chosen camera exposure.
"""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'r.EyeAdaptation.CachedLightingPreExposure 8')
assert unreal.SystemLibrary.get_console_variable_float_value('r.EyeAdaptation.CachedLightingPreExposure')==8
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if isinstance(a,unreal.SkyLight):a.light_component.recapture_sky()
unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset('/Game/Terrarium/Materials/M_SculptedPalette'))
Path(unreal.Paths.project_dir(),'Docs/Fidelity/exposure-cache-fix.json').write_text(json.dumps({'cached_lighting_pre_exposure':8,'safe_ev_range':[-4,16],'manual_camera_ev100':12,'compensation':-.65,'effective_ev':12.65},indent=2))
