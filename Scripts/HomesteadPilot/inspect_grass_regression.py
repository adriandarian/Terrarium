"""Read grass terrain state without changing the scene."""
import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=E.get_editor_world();assert 'StartingHome' in world.get_path_name()
rows=[]
for a in A.get_all_level_actors():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  m=c.static_mesh
  if m and ('GrassTerrain' in m.get_path_name() or 'MeadowTile' in m.get_path_name()):
   props={}
   for k in ('visible','hidden_in_game','forced_lod_model','min_draw_distance','ld_max_draw_distance','cached_max_draw_distance','instance_start_cull_distance','instance_end_cull_distance','render_in_main_pass'):
    try:props[k]=str(c.get_editor_property(k))
    except Exception:pass
   rows.append({'actor':a.get_actor_label(),'component':c.get_path_name(),'mesh':m.get_path_name(),'count':c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1,'actor_hidden':str(a.get_editor_property('hidden')),'temporarily_hidden':a.is_temporarily_hidden_in_editor(),'properties':props,'materials':[str(c.get_material(i)) for i in range(c.get_num_materials())]})
(R/'Docs/HomesteadPilot/grass-regression-inspection.json').write_text(json.dumps({'world':world.get_path_name(),'PIE':bool(E.get_game_world()),'grass_components':rows},indent=2))
