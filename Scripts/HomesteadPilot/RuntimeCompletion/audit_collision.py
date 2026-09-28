"""Read actual level collision/LOD state. Does not rebuild, save, or edit anything."""
import json
from collections import defaultdict
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/RuntimeCompletion'
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
mesh_editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assets, components = {}, []
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = comp.get_editor_property('static_mesh')
        if not mesh:
            continue
        path = mesh.get_path_name()
        if path not in assets:
            body = mesh.get_editor_property('body_setup')
            collision_lod = int(mesh.get_editor_property('lod_for_collision'))
            counts = [mesh.get_num_triangles(i) for i in range(mesh.get_num_lods())]
            assets[path] = {'mesh': path, 'triangles': counts,
                'screen_sizes': list(mesh_editor.get_lod_screen_sizes(mesh)),
                'collision_flag': str(body.get_editor_property('collision_trace_flag')) if body else None,
                'collision_lod': collision_lod,
                'collision_lod_triangles': counts[min(collision_lod, len(counts)-1)],
                'simple_collision_primitives': mesh_editor.get_simple_collision_count(mesh),
                'nanite': mesh_editor.get_nanite_settings(mesh).get_editor_property('enabled')}
        count = comp.get_instance_count() if isinstance(comp, unreal.InstancedStaticMeshComponent) else 1
        components.append({'actor': actor.get_actor_label(), 'component': comp.get_path_name(),
            'mesh': path, 'instances': count, 'collision_enabled': str(comp.get_collision_enabled()),
            'collision_profile': str(comp.get_collision_profile_name()),
            'overlaps': comp.get_editor_property('generate_overlap_events'),
            'forced_lod_model': comp.get_editor_property('forced_lod_model')})

summary = defaultdict(lambda: {'components': 0, 'instances': 0, 'triangle_instance_proxy': 0,
    'complex_as_simple_triangle_instance_proxy': 0, 'other_policy_instances': 0})
for row in components:
    entry = summary[row['collision_enabled']]
    entry['components'] += 1
    entry['instances'] += row['instances']
    entry['triangle_instance_proxy'] += row['instances'] * assets[row['mesh']]['collision_lod_triangles']
    if 'CTF_USE_COMPLEX_AS_SIMPLE' in (assets[row['mesh']]['collision_flag'] or ''):
        entry['complex_as_simple_triangle_instance_proxy'] += row['instances'] * assets[row['mesh']]['collision_lod_triangles']
    else:
        entry['other_policy_instances'] += row['instances']
pilot = [r for r in components if '/HomesteadPilot/' in r['mesh']]
data = {'world': world.get_path_name(), 'meshes': list(assets.values()), 'components': components,
    'summary_by_collision_enabled': dict(summary),
    'pilot_forced_lod_zero': all(r['forced_lod_model'] == 0 for r in pilot),
    'scope': 'Read-only technical inventory of actual editor objects; no mesh-plan/configure-only filter used.',
    'limits': 'Triangle-instance proxy is visual geometry exposure, not memory or measured physics cost. The complex-as-simple subtotal isolates known per-triangle simple collision policy; CTF_USE_DEFAULT visual triangles do not establish simple collision cost. Instanced meshes share geometry; this is not cooked-data size. Collision LOD is independent of visual LOD. Automatic rendered LOD and smoothness require visual review.'}
(OUT / 'collision-inventory.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
unreal.log('RuntimeCompletion collision inventory written; no assets changed.')
