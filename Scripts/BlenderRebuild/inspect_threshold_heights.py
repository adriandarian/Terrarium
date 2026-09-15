import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);all_actors=actors.get_all_level_actors();a=next(a for a in all_actors if a.get_actor_label()=='Blender_BridgeThreshold_South');t=a.get_actor_transform()
rows=[]
for y in [-39,-30,-10,0,15,30,39]:
    p=unreal.MathLibrary.transform_location(t,unreal.Vector(45,-y,0));hits=[]
    for actor in all_actors:
        for c in actor.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh or c.static_mesh.get_name() not in ['SM_Blender_BridgeThreshold','SM_Blender_TrailPatch','SM_Blender_RiverBridge']:continue
            h=c.line_trace_component(unreal.Vector(p.x,p.y,340),unreal.Vector(p.x,p.y,240),trace_complex=True,show_trace=False,persistent_show_trace=False)
            if h is not None:hits.append({'mesh':c.static_mesh.get_name(),'height':h[0].z})
    rows.append({'blender_local_y_cm':y,'world_xy_cm':[p.x,p.y],'hits':hits})
q=t.rotation
(root/'Docs/BlenderRebuild/BridgeThreshold/height-inspection.json').write_text(json.dumps({'transform':{'location':[t.translation.x,t.translation.y,t.translation.z],'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z],'rotation':[q.x,q.y,q.z,q.w]},'samples':rows},indent=2))
