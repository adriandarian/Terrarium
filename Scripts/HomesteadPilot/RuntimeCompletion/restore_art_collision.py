"""Coordinator-only: restore inherited collision on private RemainingArt copies.

The import applied a family-based policy that was not the inherited scene policy.
Use the pre-integration snapshot for component settings and actual unchanged source
meshes for BodySetup flags. This does not simplify collision or edit baseline assets.
"""
import hashlib
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/RuntimeCompletion'
before = json.loads((ROOT / 'Docs/HomesteadPilot/Completion/collision-before.json').read_text())
baseline_components = {r['component']: r for r in before['components']}
baseline_meshes = {r['mesh']: r for r in before['meshes']}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world(), 'End PIE before restoring collision'
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

def asset_hash(mesh):
    relative = mesh.get_path_name().split('.')[0].removeprefix('/Game/')
    return hashlib.sha256((ROOT / 'Content' / (relative + '.uasset')).read_bytes()).hexdigest()

def component_state(comp):
    return {'collision_profile': str(comp.get_collision_profile_name()),
        'collision_enabled': str(comp.get_collision_enabled()),
        'overlaps': comp.get_editor_property('generate_overlap_events')}

targets = []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = comp.get_editor_property('static_mesh')
        if mesh and mesh.get_path_name().startswith('/Game/Terrarium/HomesteadPilot/RemainingArt/Meshes/'):
            previous = baseline_components[comp.get_path_name()]
            source = unreal.load_asset(previous['mesh'])
            assert source and source != mesh
            original = baseline_meshes[previous['mesh']]
            source_body = source.get_editor_property('body_setup')
            assert str(source_body.get_editor_property('collision_trace_flag')) == original['collision_flag']
            assert source.get_editor_property('lod_for_collision') == original['collision_lod']
            assert original['simple_collision_primitives'] == sub.get_simple_collision_count(source) == sub.get_simple_collision_count(mesh) == 0, 'Nonzero simple shapes need a separate exact-copy repair'
            assert previous['collision_profile'] == 'BlockAll'
            assert previous['collision_enabled'] == str(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            targets.append((actor, comp, mesh, source, previous))
assert len(targets) == 17, 'Expected all 17 admitted art components before repair'

rows = []
for actor, comp, mesh, source, previous in targets:
    before_state = component_state(comp)
    source_hash = asset_hash(source)
    body = mesh.get_editor_property('body_setup')
    source_body = source.get_editor_property('body_setup')
    prior_body = {k: str(body.get_editor_property(k)) for k in ['collision_trace_flag', 'double_sided_geometry']}
    modified_mesh = False
    for prop in ['collision_trace_flag', 'double_sided_geometry']:
        value = source_body.get_editor_property(prop)
        if body.get_editor_property(prop) != value:
            body.modify()
            mesh.modify()
            body.set_editor_property(prop, value)
            modified_mesh = True
    if mesh.get_editor_property('lod_for_collision') != source.get_editor_property('lod_for_collision'):
        mesh.set_editor_property('lod_for_collision', source.get_editor_property('lod_for_collision'))
        modified_mesh = True
    expected_state = {key: previous[key] for key in before_state}
    if before_state != expected_state:
        comp.modify()
        comp.set_collision_profile_name(previous['collision_profile'])
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        comp.set_editor_property('generate_overlap_events', previous['overlaps'])
    assert component_state(comp) == expected_state
    assert body.get_editor_property('collision_trace_flag') == source_body.get_editor_property('collision_trace_flag')
    assert body.get_editor_property('double_sided_geometry') == source_body.get_editor_property('double_sided_geometry')
    assert sub.get_simple_collision_count(mesh) == 0
    assert comp.get_editor_property('forced_lod_model') == 0
    if modified_mesh:
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    assert asset_hash(source) == source_hash, 'Source package unexpectedly changed'
    rows.append({'actor': actor.get_actor_label(), 'component': comp.get_path_name(),
        'mesh': mesh.get_path_name(), 'source': source.get_path_name(), 'source_sha256': source_hash,
        'source_disk_unchanged': True, 'mesh_saved': modified_mesh,
        'body_before': prior_body,
        'body_after': {k: str(body.get_editor_property(k)) for k in prior_body},
        'collision_lod': mesh.get_editor_property('lod_for_collision'),
        'simple_collision_primitives': sub.get_simple_collision_count(mesh),
        'component_before': before_state, 'component_after': component_state(comp),
        'matches_inherited_policy': True})
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(OUT / 'art-collision-restoration.json').write_text(json.dumps({'restored_components': len(rows),
    'all_match_inherited': True, 'rows': rows,
    'scope': 'Restores source BodySetup flags/collision LOD and pre-integration component profiles/enabled/overlap flags on private art copies. All original and target simple collision counts are zero. No simplification, baseline save or visual LOD changes.'}, indent=2), encoding='utf-8')
unreal.log('RuntimeCompletion restored inherited collision for 17 private art placements.')
