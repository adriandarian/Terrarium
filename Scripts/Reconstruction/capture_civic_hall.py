"""Native front/back captures of the latest civic hall; no studio edits."""
import json
import time
from pathlib import Path
import unreal

assert Path(unreal.Paths.get_project_file_path()).name == 'Terrarium.uproject'
root = Path(unreal.Paths.project_dir())
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if '/Reconstruction/Maps/ReviewStage' not in str(levels.get_current_level()):
    assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'Preserve unsaved editor maps before capture'
    assert levels.load_level('/Game/Terrarium/Reconstruction/Maps/ReviewStage')
code = (root / 'Scripts/Reconstruction/capture.py').read_text()
requests = []
rows = [json.loads(p.read_text()) for p in (root / 'Docs/Reconstruction/Builds').glob('SM_Recon_CivicHall_R*.json')]
latest_revision = max(row['revision'] for row in rows)
for revision in (latest_revision,):
    for view, yaw in [('front', 115), ('back', 295)]:
        name = 'SM_Recon_CivicHall_R' + str(revision)
        request = {'asset': '/Game/Terrarium/Reconstruction/Meshes/' + name,
                   'name': name + '-' + view,
                   'yaw': yaw, 'pitch': -24, 'resolution': 1254}
        requests.append(request)
if latest_revision>=6:
    for view,focus,distance,yaw,pitch in [
        ('entrance',[0,-200,180],1400,105,-12),
        ('rear-stone',[0,165,92],2900,280,-9)]:
        requests.append({'asset':'/Game/Terrarium/Reconstruction/Meshes/SM_Recon_CivicHall_R'+str(latest_revision),
                         'name':'SM_Recon_CivicHall_R'+str(latest_revision)+'-'+view,
                         'focus':focus,'distance':distance,'yaw':yaw,'pitch':pitch,'resolution':1254})

# Yield actual editor frames between shots: a tight loop can capture stale
# material resources and camera transforms while shaders/scene proxies update.
state = {'index': 0, 'next': time.monotonic() + 3.0}


def capture_tick(delta):
    if time.monotonic() < state['next']:
        return
    try:
        request = requests[state['index']]
        (root / 'Saved/reconstruction-capture.json').write_text(json.dumps(request))
        exec(compile(code, 'capture.py', 'exec'), {'__name__': '__main__'})
        state['index'] += 1
        state['next'] = time.monotonic() + 2.0
        if state['index'] == len(requests):
            unreal.unregister_slate_post_tick_callback(state['handle'])
            (root / 'Docs/Reconstruction/Renders' / ('CivicHall-R' + str(latest_revision) + '-capture.json')).write_text(json.dumps({
                'views': requests, 'lighting': 'unchanged saved ReviewStage',
                'render': 'native Unreal Lit; frames yielded between shots',
                'resolution': [1254, 1254]}, indent=2))
            unreal.log('CIVIC_HALL_MATCHED_CAPTURES_COMPLETE')
    except Exception:
        unreal.unregister_slate_post_tick_callback(state['handle'])
        raise


state['handle'] = unreal.register_slate_post_tick_callback(capture_tick)
