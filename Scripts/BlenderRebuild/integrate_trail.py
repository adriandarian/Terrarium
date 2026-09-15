"""Replace all path placements with Blender pavers and ground their soil volumes."""
import unreal,json,shutil
from collections import Counter
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/TrailPatch';receipt=folder/'instance-placement.json';assert not receipt.exists()
before_path=root/'Saved/blender-foliage-TrailTerrain.json';before=json.loads(before_path.read_text())
ground=json.loads((folder/'ground-before.json').read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==before['world']==ground['world'] and '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
oldmesh=unreal.load_asset(before['components'][0]['mesh']);mesh=unreal.load_asset('/Game/Terrarium/Blender/TrailPatch/SM_Blender_TrailPatch');assert mesh
assert mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')==unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def code(row):return json.dumps({k:[round(v,3) for v in values] for k,values in row.items()},sort_keys=True)
def transform(row):
    t=unreal.Transform();t.translation=unreal.Vector(*row['translation']);t.scale3d=unreal.Vector(*row['scale']);t.rotation=unreal.Quat(*row['rotation_xyzw']);return t
def instances(m):return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==m for i in range(c.get_instance_count())]
original=instances(oldmesh);assert len(original)==61 and not instances(mesh)
assert Counter(code(serial(t)) for t in original)==Counter(code(t) for c in before['components'] for t in c['transforms'])
lookup={code(r['before']):r for r in ground['placements']};assert len(lookup)==84
def fit(t):
    initial=serial(t);row=lookup[code(initial)];assert abs(t.rotation.x)<1e-5 and abs(t.rotation.y)<1e-5
    lo,hi=row['ground_range_cm'];s=t.scale3d
    # Topsoil clears the highest sampled support by 3 mm. Ensure the closed
    # base also penetrates the lowest sampled support by at least 3 mm.
    s.z=max(s.z,(hi-lo+.6)/13.8);t.scale3d=s
    p=t.translation;p.z=hi+.3+.2*s.z;t.translation=p
    return {'before':initial,'after':serial(t),'placement':row['placement'],'ground_range_cm':[lo,hi],'missing_ground_samples':row['missing_sample_count']}
planned={code(serial(t)):fit(transform(serial(t))) for t in original}
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};statics=[]
for row in before['static_actors']:
    a=scene[row['actor']];assert a.static_mesh_component.static_mesh==oldmesh and code(serial(a.get_actor_transform()))==code(row['transform'])
    statics.append({'actor':row['actor'],**fit(a.get_actor_transform())})
assert len(statics)==23
shutil.copyfile(before_path,folder/'before-placement.json')
groups=[];removed_groups=[];unused=[]
try:
    for index,entry in enumerate(before['foliage_types']):
        oldft=unreal.load_asset(entry['path']);assert oldft.get_editor_property('mesh')==oldmesh
        pending=instances(oldmesh)
        unreal.InstancedFoliageActor.remove_all_instances(world,oldft)
        remain=Counter(code(serial(t)) for t in instances(oldmesh));removed=[]
        for t in pending:
            k=code(serial(t))
            if remain[k]:remain[k]-=1
            else:removed.append(t)
        if not removed:unused.append(oldft.get_path_name());continue
        removed_groups.append((oldft,removed))
        dest='/Game/Terrarium/Blender/TrailPatch/FT_Blender_TrailPatch_'+str(index+1)
        assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
        ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest);assert ft
        ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[])
        body=ft.get_editor_property('body_instance');body.set_editor_property('collision_profile_name','BlockAll');body.set_editor_property('collision_enabled',unreal.CollisionEnabled.QUERY_AND_PHYSICS);ft.set_editor_property('body_instance',body)
        assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
        changes=[planned[code(serial(t))] for t in removed]
        groups.append({'old_foliage_type':oldft.get_path_name(),'new_foliage_type':ft.get_path_name(),'count':len(changes),'instances':changes})
        unreal.InstancedFoliageActor.add_instances(world,ft,[transform(r['after']) for r in changes])
    assert not instances(oldmesh) and len(instances(mesh))==61
    assert Counter(code(serial(t)) for t in instances(mesh))==Counter(code(r['after']) for r in planned.values())
    for row in statics:
        a=scene[row['actor']];a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_editor_property('override_materials',[])
        a.static_mesh_component.set_collision_profile_name('BlockAll');a.set_actor_transform(transform(row['after']),False,False)
    assert levels.save_current_level()
except Exception:
    for group in groups:unreal.InstancedFoliageActor.remove_all_instances(world,unreal.load_asset(group['new_foliage_type']))
    for oldft,transforms in removed_groups:unreal.InstancedFoliageActor.add_instances(world,oldft,transforms)
    for row in statics:
        a=scene[row['actor']];a.static_mesh_component.set_static_mesh(oldmesh);a.set_actor_transform(transform(row['before']),False,False)
    levels.save_current_level();raise
receipt.write_text(json.dumps({'asset':'TrailPatch','world':world.get_path_name().split('.')[0],'old_mesh':oldmesh.get_path_name(),'mesh':mesh.get_path_name(),'count':61,'static_count':23,'groups':groups,'unused_original_foliage_types':unused,'static_actors':statics,'placement_policy':'Preserve XY, yaw and XY scale. Ground soil top 0.3 cm above the highest of nine terrain samples; deepen Z scale only when needed to embed the base through a terrain step. Two previously unsupported edge samples remain explicitly recorded.','status':'saved_pending_reload_collision_and_visual_review'},indent=2))
unreal.log('BLENDER_TRAIL_MIGRATED 61 foliage + 23 actors')
