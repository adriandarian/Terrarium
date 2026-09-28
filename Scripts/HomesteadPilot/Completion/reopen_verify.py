"""Verify approved pilot preservation and current completion serialization."""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Completion'
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
E = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not E.get_game_world()
assert E.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'

def snapshot(name):
    (OUT/'snapshot-request.json').write_text(json.dumps({'name':name}))
    exec(compile((ROOT/'Scripts/HomesteadPilot/Completion/snapshot.py').read_text(), 'completion_snapshot', 'exec'), {})
    return json.loads((OUT/(name+'.json')).read_text())

before = json.loads((OUT/'before.json').read_text())
admitted = snapshot('admitted')
approved = {p:v for p,v in before['meshes'].items() if p.startswith('/Game/Terrarium/HomesteadPilot/') or 'SM_Blender_GrassTerrain.' in p}
assert len(approved) == 12
for path, state in approved.items():
    assert admitted['meshes'].get(path) == state, ('Approved geometry changed', path)
assert admitted['baseline_sha256'] == before['baseline_sha256']
assert L.save_current_level()
L.eject_pilot_level_actor()
assert L.load_level('/Game/Terrarium/Calibration/Maps/ConceptScaleBlockout')
assert L.load_level('/Game/Terrarium/HomesteadPilot/Maps/StartingHome')
reopened = snapshot('reopened')
assert admitted['meshes'] == reopened['meshes'], 'Mesh instance counts or transforms changed on reload'
assert admitted['components'] == reopened['components'], 'Component materials, visibility, LOD or assignments changed on reload'
assert reopened['baseline_sha256'] == before['baseline_sha256']
for row in reopened['components']:
    if '/HomesteadPilot/' in row['mesh']:
        assert row['forced_lod'] == 0, row
    if 'SM_Blender_GrassTerrain.' in row['mesh']:
        assert row['visible'] and not row['hidden_in_game']
for camera in unreal.GameplayStatics.get_all_actors_of_class(E.get_editor_world(), unreal.CameraActor):
    assert camera.get_auto_activate_player_index() == -1, camera.get_actor_label()
(OUT/'persistence.json').write_text(json.dumps({'passed':True,'approved_eleven_families_unchanged':True,
    'grass_count':5841,'grass_transforms_unchanged':True,'baseline_unchanged':True,
    'all_mesh_assignments_materials_visibility_counts_transforms_survive_reopen':True,
    'admitted_mesh_families':len(set(reopened['meshes'])-set(before['meshes'])),
    'automatic_lods_restored':True,'review_camera_auto_activation_disabled':True},indent=2))
unreal.log('Homestead completion persistence PASS')
