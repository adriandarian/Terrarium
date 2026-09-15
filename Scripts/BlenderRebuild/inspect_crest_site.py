"""Inspect existing crest placements and the front of the left market counter."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);scene=actors.get_all_level_actors();existing=[]
for a in scene:
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh and 'embercrest' in c.static_mesh.get_name().lower():existing.append({'actor':a.get_actor_label(),'mesh':c.static_mesh.get_path_name()})
counter=next(a for a in scene if a.get_actor_label()=='Blender_MarketStall_UpperPath').static_mesh_component
samples=[]
for x in [195,198,201]:
    for z in [596,607,618]:
        h=counter.line_trace_component(unreal.Vector(x,670,z),unreal.Vector(x,600,z),True,False,False)
        samples.append({'xz':[x,z],'y':h[0].y if h else None})
(root/'Docs/BlenderRebuild/EmberCrest/site-preflight.json').write_text(json.dumps({'existing_crests':existing,'counter_face_samples':samples},indent=2))
