"""Seat tree roots into the verified meadow surface without moving their XY layout."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
key='HomesteadTree';folder=root/'Docs/BlenderRebuild'/key;receipt=folder/'instance-placement.json';record=json.loads(receipt.read_text())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert record['world']+'.' in str(levels.get_current_level())
mesh=unreal.load_asset(record['mesh']);base=mesh.get_bounding_box().min.z;ground=[];components=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if c.static_mesh==mesh:components.append(c)
        if c.static_mesh and c.static_mesh.get_name() in ['SM_Env_MeadowTile','SM_Blender_GrassTerrain']:
            b=c.static_mesh.get_bounding_box();assert abs(b.max.z)<.02
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,world_space=True);q=t.rotation
                assert abs(q.x)+abs(q.y)<.001
                yaw=2*math.atan2(q.z,q.w)
                ground.append((t.translation,t.scale3d,math.cos(yaw),math.sin(yaw),b.min,b.max))
assert ground and components
plans=[]
for c in components:
    for i in range(c.get_instance_count()):
        t=c.get_instance_transform(i,world_space=True);p=t.translation;candidates=[]
        for g,s,co,si,lo,hi in ground:
            if abs(g.z-p.z)>15:continue
            dx=p.x-g.x;dy=p.y-g.y;lx=(dx*co+dy*si)/s.x;ly=(-dx*si+dy*co)/s.y
            if lo.x<=lx<=hi.x and lo.y<=ly<=hi.y:candidates.append(g.z+hi.z*s.z)
        assert candidates,('No verified meadow below tree',i,str(p))
        top=max(candidates);new_z=top-1.1-base*t.scale3d.z
        row=next(r for r in record['instances'] if abs(r['after']['translation'][0]-p.x)<.01 and abs(r['after']['translation'][1]-p.y)<.01)
        plans.append((c,i,t,row,top,new_z))
assert len(plans)==record['count']
report=[]
for c,i,t,row,top,new_z in plans:
    p=t.translation;previous=p.z;p.z=new_z;t.translation=p
    assert c.update_instance_transform(i,t,world_space=True,mark_render_state_dirty=True,teleport=True)
    row['after']['translation'][2]=new_z
    report.append({'xy_cm':[p.x,p.y],'previous_root_z_cm':previous,'new_root_z_cm':new_z,'nominal_meadow_top_cm':top,'root_base_below_nominal_top_cm':1.1})
assert levels.save_current_level()
record['root_policy']='Root bottoms sit 1.1 cm below nominal meadow top, covering its measured 0 to 1.05 cm shallow depressions.'
receipt.write_text(json.dumps(record,indent=2));(folder/'root-grounding.json').write_text(json.dumps(report,indent=2))
