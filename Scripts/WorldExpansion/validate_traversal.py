"""PIE walking traversal and frame pacing evidence, driven by real Character movement.

Run in editor, then start Play (or run while playing). Routes in traversal-request.json
provide capsule-center start/waypoints. Teleport only places the test at its initial
start; AddMovementInput traverses every segment with gravity/collision enabled.
This proves collision traversal, not physical keyboard input; capture keyboard
control separately using record_manual_control.py. No scene or assets are saved.
"""
import ctypes
from ctypes import wintypes
import json
import math
import statistics
import time
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/WorldExpansion'
CONFIG = json.loads((OUT / 'traversal-request.json').read_text())
assert CONFIG.get('test_routes'), 'Set test_routes using the assembled map before running'

def vec(v):
    return [v.x, v.y, v.z]

def process_memory():
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ['PeakWorkingSetSize', 'WorkingSetSize',
            'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
            'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage', 'PrivateUsage']]
    value = Counters()
    value.cb = ctypes.sizeof(value)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    assert psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(value), value.cb)
    return {'editor_process_working_set_bytes': value.WorkingSetSize,
            'editor_process_private_bytes': value.PrivateUsage,
            'scope': 'Entire editor process with PIE, not standalone game or GPU memory'}

class WorldExpansionTraversalRunner:
    def __init__(self):
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.started = time.perf_counter()
        self.pawn = None
        self.index = -1
        self.waypoint = 0
        self.arrival_at = None
        self.results = []
        self.samples = []
        self.trace = []
        self.last_frame = None
        self.handle = None
        self.finished = False
        settings_class = unreal.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings')
        assert settings_class, 'EditorPerformanceSettings class is not loaded'
        self.performance_settings = unreal.get_default_object(settings_class)
        self.previous_throttle = self.performance_settings.get_editor_property('bThrottleCPUWhenNotForeground')
        self.performance_settings.set_editor_property('bThrottleCPUWhenNotForeground', False)
        self.original_speed = None

    def finish(self, error=None):
        if self.finished:
            return
        self.finished = True
        self.performance_settings.set_editor_property('bThrottleCPUWhenNotForeground', self.previous_throttle)
        if self.pawn:
            try:
                self.pawn.character_movement.stop_movement_immediately()
                if self.original_speed is not None:
                    self.pawn.character_movement.set_editor_property('max_walk_speed', self.original_speed)
            except Exception:
                pass  # PIE may have already destroyed the pawn; restore editor setting regardless.
        if self.handle:
            unreal.unregister_slate_post_tick_callback(self.handle)
        values = sorted(self.samples)
        percentile = lambda p: values[min(len(values)-1, int((len(values)-1)*p))] if values else None
        data = {'level': '/Game/Terrarium/WorldExpansion/Maps/ValleyRegion',
            'measurement': 'Possessed PIE Character driven by AddMovementInput; real gravity and collision',
            'physical_keyboard_input_test': 'Separate manual-control receipt required',
            'waypoint_approach': 'Transient maximum walking speed decreases near targets to prevent frame-step overshoot; original speed restored at end',
            'background_throttle_disabled_during_test': True,
            'background_throttle_restored': self.performance_settings.get_editor_property('bThrottleCPUWhenNotForeground') == self.previous_throttle,
            'routes': self.results, 'all_routes_passed': not error and len(self.results) == len(CONFIG['test_routes']) and all(r['passed'] for r in self.results),
            'error': error, 'trace': self.trace,
            'frame_pacing': {'source': 'GameplayStatics.get_world_delta_seconds; one sample per unique engine frame after warmup',
                'samples': len(values), 'mean_ms': statistics.mean(values) if values else None,
                'median_ms': percentile(.5), 'p95_ms': percentile(.95), 'max_ms': max(values) if values else None,
                'scope': 'PIE world delta including editor overhead; not GPU/CPU profiler timings'},
            'memory': process_memory(), 'wall_seconds': time.perf_counter()-self.started}
        (OUT / CONFIG.get('output_file','traversal-receipt.json')).write_text(json.dumps(data, indent=2), encoding='utf-8')
        unreal.log('WorldExpansion traversal complete: ' + str(data['all_routes_passed']))

    def next_route(self):
        self.index += 1
        if self.index >= len(CONFIG['test_routes']):
            self.finish()
            return
        self.route = CONFIG['test_routes'][self.index]
        self.waypoint = 0
        self.arrival_at = None
        self.pawn.character_movement.stop_movement_immediately()
        self.pawn.set_actor_location(unreal.Vector(*self.route['start_cm']), False, True)
        self.pawn.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING)
        self.route_start = time.perf_counter()
        self.segment_start = self.route_start + 1.5
        self.warmup_until = self.segment_start
        self.result = {'name': self.route['name'], 'start_cm': self.route['start_cm'], 'waypoints': [], 'passed': False}
        self.results.append(self.result)

    def tick(self, delta):
        try:
            self.update()
        except Exception as exc:
            self.finish(repr(exc))

    def update(self):
        world = self.editor.get_game_world()
        if not world:
            if self.pawn:
                self.finish('PIE ended before traversal finished')
                return
            if time.perf_counter()-self.started > 120:
                self.finish('PIE world did not become available within 120s')
            return
        assert 'ValleyRegion' in world.get_path_name(), world.get_path_name()
        if not self.pawn:
            self.pawn = unreal.GameplayStatics.get_player_character(world, 0)
            if not self.pawn:
                return
            assert 'BP_HomesteadExplorer' in self.pawn.get_class().get_path_name(), self.pawn.get_class().get_path_name()
            assert self.pawn.get_controller(), 'Pawn must be possessed'
            assert self.pawn.get_controller().get_view_target() == self.pawn, 'An inherited review camera is overriding the playable pawn view; run fix_play_view.py'
            self.original_speed = self.pawn.character_movement.get_editor_property('max_walk_speed')
            self.next_route()
            return
        now = time.perf_counter()
        if now < self.warmup_until:
            return
        frame = unreal.SystemLibrary.get_frame_count()
        if frame == self.last_frame:
            return
        self.last_frame = frame
        dt = unreal.GameplayStatics.get_world_delta_seconds(world)
        if dt > 0:
            self.samples.append(dt * 1000.)
        location = self.pawn.get_actor_location()
        movement = self.pawn.character_movement
        target = self.route['waypoints_cm'][self.waypoint]
        dx, dy = target[0]-location.x, target[1]-location.y
        distance = math.hypot(dx, dy)
        if len(self.samples) % 10 == 0:
            self.trace.append({'route': self.route['name'], 'waypoint': self.waypoint,
                'position_cm': vec(location), 'movement_mode': str(movement.movement_mode),
                'speed_cm_s': self.pawn.get_velocity().length(), 'frame_delta_ms': dt*1000.})
        if location.z < min(target[2], self.route['start_cm'][2]) - 350:
            self.result['failure'] = 'Fell below the route floor'
            self.next_route()
            return
        if distance < self.route.get('xy_tolerance_cm', 35):
            valid_z = abs(location.z-target[2]) < self.route.get('z_tolerance_cm', 45)
            grounded = movement.movement_mode == unreal.MovementMode.MOVE_WALKING
            if not valid_z or not grounded:
                # A legitimate descending step can still be in its short falling
                # phase at the arrival frame. Allow gravity to settle the pawn.
                if self.arrival_at is None:
                    self.arrival_at = now
                if now-self.arrival_at < 1.5:
                    return
            self.result['waypoints'].append({'target_cm': target, 'actual_cm': vec(location), 'correct_height': valid_z,
                'grounded': grounded, 'elapsed_wall_s': now-self.segment_start})
            if not valid_z or not grounded:
                self.result['failure'] = 'Reached XY without expected walkable elevation'
                self.next_route()
                return
            self.waypoint += 1
            self.arrival_at = None
            self.segment_start = now
            if self.waypoint >= len(self.route['waypoints_cm']):
                self.result['passed'] = True
                self.next_route()
            return
        self.arrival_at = None
        if now-self.segment_start > self.route.get('segment_timeout_s', 20.):
            self.result['failure'] = 'Movement timeout at waypoint ' + str(self.waypoint)
            self.result['stopped_cm'] = vec(location)
            self.next_route()
            return
        direction = unreal.Vector(dx/distance, dy/distance, 0.)
        # The background editor can otherwise step past a narrow acceptance circle
        # on alternating frames. This changes walking speed, never pawn position.
        approach_speed = min(self.original_speed, max(20., distance / max(dt * 2., .15)))
        movement.set_editor_property('max_walk_speed', approach_speed)
        self.pawn.add_movement_input(direction, 1., True)
        self.pawn.set_actor_rotation(unreal.Rotator(pitch=0., yaw=math.degrees(math.atan2(dy, dx)), roll=0.), False)

previous = getattr(unreal, '_world_expansion_traversal_runner', None)
if previous and not previous.finished:
    previous.finish('Replaced by a new traversal run')
runner = WorldExpansionTraversalRunner()
unreal._world_expansion_traversal_runner = runner
runner.handle = unreal.register_slate_post_tick_callback(runner.tick)
unreal.log('WorldExpansion traversal armed. Start PIE if it is not already playing.')

