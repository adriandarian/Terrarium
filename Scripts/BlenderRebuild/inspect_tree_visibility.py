import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
ft=unreal.load_asset('/Game/Terrarium/Blender/HomesteadTree/FT_Blender_HomesteadTree')
mesh=ft.get_editor_property('mesh');report={'foliage':{},'components':[],'bounds':str(mesh.get_bounds())}
for name in ['cull_distance','enable_cull_distance_scaling','enable_density_scaling','density','scale_x','scale_y','scale_z']:
    try:report['foliage'][name]=str(ft.get_editor_property(name))
    except Exception as e:report['foliage'][name]=str(e)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh!=mesh:continue
        row={'component':c.get_path_name(),'count':c.get_instance_count(),'instances':[str(c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count())]}
        for name in ['visible','hidden_in_game','instance_start_cull_distance','instance_end_cull_distance','bounds_scale','min_draw_distance','cached_max_draw_distance']:
            try:row[name]=str(c.get_editor_property(name))
            except Exception as e:row[name]=str(e)
        report['components'].append(row)
(root/'Saved/blender-tree-visibility.json').write_text(json.dumps(report,indent=2))
