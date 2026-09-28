"""Region-only broad tree trunk capsule, preserving source tree and render LODs.

Coordinator executes with ValleyRegion open and PIE stopped. Recreates only the
new region forest instances via its existing private FoliageTypes. Run forest
contact queries and actual pawn collision checks after this native rebuild.
"""
import hashlib
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/WorldExpansion'
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
source = unreal.load_asset('/Game/Terrarium/HomesteadPilot/Landscape/Meshes/SM_BroadTree5m')
assert isinstance(source, unreal.StaticMesh)
source_file = ROOT / 'Content/Terrarium/HomesteadPilot/Landscape/Meshes/SM_BroadTree5m.uasset'
source_hash = hashlib.sha256(source_file.read_bytes()).hexdigest()
source_lods = [source.get_num_triangles(i) for i in range(source.get_num_lods())]
source_materials = [str(slot.material_interface) for slot in source.static_materials]
source_flag = source.get_editor_property('body_setup').get_editor_property('collision_trace_flag')
source_simple_count = sub.get_simple_collision_count(source)
assert len(source_lods) == 3
destination = '/Game/Terrarium/WorldExpansion/Forest/SM_WX_BroadTree5m'
mesh = unreal.load_asset(destination) or unreal.EditorAssetLibrary.duplicate_asset(source.get_path_name().split('.')[0], destination)
assert isinstance(mesh, unreal.StaticMesh) and mesh != source
mesh.modify()
body = mesh.get_editor_property('body_setup')
assert body and body != source.get_editor_property('body_setup')
body.modify()
# Clear any imported aggregate through the editor subsystem before authoring the
# precise trunk shape; this never changes the source mesh's collision policy.
sub.remove_collisions(mesh)
capsule = unreal.KSphylElem()
capsule.set_editor_property('center', unreal.Vector(0, 0, 130))
capsule.set_editor_property('rotation', unreal.Rotator(pitch=0, yaw=0, roll=0))
capsule.set_editor_property('radius', 30.0)
capsule.set_editor_property('length', 200.0)
capsule.set_editor_property('collision_enabled', unreal.CollisionEnabled.QUERY_AND_PHYSICS)
capsule.set_editor_property('name', 'TerrariumTrunk')
capsule.set_editor_property('is_generated', True)
aggregate = unreal.KAggregateGeom()
aggregate.set_editor_property('sphyl_elems', [capsule])
body.set_editor_property('agg_geom', aggregate)
body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX)
body.set_editor_property('double_sided_geometry', source.get_editor_property('body_setup').get_editor_property('double_sided_geometry'))
mesh.set_editor_property('lod_for_collision', 2)
# Native editor rebuild with identical visual settings. Query validation after
# component recreation is the physical acceptance criterion, not this setter.
settings = sub.get_lod_build_settings(mesh, 0)
sub.set_lod_build_settings(mesh, 0, settings)
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
body = mesh.get_editor_property('body_setup')
aggregate = body.get_editor_property('agg_geom')
assert len(aggregate.get_editor_property('sphyl_elems')) == 1
assert sub.get_simple_collision_count(mesh) == 1
assert body.get_editor_property('collision_trace_flag') == unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX
assert [mesh.get_num_triangles(i) for i in range(mesh.get_num_lods())] == source_lods
assert [str(slot.material_interface) for slot in mesh.static_materials] == source_materials
assert hashlib.sha256(source_file.read_bytes()).hexdigest() == source_hash
assert source.get_editor_property('body_setup').get_editor_property('collision_trace_flag') == source_flag
assert sub.get_simple_collision_count(source) == source_simple_count

# This existing manifest-driven importer removes/re-adds the region's two private
# FoliageTypes, preserving homestead/settlement trees and every source asset.
exec(compile((ROOT / 'Scripts/WorldExpansion/integrate_forest.py').read_text(encoding='utf-8'),
             'world_expansion_recreate_private_forest', 'exec'), {})
private_ft = unreal.load_asset('/Game/Terrarium/WorldExpansion/Forest/FT_WX_BroadTree5m')
assert private_ft.get_editor_property('mesh') == mesh
report = {'private_mesh': mesh.get_path_name(), 'source_mesh': source.get_path_name(),
    'source_sha256': source_hash, 'source_disk_unchanged': hashlib.sha256(source_file.read_bytes()).hexdigest() == source_hash,
    'actual_visual_lod_triangles': source_lods, 'visual_lods_and_materials_preserved': True,
    'simple_collision_primitives': sub.get_simple_collision_count(mesh),
    'capsule_center_cm': [0, 0, 130], 'capsule_radius_cm': 30, 'capsule_cylinder_length_cm': 200,
    'capsule_total_height_cm': 260, 'trace_policy': str(body.get_editor_property('collision_trace_flag')),
    'complex_collision_lod': 2, 'private_foliage_type': private_ft.get_path_name(),
    'rebuild': 'Native StaticMeshEditorSubsystem identical LOD0 build-settings round-trip; region private forest instances recreated.',
    'limits': 'Native shape/property/source preservation evidence. Run forest simple traces and pawn collision checks; this receipt alone does not assert cooked collision success.'}
(OUT / 'forest-collision.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('WorldExpansion private trunk capsule applied; run forest contact validation.')
