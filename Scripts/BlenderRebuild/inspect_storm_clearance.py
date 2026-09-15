"""Measure the post face behind Storm, not just the plank below its tip."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
scene={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
c=scene['Blender_MarketStall_UpperPath'].static_mesh_component;rows=[]
for x in [389,393,397,401,405]:
    for z in [638,643,648,651]:
        hit=c.line_trace_component(unreal.Vector(x,660,z),unreal.Vector(x,590,z),True,False,False)
        rows.append({'xz':[x,z],'front_y':hit[0].y if hit else None})
(root/'Docs/BlenderRebuild/Storm/post-clearance-preflight.json').write_text(json.dumps(rows,indent=2))
