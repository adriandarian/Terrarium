"""Read existing prism placements and candidate counter support."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
scene=actors.get_all_level_actors();rows=[]
for a in scene:
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh and 'prism' in (a.get_actor_label()+c.static_mesh.get_name()).lower():rows.append({'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'transform':str(a.get_actor_transform())})
counter=next(a for a in scene if a.get_actor_label()=='Blender_MarketStall_UpperPath').static_mesh_component
probes=[]
for x in [303,307,311,315]:
    for y in [620,623,625]:
        hit=counter.line_trace_component(unreal.Vector(x,y,670),unreal.Vector(x,y,630),True,False,False)
        probes.append({'xy':[x,y],'z':hit[0].z if hit else None})
(root/'Docs/BlenderRebuild/TrailPrism/site-preflight.json').write_text(json.dumps({'level':str(levels.get_current_level()),'existing_prisms':rows,'counter_samples':probes},indent=2))
