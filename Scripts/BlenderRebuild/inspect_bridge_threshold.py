"""Read bridge, path and bank surfaces to size a source-style timber threshold."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);scene=actors.get_all_level_actors()
r=json.loads((root/'Docs/BlenderRebuild/RiverBridge/world-placement.json').read_text())
bridge=next(a for a in scene if a.get_actor_label()==r['actor']);assert bridge.static_mesh_component.static_mesh.get_path_name()==r['mesh']
p=bridge.get_actor_location();rot=bridge.get_actor_rotation();assert abs(rot.yaw-r['yaw'])<.001
angle=math.radians(rot.yaw)
components=[c for a in scene for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and c.static_mesh.get_name() in ['SM_Blender_GrassTerrain','SM_Blender_CliffColumn','SM_Blender_TrailPatch','SM_Blender_RiverBridge']]
rows=[]
for along in [-450,-430,-410,-395,-380,-365,-350,-335,-320]:
    samples=[]
    for across in range(-130,151,10):
        x=p.x+across*math.cos(angle)-along*math.sin(angle);y=p.y+across*math.sin(angle)+along*math.cos(angle);hits=[]
        for c in components:
            h=c.line_trace_component(unreal.Vector(x,y,310),unreal.Vector(x,y,240),trace_complex=True,show_trace=False,persistent_show_trace=False)
            if h is not None:hits.append({'mesh':c.static_mesh.get_name(),'z_cm':h[0].z})
        samples.append({'across_cm':across,'hits':hits})
    rows.append({'along_cm':along,'samples':samples})
folder=root/'Docs/BlenderRebuild/BridgeThreshold';folder.mkdir(exist_ok=True)
(folder/'site-before.json').write_text(json.dumps({'world':world.get_path_name(),'bridge_actor':bridge.get_actor_label(),'bridge_mesh':bridge.static_mesh_component.static_mesh.get_path_name(),'bridge_location_cm':[p.x,p.y,p.z],'bridge_yaw':rot.yaw,'bridge_scale':[bridge.get_actor_scale3d().x,bridge.get_actor_scale3d().y,bridge.get_actor_scale3d().z],'samples':rows,'purpose':'Fit a timber threshold using the existing bridge language; canonical river_crossing geometry remains separate.'},indent=2))
unreal.log('BRIDGE_THRESHOLD_SITE_INSPECTED')
