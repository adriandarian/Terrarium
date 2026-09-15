"""Matched native capture with only background softness toggled."""
import unreal,sys,json,importlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir())
sys.path.insert(0,str(root/'Scripts/Fidelity'))
import atmosphere_v7
importlib.reload(atmosphere_v7)
request=json.loads((root/'Saved/atmosphere-ab.json').read_text())
atmosphere_v7.set_softness_enabled(request['enabled'])
camera=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
task=unreal.AutomationLibrary.take_high_res_screenshot(1443,2427,str(root/'Docs/Fidelity/Pass7'/request['filename']),camera=camera,delay=1)
assert task
unreal.log('PASS7_AB '+str(request))
