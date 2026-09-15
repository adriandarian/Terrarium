"""Inspect path protrusion and collect nearby native transforms for bearing checks."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);scene=actors.get_all_level_actors()
a=next(a for a in scene if a.get_actor_label()=='Blender_BridgeThreshold_South');t=a.get_actor_transform();c=a.static_mesh_component
path_components=[x for o in scene for x in o.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if x.static_mesh and x.static_mesh.get_name()=='SM_Blender_TrailPatch']
issues=[];samples=0;minimum=999
for y in list(range(-36,-12))+list(range(-12,39,3)):
    left=-80+80*(y+39)/78
    for x in range(-78,100,1 if y<-12 else 3):
        if x<left+1:continue
        p=unreal.MathLibrary.transform_location(t,unreal.Vector(x,-y,0));start=unreal.Vector(p.x,p.y,310);end=unreal.Vector(p.x,p.y,270)
        timber=c.line_trace_component(start,end,trace_complex=True,show_trace=False,persistent_show_trace=False);assert timber is not None
        ground=[]
        for pc in path_components:
            h=pc.line_trace_component(start,end,trace_complex=True,show_trace=False,persistent_show_trace=False)
            if h is not None:ground.append(h[0].z)
        if not ground:continue
        samples+=1;clearance=timber[0].z-max(ground);minimum=min(minimum,clearance)
        if clearance<.03:issues.append({'local_blender_xy_cm':[x,y],'timber_z_cm':timber[0].z,'path_z_cm':max(ground),'clearance_cm':clearance})
def serial(t):
    q=t.rotation;return {'translation':[t.translation.x,t.translation.y,t.translation.z],'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z],'rotation_xyzw':[q.x,q.y,q.z,q.w]}
nearby=[]
for actor in scene:
    for component in actor.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if not component.static_mesh or component.static_mesh.get_name()!='SM_Blender_CliffColumn':continue
        for i in range(component.get_instance_count()):
            other=component.get_instance_transform(i,world_space=True);d=other.translation-t.translation
            if d.x*d.x+d.y*d.y<400*400:nearby.append({'component':component.get_name(),'index':i,'transform':serial(other)})
bridge=next(o for o in scene if o.get_actor_label()=='Fidelity_PlankBridge_v4_001')
(root/'Docs/BlenderRebuild/BridgeThreshold/clearance-inspection.json').write_text(json.dumps({'samples_with_underlying_path':samples,'minimum_clearance_cm':minimum,'issues':issues,'threshold_transform':serial(t),'bridge_transform':serial(bridge.get_actor_transform()),'nearby_cliffs':nearby},indent=2))
unreal.log('THRESHOLD_CLEARANCE '+str(len(issues))+' issues')
