"""Read terrain contact beneath every existing path placement before replacing it."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Terrarium/Blender/Maps/HomesteadBlender.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
terrain=[];placements=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if not c.static_mesh:continue
        if c.static_mesh.get_name() in ['SM_Blender_GrassTerrain','SM_Blender_CliffColumn']:terrain.append(c)
        if c.static_mesh.get_name()!='SM_PathTile_v4_Detail':continue
        if isinstance(c,unreal.FoliageInstancedStaticMeshComponent):
            placements.extend((c.get_name()+':'+str(i),c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count()))
        elif isinstance(a,unreal.StaticMeshActor):placements.append((a.get_actor_label(),a.get_actor_transform()))
assert len(placements)==84 and len(terrain)>=5
def vec(p):return [p.x,p.y,p.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
samples=[(0,0),(-80,-50),(-80,50),(80,-50),(80,50),(-30,-75),(-30,75),(40,-75),(40,75)]
rows=[]
for label,t in placements:
    checks=[]
    for x,y in samples:
        p=unreal.MathLibrary.transform_location(t,unreal.Vector(x,y,0));hits=[]
        for c in terrain:
            hit=c.line_trace_component(unreal.Vector(p.x,p.y,p.z+25),unreal.Vector(p.x,p.y,p.z-80),trace_complex=True,show_trace=False,persistent_show_trace=False)
            if hit is not None:hits.append({'height_cm':hit[0].z,'component':c.get_name(),'mesh':c.static_mesh.get_name()})
        checks.append({'local_xy_cm':[x,y],'world_xy_cm':[p.x,p.y],'ground':max(hits,key=lambda h:h['height_cm']) if hits else None})
    heights=[p['ground']['height_cm'] for p in checks if p['ground']]
    rows.append({'placement':label,'before':serial(t),'samples':checks,'missing_sample_count':sum(p['ground'] is None for p in checks),'ground_range_cm':[min(heights),max(heights)] if heights else None})
report={'world':world.get_path_name(),'count':len(rows),'sample_count':len(samples),'method':'Complex component traces restricted to Blender grass and cliff meshes; checks underlying support, excludes props and old paths.','placements':rows}
(root/'Docs/BlenderRebuild/TrailPatch/ground-before.json').write_text(json.dumps(report,indent=2))
unreal.log('TRAIL_GROUND_INSPECTED '+str(len(rows)))
