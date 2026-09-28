"""Finite PIE trace microbenchmark. No collision mutations, movement or saving.

This measures Python-to-Unreal query latency, not total physics frame cost. Run
separately from frame profiling. Alternate simple/complex batches each tick.
"""
import json
import statistics
import time
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/RuntimeCompletion'
CONFIG = json.loads((ROOT / 'Docs/HomesteadPilot/Runtime/runtime-config.json').read_text())

class QueryBenchmark:
    def __init__(self):
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.armed = time.perf_counter()
        self.started = None
        self.done = False
        self.handle = None
        self.batches = []
        self.points = []
        for route in CONFIG['test_routes']:
            for point in [route['start_cm']] + route['waypoints_cm']:
                self.points.append((route['name'], point))

    def finish(self, error=None):
        if self.done:
            return
        self.done = True
        if self.handle:
            unreal.unregister_slate_post_tick_callback(self.handle)
        summary = {}
        for mode in (False, True):
            rows = [r for r in self.batches if r['trace_complex'] == mode and not r['warmup']]
            costs = sorted(r['microseconds_per_query'] for r in rows)
            summary[str(mode)] = {'measured_batches': len(rows),
                'queries': sum(r['query_count'] for r in rows),
                'mean_us_per_query': statistics.mean(costs) if costs else None,
                'p95_batch_us_per_query': costs[int(.95*(len(costs)-1))] if costs else None,
                'query_results_returned': sum(r['results_returned'] for r in rows)}
        data = {'error': error, 'world': getattr(self, 'world_path', None), 'summary': summary,
            'batches': self.batches, 'input_or_movement_injected': False,
            'collision_modified': False,
            'method': 'Alternating simple/complex Visibility vertical line traces at current route checkpoints; 4 repeats per point; first two ticks warmup.',
            'limits': 'Python-to-Unreal call overhead included. Hit return counts are smoke coverage, not route traversal. Timings are synchronous query microbenchmarks, not CharacterMovement, total scene physics, game-thread, GPU or shipping timings.'}
        (OUT / 'collision-query-benchmark.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
        unreal.log('RuntimeCompletion collision query benchmark complete: ' + str(error or 'OK'))

    def tick(self, delta):
        try:
            now = time.perf_counter()
            if now-self.armed > 90:
                self.finish('90-second timeout')
                return
            world = self.editor.get_game_world()
            if not world:
                if self.started:
                    self.finish('PIE ended during benchmark')
                return
            assert 'StartingHome' in world.get_path_name()
            self.world_path = world.get_path_name()
            if self.started is None:
                self.started = now
            if now-self.started < 3:
                return
            if len(self.batches) >= 24:
                self.finish()
                return
            complex_trace = bool(len(self.batches) % 2)
            pawn = unreal.GameplayStatics.get_player_character(world, 0)
            returned = 0
            count = 0
            began = time.perf_counter_ns()
            for repeat in range(4):
                for _, point in self.points:
                    hit = unreal.SystemLibrary.line_trace_single(
                        world_context_object=world,
                        start=unreal.Vector(point[0], point[1], point[2]+100),
                        end=unreal.Vector(point[0], point[1], point[2]-350),
                        trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                        trace_complex=complex_trace, actors_to_ignore=[pawn] if pawn else [],
                        draw_debug_type=unreal.DrawDebugTrace.NONE, ignore_self=True)
                    returned += hit is not None
                    count += 1
            duration_us = (time.perf_counter_ns()-began)/1000
            self.batches.append({'trace_complex': complex_trace, 'warmup': len(self.batches)<2,
                'query_count': count, 'results_returned': returned,
                'duration_us': duration_us, 'microseconds_per_query': duration_us/count})
        except Exception as exc:
            self.finish(repr(exc))

prior = getattr(unreal, '_homestead_query_benchmark', None)
if prior and not prior.done:
    prior.finish('Replaced by a new benchmark')
benchmark = QueryBenchmark()
unreal._homestead_query_benchmark = benchmark
benchmark.handle = unreal.register_slate_post_tick_callback(benchmark.tick)
unreal.log('RuntimeCompletion collision benchmark armed; 3s PIE warmup then 24 tick batches.')
