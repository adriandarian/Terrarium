"""Expose the modeled bank apron just above the existing water geometry."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/Riverbank';record=json.loads((folder/'instance-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert record['world']+'.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};water=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if not c.static_mesh or c.static_mesh.get_name() not in ['SM_WaterTile_v4_Detail','SM_WaterShallow_v4_Detail','SM_WaterDeep_v4_Detail']:continue
        b=c.static_mesh.get_bounding_box()
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,world_space=True);q=t.rotation
            ang=2*math.atan2(q.z,q.w)
            water.append((t.translation,t.scale3d,math.cos(ang),math.sin(ang),b.min,b.max))
assert water
plans=[]
for row in record['static_actors']:
    a=scene[row['actor']];p=a.get_actor_location();scale=a.get_actor_scale3d().z;tops=[]
    assert a.static_mesh_component.static_mesh.get_path_name()==record['mesh']
    for pos,s,co,si,lo,hi in water:
        dx=p.x-pos.x;dy=p.y-pos.y;lx=(dx*co+dy*si)/s.x;ly=(-dx*si+dy*co)/s.y
        if lo.x<=lx<=hi.x and lo.y<=ly<=hi.y:tops.append(pos.z+hi.z*s.z)
    assert tops,('No water geometry below bank actor',row['actor'])
    top=max(tops);new_z=top+.5-9*scale
    plans.append((a,row,{'actor':row['actor'],'previous_root_z_cm':p.z,'new_root_z_cm':new_z,'water_geometry_upper_bound_cm':top,'apron_top_cm':top+.5}))
for a,row,r in plans:
    p=a.get_actor_location();p.z=r['new_root_z_cm'];a.set_actor_location(p,False,False)
    row['after']['translation'][2]=p.z
assert levels.save_current_level()
record['waterline_policy']='Static bank apron top is 0.5 cm above the local water tile geometry upper bound, keeping its bottom embedded below water.'
(folder/'instance-placement.json').write_text(json.dumps(record,indent=2))
(folder/'waterline-adjustment.json').write_text(json.dumps([r for a,row,r in plans],indent=2))
unreal.log('BLENDER_RIVERBANK_WATERLINE_SEATED')
