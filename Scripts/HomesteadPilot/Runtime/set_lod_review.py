"""Select actual LOD on pilot-only components for a fixed-camera visual comparison.

Set runtime-config lod_review_forced to 0 (automatic), 1 (LOD0), 2 (LOD1), 3 (LOD2).
Never save the level while forced. Run with 0 before final save/reopen verification.
"""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'
config = json.loads((OUT / 'runtime-config.json').read_text())
forced = int(config['lod_review_forced'])
assert forced in range(4)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
rows = []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if config.get('lod_review_actor_labels') and actor.get_actor_label() not in config['lod_review_actor_labels']:
        continue
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = comp.get_editor_property('static_mesh')
        if not mesh or not mesh.get_path_name().startswith('/Game/Terrarium/HomesteadPilot/'):
            continue
        if mesh.get_num_lods() < 3:
            continue
        comp.set_forced_lod_model(forced)
        assert comp.get_editor_property('forced_lod_model') == forced
        rows.append({'actor': actor.get_actor_label(), 'component': comp.get_path_name(),
                     'mesh': mesh.get_path_name(), 'forced_lod_model': forced})
assert rows, 'No matching 3-LOD pilot component in this level'
(OUT / ('lod-review-forced-' + str(forced) + '.json')).write_text(json.dumps(rows, indent=2), encoding='utf-8')
unreal.log('Pilot forced LOD ' + str(forced) + '; capture fixed camera, then restore 0 before save.')
