"""Read counter support and nearby props before seating the Grove model."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world='/Game/Terrarium/Blender/Maps/HomesteadBlender'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
if world+'.' not in str(levels.get_current_level()):assert levels.load_level(world)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
counter=scene['Blender_MarketStall_UpperPath'].static_mesh_component
samples=[]
for x in [241.4,307,345,365,375,385]:
    for y in [616,620,623,626]:
        hit=counter.line_trace_component(unreal.Vector(x,y,670),unreal.Vector(x,y,630),True,False,False)
        samples.append({'xy':[x,y],'z':hit[0].z if hit else None})
p=scene['Blender_MarketStall_UpperPath'].get_actor_location()
(root/'Docs/BlenderRebuild/Grove/counter-probes.json').write_text(json.dumps({'stall_position':[p.x,p.y,p.z],'samples':samples},indent=2))
