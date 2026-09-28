"""Observe three seconds of a fresh PIE spawn; never teleports or drives the pawn.

Run after starting a NEW default PIE session without a StartTransform override,
before any traversal harness. Requires the saved PlayerStart position, grounded
CharacterMovement and the player's actual eye camera above the courtyard.
"""
import json
import math
import time
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT/'Docs/HomesteadPilot/Runtime'
config = json.loads((OUT/'runtime-config.json').read_text())
active = getattr(unreal,'_homestead_traversal_runner',None)
assert not active or active.finished, 'Finish automated movement before starting a NEW PIE spawn check'

class FreshSpawnObserver:
    def __init__(self):
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.started = time.perf_counter()
        self.handle = None
        self.samples = []
        self.done = False
        self.last_frame = None

    def finish(self,error=None):
        if self.done:
            return
        self.done = True
        if self.handle:
            unreal.unregister_slate_post_tick_callback(self.handle)
        checks = ['near_configured_spawn','grounded','correct_floor_height','camera_above_courtyard','view_target_is_pawn','valid_selected_start']
        passed = bool(self.samples) and not error and all(all(row[name] for name in checks) for row in self.samples)
        (OUT/'fresh-spawn-verification.json').write_text(json.dumps({'passed':passed,'error':error,
            'configured_spawn_cm':config['spawn_cm'],'observation_seconds':time.perf_counter()-self.started,
            'teleports_or_movement_injected':False,'samples':self.samples},indent=2),encoding='utf-8')
        unreal.log('Fresh default PIE spawn verified: '+str(passed))

    def tick(self,delta):
        try:
            world = self.editor.get_game_world()
            assert world and 'StartingHome' in world.get_path_name(), 'Start a new default PIE session first'
            frame = unreal.SystemLibrary.get_frame_count()
            if frame == self.last_frame:
                return
            self.last_frame = frame
            pawn = unreal.GameplayStatics.get_player_character(world,0)
            pc = unreal.GameplayStatics.get_player_controller(world,0)
            mode = unreal.GameplayStatics.get_game_mode(world)
            assert pawn and pc and mode
            assert 'BP_HomesteadExplorer' in pawn.get_class().get_path_name()
            # FindPlayerStart returns this controller's cached actual StartSpot;
            # ChoosePlayerStart would re-test a spot now occupied by this pawn.
            start = mode.find_player_start(pc,'')
            p = pawn.get_actor_location()
            camera = pc.player_camera_manager.get_camera_location()
            expected = config['spawn_cm']
            self.samples.append({'world_time_seconds':unreal.GameplayStatics.get_time_seconds(world),
                'pawn_cm':[p.x,p.y,p.z],'camera_cm':[camera.x,camera.y,camera.z],
                'near_configured_spawn':math.hypot(p.x-expected[0],p.y-expected[1])<50.,
                'grounded':pawn.character_movement.movement_mode==unreal.MovementMode.MOVE_WALKING,
                'correct_floor_height':600.<p.z<expected[2]+20.,
                'camera_above_courtyard':camera.z>=600.,'view_target_is_pawn':pc.get_view_target()==pawn,
                'valid_selected_start':isinstance(start,unreal.PlayerStart),
                'selected_start':start.get_path_name() if start else None})
            if time.perf_counter()-self.started>=3.:
                self.finish()
        except Exception as exc:
            self.finish(repr(exc))

observer = FreshSpawnObserver()
unreal._homestead_fresh_spawn_observer = observer
observer.handle = unreal.register_slate_post_tick_callback(observer.tick)
unreal.log('Observing fresh PIE spawn for three seconds without moving the pawn.')
