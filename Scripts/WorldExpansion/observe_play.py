"""Passive finite PIE input/frame recorder. Never teleports or injects input.

Arm, start fresh PIE, focus gameplay, then hold each WASD key separately in a clear
space. Source remains unverified unless a coordinator records an actual human hold.
Use a separate idle run for performance: input activity invalidates idle comparison.
"""
import ctypes
import json
import math
import statistics
import time
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/WorldExpansion'
REQUEST = json.loads((OUT / 'observation-request.json').read_text(encoding='utf-8'))
assert REQUEST['name'] in ('idle', 'input', 'city')

def xyz(value):
    return [value.x, value.y, value.z]

class Observer:
    def __init__(self):
        for name, flag in [('_world_expansion_traversal_runner', 'finished'),
                           ('_homestead_performance_sampler', 'done')]:
            prior = getattr(unreal, name, None)
            assert not prior or getattr(prior, flag), 'Stop previous runtime harness: ' + name
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.settings = unreal.get_default_object(unreal.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        self.throttle = self.settings.get_editor_property('bThrottleCPUWhenNotForeground')
        self.settings.set_editor_property('bThrottleCPUWhenNotForeground', False)
        self.armed = time.perf_counter()
        self.started = None
        self.done = False
        self.handle = None
        self.last_frame = None
        self.samples = []
        self.keys = {}
        self.win = ctypes.WinDLL('user32', use_last_error=True)
        self.win.GetAsyncKeyState.argtypes = [ctypes.c_int]
        self.win.GetAsyncKeyState.restype = ctypes.c_short
        self.win.GetForegroundWindow.restype = ctypes.c_void_p
        for name in 'WASD':
            key = unreal.Key()
            key.set_editor_property('key_name', name)
            self.keys[name] = key

    def finish(self, error=None):
        if self.done:
            return
        self.done = True
        if self.handle:
            unreal.unregister_slate_post_tick_callback(self.handle)
        self.settings.set_editor_property('bThrottleCPUWhenNotForeground', self.throttle)
        values = sorted(r['frame_ms'] for r in self.samples)
        percentile = lambda p: values[int((len(values)-1)*p)] if values else None
        holds = []
        for key in 'WASD':
            run = []
            for row in self.samples + [None]:
                if row and key in row['controller_keys'] and key in row['os_keys']:
                    run.append(row)
                elif run:
                    elapsed = run[-1]['t'] - run[0]['t']
                    if elapsed >= .2:
                        holds.append({'key': key, 'duration_s': elapsed, 'samples': len(run),
                            'displacement_cm': math.dist(run[0]['position_cm'], run[-1]['position_cm']),
                            'walking_samples': sum('WALKING' in r['movement_mode'] for r in run)})
                    run = []
        self.report = {'error': error, 'request': REQUEST, 'warmup_s': 5, 'sample_window_s': 20,
            'sample_count': len(values), 'frame_ms': {'mean': statistics.mean(values) if values else None,
                'median': percentile(.5), 'p95': percentile(.95), 'max': max(values) if values else None},
            'observed_holds': holds, 'input_activity_observed': any(r['controller_keys'] or r['os_keys'] for r in self.samples),
            'movement_injected': False, 'camera_or_pawn_repositioned': False,
            'physical_hardware_source_verified': False,
            'throttle_restored': self.settings.get_editor_property('bThrottleCPUWhenNotForeground') == self.throttle,
            'engine': unreal.SystemLibrary.get_engine_version(),
            'viewport_size': str(self.editor.get_level_viewport_size()),
            'cvars': {k: unreal.SystemLibrary.get_console_variable_float_value(k) for k in ['t.MaxFPS','r.VSync','r.ScreenPercentage','r.DynamicRes.OperationMode']},
            'samples': self.samples,
            'limits': 'OS+controller holds distinguish held keys from AddMovementInput, but software-generated OS events cannot be distinguished from physical hardware by this observer. Frame deltas include editor overhead; no CPU/GPU attribution or city-scale claim.'}
        (OUT / (REQUEST['name'] + '-observation.json')).write_text(json.dumps(self.report, indent=2), encoding='utf-8')
        unreal.log('WorldExpansion observer finished: ' + str(error or 'OK'))

    def tick(self, delta):
        try:
            now = time.perf_counter()
            world = self.editor.get_game_world()
            if not world:
                if self.started:
                    self.finish('PIE ended during observation')
                elif now-self.armed > 90:
                    self.finish('PIE did not start within 90 seconds')
                return
            assert 'ValleyRegion' in world.get_path_name(), world.get_path_name()
            pawn = unreal.GameplayStatics.get_player_character(world, 0)
            controller = unreal.GameplayStatics.get_player_controller(world, 0)
            if not pawn or not controller:
                assert now-self.armed < 90, 'Pawn/controller missing for 90 seconds'
                return
            assert controller.get_view_target() == pawn, 'Gameplay camera is not possessed explorer'
            if self.started is None:
                self.started = now
            elapsed = now-self.started
            if elapsed >= 25:
                self.finish()
                return
            if elapsed < 5:
                return
            frame = unreal.SystemLibrary.get_frame_count()
            if frame == self.last_frame:
                return
            self.last_frame = frame
            rotation = controller.get_control_rotation()
            self.samples.append({'t': elapsed-5, 'frame_ms': 1000*unreal.GameplayStatics.get_world_delta_seconds(world),
                'position_cm': xyz(pawn.get_actor_location()), 'velocity_cm_s': xyz(pawn.get_velocity()),
                'control_rotation': [rotation.pitch, rotation.yaw, rotation.roll],
                'movement_mode': str(pawn.character_movement.movement_mode),
                'controller_keys': [k for k,v in self.keys.items() if controller.is_input_key_down(v)],
                'os_keys': [k for k in self.keys if self.win.GetAsyncKeyState(ord(k)) & 0x8000],
                'foreground_hwnd': self.win.GetForegroundWindow()})
        except Exception as exc:
            self.finish(repr(exc))

prior = getattr(unreal, '_world_expansion_observer', None)
if prior and not prior.done:
    prior.finish('Replaced by new observation')
observer = Observer()
unreal._world_expansion_observer = observer
observer.handle = unreal.register_slate_post_tick_callback(observer.tick)
unreal.log('WorldExpansion passive observer armed: 5s warmup + 20s sample; timeout 90s.')

