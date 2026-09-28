"""Capture admission/persistence evidence without changing scene assets."""
import collections
import hashlib
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Completion'
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not editor.get_game_world()
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] == '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
rows = []
mesh_transforms = collections.defaultdict(list)
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = comp.static_mesh
        if not mesh:
            continue
        transforms = [comp.get_instance_transform(i, world_space=True) for i in range(comp.get_instance_count())] if isinstance(comp, unreal.InstancedStaticMeshComponent) else [comp.get_world_transform()]
        values = []
        for t in transforms:
            p, s, q = t.translation, t.scale3d, t.rotation
            values.append([round(v, 5) for v in (p.x,p.y,p.z,s.x,s.y,s.z,q.x,q.y,q.z,q.w)])
        path = mesh.get_path_name()
        mesh_transforms[path].extend(values)
        rows.append({'actor':actor.get_actor_label(), 'mesh':path, 'instances':len(values),
                     'visible':bool(comp.get_editor_property('visible')), 'hidden_in_game':bool(comp.get_editor_property('hidden_in_game')),
                     'forced_lod':comp.get_editor_property('forced_lod_model'),
                     'materials':[comp.get_material(i).get_path_name() if comp.get_material(i) else None for i in range(comp.get_num_materials())]})
summary = {path:{'instances':len(ts), 'transform_sha256':hashlib.sha256(json.dumps(sorted(ts)).encode()).hexdigest()} for path,ts in mesh_transforms.items()}
rows.sort(key=lambda row:(row['actor'],row['mesh']))
result = {'world':world.get_path_name(),'meshes':summary,'components':rows,
          'baseline_sha256':hashlib.sha256((ROOT/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap').read_bytes()).hexdigest(),
          'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
          'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]}
request = OUT/'snapshot-request.json'
name = json.loads(request.read_text())['name'] if request.exists() else 'before'
(OUT/(name+'.json')).write_text(json.dumps(result,indent=2))
unreal.log('Homestead completion snapshot: '+name)
