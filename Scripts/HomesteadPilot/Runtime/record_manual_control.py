"""Observe PIE keys and movement without injecting movement or changing assets.

Run while PIE is active, focus viewport, hold W/A/S/D and move mouse. A 30-second
observation writes key states, real positions and look rotation. Screenshot input
and actual path should accompany this receipt; it does not infer input from motion.
"""
import json
import math
import time
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'

class HomesteadManualRecorder:
    def __init__(self):
        auto_runner = getattr(unreal, '_homestead_traversal_runner', None)
        assert not auto_runner or auto_runner.finished, 'Stop automated traversal before recording manual input'
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.start = time.perf_counter()
        self.samples = []
        self.handle = None
        self.keys = {}
        self.done = False
        self.last_sample = 0
        for name in ['W', 'A', 'S', 'D']:
            key = unreal.Key()
            key.set_editor_property('key_name', name)
            self.keys[name] = key

    def finish(self, error=None):
        if self.done:
            return
        self.done = True
        if self.handle:
            unreal.unregister_slate_post_tick_callback(self.handle)
        distance = sum(math.dist(a['position_cm'], b['position_cm']) for a,b in zip(self.samples, self.samples[1:]))
        keyed_distance = sum(math.dist(a['position_cm'], b['position_cm']) for a,b in zip(self.samples, self.samples[1:])
                             if (a['keys_down'] or b['keys_down']) and 'WALKING' in b['movement_mode'])
        key_samples = sum(bool(row['keys_down']) for row in self.samples)
        data = {'duration_seconds': time.perf_counter()-self.start, 'error': error,
            'movement_injected_by_recorder': False, 'samples': self.samples,
            'key_samples': key_samples, 'distance_moved_cm': distance,
            'distance_while_keys_held_and_walking_cm': keyed_distance,
            'keyboard_movement_observed': key_samples > 2 and keyed_distance > 100,
            'scope': 'PIE controller real key-down states sampled alongside possessed pawn position; no automatic movement'}
        (OUT / 'manual-control-receipt.json').write_text(json.dumps(data, indent=2), encoding='utf-8')

    def tick(self, delta):
        if time.perf_counter()-self.start > 30:
            self.finish()
            return
        if time.perf_counter()-self.last_sample < .05:
            return
        try:
            world = self.editor.get_game_world()
            if not world:
                return
            assert 'StartingHome' in world.get_path_name()
            pawn = unreal.GameplayStatics.get_player_character(world, 0)
            controller = unreal.GameplayStatics.get_player_controller(world, 0)
            if not pawn or not controller:
                return
            p = pawn.get_actor_location()
            r = pawn.get_actor_rotation()
            self.samples.append({'t': time.perf_counter()-self.start, 'position_cm': [p.x,p.y,p.z],
                'yaw_degrees': r.yaw, 'keys_down': [n for n,k in self.keys.items() if controller.is_input_key_down(k)],
                'movement_mode': str(pawn.character_movement.movement_mode)})
            self.last_sample = time.perf_counter()
        except Exception as exc:
            self.finish(repr(exc))

previous = getattr(unreal, '_homestead_manual_recorder', None)
if previous and not previous.done:
    previous.finish('Replaced by another manual recording')
recorder = HomesteadManualRecorder()
unreal._homestead_manual_recorder = recorder
recorder.handle = unreal.register_slate_post_tick_callback(recorder.tick)
unreal.log('Recording manual PIE input for 30s; focus viewport and walk using WASD.')
