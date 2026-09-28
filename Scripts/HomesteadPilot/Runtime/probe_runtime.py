"""Read-only runtime API probe; execute in the verified Terrarium editor."""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'
OUT.mkdir(parents=True, exist_ok=True)
types = ['ArchVisCharacter', 'ArchVisCharMovementComponent', 'StaticMeshEditorSubsystem',
         'StaticMeshReductionSettings', 'StaticMeshReductionOptions', 'StaticMesh',
         'InputSettings', 'InputAxisKeyMapping', 'Key', 'EditorLevelLibrary',
         'UnrealEditorSubsystem', 'LevelEditorSubsystem', 'GameplayStatics',
         'CollisionTraceFlag', 'BodySetup', 'PlayerController', 'GameModeBase']
result = {'project': str(ROOT), 'types': {}, 'class': None}
for name in types:
    cls = getattr(unreal, name, None)
    result['types'][name] = {'exists': cls is not None}
    if cls:
        result['types'][name]['members'] = [x for x in dir(cls) if not x.startswith('_')]
        result['types'][name]['doc'] = cls.__doc__
result['class'] = str(unreal.load_class(None, '/Script/ArchVisCharacter.ArchVisCharacter'))
result['selected_docs'] = {}
for typ, names in {
    'StaticMeshEditorSubsystem': ['set_lods', 'set_lod_screen_sizes', 'get_nanite_settings', 'set_nanite_settings', 'remove_collisions'],
    'LevelEditorSubsystem': ['editor_request_begin_play', 'editor_request_end_play'],
    'InputSettings': ['add_axis_mapping', 'save_key_mappings', 'force_rebuild_keymaps'],
    'InputAxisKeyMapping': ['__init__'],
    'GameplayStatics': ['get_world_delta_seconds', 'get_player_character'],
}.items():
    for name in names:
        result['selected_docs'][typ + '.' + name] = getattr(getattr(unreal, typ), name, None).__doc__
(OUT / 'api-probe.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
unreal.log('Homestead runtime API probe saved.')
