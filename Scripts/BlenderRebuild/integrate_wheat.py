"""Replace the forty inspected crop patches, grounding every authored stalk on the terrace."""
import unreal, json, math, shutil, hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve()
assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/WheatPatch'
receipt=folder/'instance-placement.json'
assert not receipt.exists(), 'Already migrated; inspect the saved placement before refining'
before_path=root/'Saved/blender-foliage-WheatField.json'
before=json.loads(before_path.read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==before['world'] and '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert len(before['foliage_types'])==1 and not before['static_actors']
oldft=unreal.load_asset(before['foliage_types'][0]['path'])
oldmesh=oldft.get_editor_property('mesh')
mesh=unreal.load_asset('/Game/Terrarium/Blender/WheatPatch/SM_Blender_WheatPatch')
assert mesh
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation
    return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def instances(m):
    return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==m for i in range(c.get_instance_count())]
jobs=instances(oldmesh)
assert len(jobs)==40 and not instances(mesh)
assert [serial(t) for t in jobs]==[t for c in before['components'] for t in c['transforms']]
roots_path=folder/'stalk-roots.json'
roots=json.loads(roots_path.read_text())['roots_xy_m']
assert len(roots)==56
ground=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if not c.static_mesh or c.static_mesh.get_name()!='SM_Env_MeadowTile':continue
        b=c.static_mesh.get_bounding_box()
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,world_space=True)
            p=t.translation
            if not (-1900<p.x<-880 and -450<p.y<1200):continue
            q=t.rotation;ang=2*math.atan2(q.z,q.w)
            ground.append((p,t.scale3d,math.cos(ang),math.sin(ang),b.min,b.max))
assert ground
def terrain_at(x,y):
    tops=[]
    for p,s,co,si,lo,hi in ground:
        dx=x-p.x;dy=y-p.y
        if abs(dx)>80 or abs(dy)>80:continue
        lx=(dx*co+dy*si)/s.x;ly=(-dx*si+dy*co)/s.y
        if lo.x<=lx<=hi.x and lo.y<=ly<=hi.y:tops.append(p.z+hi.z*s.z)
    return max(tops) if tops else None
ob=oldmesh.get_bounding_box();nb=mesh.get_bounding_box()
changes=[];checked=0;missing=[]
for index,t in enumerate(jobs):
    initial=serial(t)
    uniform=(ob.max.z-ob.min.z)*t.scale3d.z/(nb.max.z-nb.min.z)
    q=t.rotation;ang=2*math.atan2(q.z,q.w);co=math.cos(ang);si=math.sin(ang)
    p=t.translation;tops=[]
    for x,y in roots:
        # FBX preserves X and changes the sign of Blender Y.
        wx=p.x+(x*co+y*si)*100*uniform;wy=p.y+(x*si-y*co)*100*uniform
        top=terrain_at(wx,wy)
        if top is None or abs(top-880)>.02:missing.append({'instance':index,'root_xy_cm':[wx,wy],'terrain_top_cm':top})
        else:tops.append(top);checked+=1
    t.scale3d=unreal.Vector(uniform,uniform,uniform)
    p.z=878.9-nb.min.z*uniform;t.translation=p
    changes.append({'before':initial,'after':serial(t)})
(folder/'grounding-preflight.json').write_text(json.dumps({'roots_checked':checked,'missing_or_wrong_elevation':missing,'root_layout_sha256':hashlib.sha256(roots_path.read_bytes()).hexdigest(),'nominal_terrace_cm':880,'root_base_cm':878.9},indent=2))
assert not missing, ('Some stalk roots lack the upper terrace',len(missing))
dest='/Game/Terrarium/Blender/WheatPatch/FT_Blender_WheatPatch'
assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest)
assert ft
ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[])
assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
shutil.copyfile(before_path,folder/'before-placement.json')
unreal.InstancedFoliageActor.add_instances(world,ft,jobs)
assert len(instances(mesh))==len(jobs)
unreal.InstancedFoliageActor.remove_all_instances(world,oldft)
assert not instances(oldmesh)
assert levels.save_current_level()
receipt.write_text(json.dumps({'asset':'WheatPatch','variant_of':'WheatField','world':world.get_path_name().split('.')[0],'old_foliage_type':oldft.get_path_name(),'new_foliage_type':ft.get_path_name(),'mesh':mesh.get_path_name(),'old_mesh':oldmesh.get_path_name(),'count':len(jobs),'stalks_per_patch':56,'instances':changes,'grounding':'All 2240 stalk roots have 880 cm meadow beneath them; roots embedded 1.1 cm beneath nominal top to cover shallow depressions.','status':'saved_pending_visual_review'},indent=2))
unreal.log('BLENDER_WHEAT_MIGRATED')
