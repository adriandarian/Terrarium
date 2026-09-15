"""Check identified edge contacts and sample the visible south bridge joint densely."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
names=['SM_Blender_GrassTerrain','SM_Blender_CliffColumn','SM_Blender_TrailPatch','SM_Blender_RiverBridge','SM_Blender_StoneStairs','SM_Blender_BridgeThreshold']
components=[c for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and c.static_mesh.get_name() in names]
def hits(x,y,top,bottom,exclude_trail=False):
    results=[]
    for c in components:
        if exclude_trail and c.static_mesh.get_name() in ['SM_Blender_TrailPatch','SM_Blender_BridgeThreshold']:continue
        hit=c.line_trace_component(unreal.Vector(x,y,top),unreal.Vector(x,y,bottom),trace_complex=True,show_trace=False,persistent_show_trace=False)
        if hit is not None:results.append({'mesh':c.static_mesh.get_name(),'component':c.get_name(),'height_cm':hit[0].z})
    return sorted(results,key=lambda p:p['height_cm'],reverse=True)
ground=json.loads((root/'Docs/BlenderRebuild/TrailPatch/ground-before.json').read_text());edges=[]
for row in ground['placements']:
    for sample in row['samples']:
        if sample['ground'] is not None:continue
        x,y=sample['world_xy_cm'];z=row['before']['translation'][2]
        edges.append({'placement':row['placement'],'world_xy_cm':[x,y],'underlying_support':hits(x,y,z+25,z-80,True),'with_path':hits(x,y,z+25,z-80)})
r=json.loads((root/'Docs/BlenderRebuild/RiverBridge/world-placement.json').read_text());p=r['location_cm'];angle=math.radians(r['yaw']);samples=[]
for across in [-60,0,60]:
    for along in range(-420,-319,5):
        x=p[0]+across*math.cos(angle)-along*math.sin(angle);y=p[1]+across*math.sin(angle)+along*math.cos(angle)
        found=hits(x,y,350,240)
        samples.append({'across_cm':across,'along_cm':along,'xy_cm':[x,y],'top_surface':found[0] if found else None})
(root/'Docs/BlenderRebuild/TrailPatch/connection-review.json').write_text(json.dumps({'edge_contacts':edges,'bridge_south_joint':samples,'scope':'Component collision sampled every 5 cm along three lines across the south joint. No character traversal test.'},indent=2))
unreal.log('TRAIL_CONNECTIONS_INSPECTED')
