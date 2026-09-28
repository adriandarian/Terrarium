"""Measure local PIE frame pacing and editor memory with background throttle disabled.

Arm before PIE or while playing. Warm up 5 seconds then sample 20 seconds. Restores the
previous foreground-throttle preference without saving user settings. Keep the
desired gameplay camera active; this script does not move the pawn or camera.
"""
import ctypes
from ctypes import wintypes
import json
import platform
import statistics
import time
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'

def memory_bytes():
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ['PeakWorkingSetSize','WorkingSetSize',
             'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
             'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage']]
    value = Counters()
    value.cb = ctypes.sizeof(value)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    assert psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(value), value.cb)
    return {'working_set_bytes':value.WorkingSetSize,'private_bytes':value.PrivateUsage}

class HomesteadPerformanceSampler:
    def __init__(self):
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        settings_class = unreal.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings')
        assert settings_class, 'EditorPerformanceSettings class is not loaded'
        self.settings = unreal.get_default_object(settings_class)
        self.previous_throttle = self.settings.get_editor_property('bThrottleCPUWhenNotForeground')
        self.settings.set_editor_property('bThrottleCPUWhenNotForeground', False)
        self.armed_at = time.perf_counter()
        self.warmup_at = None
        self.samples = []
        self.last_frame = None
        self.handle = None
        self.done = False

    def finish(self, error=None):
        if self.done:
            return
        self.done = True
        self.settings.set_editor_property('bThrottleCPUWhenNotForeground', self.previous_throttle)
        if self.handle:
            unreal.unregister_slate_post_tick_callback(self.handle)
        values = sorted(x['frame_delta_ms'] for x in self.samples)
        pct = lambda fraction: values[min(len(values)-1,int((len(values)-1)*fraction))] if values else None
        report = {'error':error,'level':'/Game/Terrarium/HomesteadPilot/Maps/StartingHome',
            'engine':unreal.SystemLibrary.get_engine_version(),'os':platform.platform(),
            'viewport_size':str(self.editor.get_level_viewport_size()),
            'warmup_seconds':5,'sample_window_seconds':20,'sample_count':len(values),
            'frame_ms':{'mean':statistics.mean(values) if values else None,'median':pct(.5),'p95':pct(.95),'max':max(values) if values else None},
            'memory_start':getattr(self,'memory_start',None),'memory_end':memory_bytes(),
            'prior_background_throttle':self.previous_throttle,
            'throttle_disabled_during_measurement':True,
            'throttle_restored':self.settings.get_editor_property('bThrottleCPUWhenNotForeground') == self.previous_throttle,
            'console_variables':{name:unreal.SystemLibrary.get_console_variable_float_value(name) for name in ['t.MaxFPS','r.VSync','r.ScreenPercentage','r.DynamicRes.OperationMode']},
            'samples':self.samples,
            'limits':'Actual PIE world delta and whole editor process memory; not standalone or GPU/CPU-separated timings. No city-scale budget inferred.'}
        (OUT / 'performance-receipt.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        unreal.log('Homestead performance sample complete; background throttle restored.')

    def tick(self, delta):
        try:
            world = self.editor.get_game_world()
            now = time.perf_counter()
            if not world:
                if self.warmup_at:
                    self.finish('PIE ended before sample completed')
                elif now-self.armed_at > 120:
                    self.finish('PIE did not start within 120 seconds')
                return
            assert 'StartingHome' in world.get_path_name()
            if self.warmup_at is None:
                self.warmup_at = now
                return
            elapsed = now-self.warmup_at
            if elapsed < 5:
                return
            if elapsed >= 25:
                self.finish()
                return
            if not hasattr(self,'memory_start'):
                self.memory_start = memory_bytes()
            frame = unreal.SystemLibrary.get_frame_count()
            if frame == self.last_frame:
                return
            self.last_frame = frame
            pawn = unreal.GameplayStatics.get_player_character(world,0)
            assert pawn and pawn.get_controller().get_view_target() == pawn, 'Performance sample requires the actual explorer view'
            p = pawn.get_actor_location() if pawn else unreal.Vector()
            self.samples.append({'t':elapsed-5,'frame_delta_ms':unreal.GameplayStatics.get_world_delta_seconds(world)*1000,
                                 'pawn_cm':[p.x,p.y,p.z]})
        except Exception as exc:
            self.finish(repr(exc))

prior = getattr(unreal,'_homestead_performance_sampler',None)
if prior and not prior.done:
    prior.finish('Replaced by another performance sample')
sampler = HomesteadPerformanceSampler()
unreal._homestead_performance_sampler = sampler
sampler.handle = unreal.register_slate_post_tick_callback(sampler.tick)
unreal.log('Homestead performance sampler armed; start PIE. Warmup 5s, sample 20s, throttle auto-restores.')
