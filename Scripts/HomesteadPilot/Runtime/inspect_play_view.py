"""Read-only camera/possession query for editor and active PIE worlds."""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
out = {'worlds':[]}
for kind,world in [('editor',editor.get_editor_world()),('PIE',editor.get_game_world())]:
    if not world:
        continue
    assert 'StartingHome' in world.get_path_name()
    row = {'kind':kind,'world':world.get_path_name(),'cameras':[]}
    for camera in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.CameraActor):
        row['cameras'].append({'actor':camera.get_path_name(),'label':camera.get_actor_label(),
            'auto_activate_for_player':str(camera.get_editor_property('auto_activate_for_player')),
            'auto_activate_player_index':camera.get_auto_activate_player_index()})
    if kind == 'PIE':
        controller = unreal.GameplayStatics.get_player_controller(world,0)
        pawn = unreal.GameplayStatics.get_player_character(world,0)
        target = controller.get_view_target() if controller else None
        manager = controller.player_camera_manager if controller else None
        row.update(controller=controller.get_path_name() if controller else None,
                   pawn=pawn.get_path_name() if pawn else None,
                   view_target=target.get_path_name() if target else None,
                   view_target_is_pawn=bool(pawn and target==pawn))
        if manager:
            p,r = manager.get_camera_location(),manager.get_camera_rotation()
            row['actual_camera']={'location_cm':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],
                                  'fov':manager.get_fov_angle()}
    out['worlds'].append(row)
(ROOT/'Docs/HomesteadPilot/Runtime/play-view-inspection.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
