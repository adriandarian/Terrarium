"""Read-only PIE spawn diagnostics and pawn-profile capsule overlap probes."""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = editor.get_game_world() or editor.get_editor_world()
assert world and 'StartingHome' in world.get_path_name()
starts = unreal.GameplayStatics.get_all_actors_of_class(world,unreal.PlayerStart)
pawn = unreal.GameplayStatics.get_player_character(world,0)
controller = unreal.GameplayStatics.get_player_controller(world,0)
mode = unreal.GameplayStatics.get_game_mode(world)
vec = lambda p:[p.x,p.y,p.z]
report = {'world':world.get_path_name(),'starts':[],'probes':[]}
for start in starts:
    report['starts'].append({'actor':start.get_path_name(),'class':start.get_class().get_path_name(),
        'location_cm':vec(start.get_actor_location()),'editor_only':start.get_editor_property('is_editor_only_actor'),
        'actor_scale':vec(start.get_actor_scale3d())})
if mode and controller:
    chosen = mode.choose_player_start(controller)
    found = mode.find_player_start(controller,'')
    report.update(game_mode=mode.get_class().get_path_name(),
        chosen_start=chosen.get_path_name() if chosen else None,
        found_start=found.get_path_name() if found else None)
if pawn:
    report['pawn']={'class':pawn.get_class().get_path_name(),'position_cm':vec(pawn.get_actor_location()),
        'radius_cm':pawn.capsule_component.get_unscaled_capsule_radius(),
        'half_height_cm':pawn.capsule_component.get_unscaled_capsule_half_height()}
ignore = list(starts)+([pawn] if pawn else [])
for point in ([585,-91,652],[650,-150,652],[650,-150,672],[550,-200,672]):
    row = {'position_cm':point}
    try:
        result = unreal.SystemLibrary.capsule_trace_single_by_profile(world,unreal.Vector(*point),
            unreal.Vector(point[0],point[1],point[2]+.1),34.,90.,'Pawn',False,ignore,unreal.DrawDebugTrace.NONE,True)
        row['result_type'] = str(type(result))
        row['result'] = str(result)
        hit = result if isinstance(result,unreal.HitResult) else next((x for x in (result or []) if isinstance(x,unreal.HitResult)),None)
        if result is None:
            row['blocking_hit'] = False
        if hit:
            # NativeBreakFunc is exposed as StructBase.to_tuple, not as a
            # GameplayStatics method in this editor's Python bindings.
            values = hit.to_tuple()
            names = ['blocking_hit','initial_overlap','time','distance','location','impact_point','normal','impact_normal',
                     'physical_material','hit_actor','hit_component','hit_bone_name','bone_name','hit_item','element_index',
                     'face_index','trace_start','trace_end']
            row['hit'] = {name:str(value) for name,value in zip(names,values)}
    except Exception as exc:
        row['probe_error'] = repr(exc)
    report['probes'].append(row)
(ROOT/'Docs/HomesteadPilot/Runtime/spawn-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
