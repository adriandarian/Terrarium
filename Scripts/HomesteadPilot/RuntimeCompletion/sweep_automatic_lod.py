"""Finite editor camera approach/retreat, keeping every pilot component automatic.

No mesh/actor edits or saves. Repositions only the level viewport, then restores it.
Root must unpilot any review camera before running. Optional native captures are
stills from an automatically selected LOD camera sweep, not forced-LOD snapshots.
Rendered LOD indices are not exposed by this recorder; visual review is required.
"""
import json
import math
import time
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/RuntimeCompletion'
REQUEST = json.loads((OUT / 'lod-sweep-request.json').read_text(encoding='utf-8'))
tag = REQUEST.get('output_tag', '')
assert not tag or (tag.replace('-', '').replace('_', '').isalnum()), 'Use a simple output_tag directory name'
RUN_OUT = OUT / tag if tag else OUT
RUN_OUT.mkdir(parents=True, exist_ok=True)

def xyz(value):
    return [value.x, value.y, value.z]

class LODSweep:
    def __init__(self):
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        assert not self.editor.get_game_world(), 'End PIE before viewport sweep'
        assert self.editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
        self.lod_cvars = {name: unreal.SystemLibrary.get_console_variable_float_value(name)
            for name in ['r.ForceLOD', 'foliage.ForceLOD', 'r.StaticMeshLODDistanceScale', 'r.ViewDistanceScale']}
        assert self.lod_cvars['r.ForceLOD'] == -1, 'Disable global r.ForceLOD before automatic review'
        assert self.lod_cvars['foliage.ForceLOD'] == -1, 'Disable global foliage.ForceLOD before automatic review'
        self.original_camera = self.editor.get_level_viewport_camera_info()
        assert self.original_camera, 'No level viewport'
        self.settings = unreal.get_default_object(unreal.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        self.throttle = self.settings.get_editor_property('bThrottleCPUWhenNotForeground')
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
        self.pilot_components = []
        candidates = []
        for actor in actors:
            for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
                mesh = comp.get_editor_property('static_mesh')
                if mesh and '/HomesteadPilot/' in mesh.get_path_name():
                    assert comp.get_editor_property('forced_lod_model') == 0, 'Restore forced LOD 0 before sweep: ' + comp.get_path_name()
                    self.pilot_components.append(comp)
                    if mesh.get_num_lods() >= 3 and not isinstance(comp, unreal.InstancedStaticMeshComponent):
                        candidates.append((actor, mesh))
        labels = REQUEST.get('actor_labels', [])
        if labels:
            self.targets = [(a,m) for a,m in candidates if a.get_actor_label() in labels]
            assert set(a.get_actor_label() for a,m in self.targets) == set(labels), 'Requested actors missing or lack 3 LODs'
        else:
            self.targets = [(a,m) for a,m in candidates if 'cottage' in m.get_name().lower()][:1]
        assert self.targets, 'No sweep targets'
        self.settings.set_editor_property('bThrottleCPUWhenNotForeground', False)
        self.started = time.perf_counter()
        self.handle = None
        self.done = False
        self.samples = []
        self.captures = []
        self.last_sample = 0
        self.captured = set()

    def finish(self, error=None):
        if self.done:
            return
        self.done = True
        if self.handle:
            unreal.unregister_slate_post_tick_callback(self.handle)
        self.editor.set_level_viewport_camera_info(*self.original_camera)
        self.settings.set_editor_property('bThrottleCPUWhenNotForeground', self.throttle)
        # We never force a component, and independently read back every one.
        zeros = all(c.get_editor_property('forced_lod_model') == 0 for c in self.pilot_components)
        data = {'error': error, 'request': REQUEST, 'pilot_components': len(self.pilot_components),
            'lod_console_variables': self.lod_cvars,
            'forced_lod_zero_before_and_after': zeros, 'camera_restored': True,
            'throttle_restored': self.settings.get_editor_property('bThrottleCPUWhenNotForeground') == self.throttle,
            'samples': self.samples, 'captures': self.captures,
            'visual_smoothness_verified': False, 'actual_rendered_lod_indices_observed': False,
            'scope': 'Continuous approach/retreat of editor viewport with automatic component LODs. Distance samples and optional auto-LOD stills are evidence for a visual reviewer; not a rendered-LOD-index query or gameplay walking test.'}
        (RUN_OUT / 'automatic-lod-sweep.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
        unreal.log('RuntimeCompletion automatic LOD sweep done; viewport restored: ' + str(error or 'OK'))

    def tick(self, delta):
        try:
            assert not self.editor.get_game_world(), 'PIE started during viewport sweep'
            elapsed = time.perf_counter()-self.started
            seconds = float(REQUEST.get('seconds_per_actor', 24))
            index = int(elapsed/seconds)
            if index >= len(self.targets):
                self.finish()
                return
            local = elapsed-index*seconds
            actor, mesh = self.targets[index]
            center, extents = actor.get_actor_bounds(False)
            radius = max(extents.length(), 20)
            phase = local/seconds
            # Logarithmic distance gives the near thresholds sufficient time.
            out_back = 1-abs(2*phase-1)
            multiplier = 1.5 * (30/1.5)**out_back
            distance = radius*multiplier
            offset = unreal.Vector(.82*distance, -.52*distance, .24*distance)
            location = center+offset
            rotation = unreal.MathLibrary.find_look_at_rotation(location, center)
            self.editor.set_level_viewport_camera_info(location, rotation)
            if elapsed-self.last_sample >= .1:
                self.last_sample = elapsed
                self.samples.append({'t': elapsed, 'actor': actor.get_actor_label(), 'mesh': mesh.get_path_name(),
                    'camera_cm': xyz(location), 'target_cm': xyz(center), 'bounds_radius_cm': radius,
                    'distance_cm': distance, 'direction': 'retreat' if phase<.5 else 'approach',
                    'forced_lod_model': 0})
            if REQUEST.get('capture_stills', True):
                for sample_phase, name in [(.08,'near'),(.27,'middle'),(.48,'far'),(.74,'return-middle'),(.92,'return-near')]:
                    key = (index, name)
                    if phase >= sample_phase and key not in self.captured:
                        self.captured.add(key)
                        filename = RUN_OUT / ('lod-' + str(index) + '-' + name + '.png')
                        task = unreal.AutomationLibrary.take_high_res_screenshot(1280, 720, str(filename))
                        self.captures.append({'actor': actor.get_actor_label(), 't': elapsed,
                            'path': str(filename), 'request_accepted': task is not None,
                            'distance_cm': distance})
                        break
        except Exception as exc:
            self.finish(repr(exc))

prior = getattr(unreal, '_homestead_lod_sweep', None)
if prior and not prior.done:
    prior.finish('Replaced by another sweep')
sweep = LODSweep()
unreal._homestead_lod_sweep = sweep
sweep.handle = unreal.register_slate_post_tick_callback(sweep.tick)
unreal.log('RuntimeCompletion automatic LOD sweep started; finite timeline and viewport restoration.')
