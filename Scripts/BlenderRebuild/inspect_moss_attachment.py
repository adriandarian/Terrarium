"""Check modeled root points against the rebuilt cliffs' known solid core volumes."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
cliffs=[];moss=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if not c.static_mesh:continue
        if c.static_mesh.get_name()=='SM_Blender_CliffColumn':
            cliffs.extend((c.get_name(),i,c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count()))
        if c.static_mesh.get_name()=='SM_Blender_MossFringe':
            moss.extend((c.get_name(),i,c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count()))
assert len(cliffs)==2076 and len(moss)==209
anchors=[unreal.Vector(-12,0,-3),unreal.Vector(-5,0,-3),unreal.Vector(12,0,-3),unreal.Vector(-12,0,-6),unreal.Vector(-5,0,-6),unreal.Vector(12,0,-6)]
rows=[]
for name,i,t in moss:
    matches=[]
    candidates=[r for r in cliffs if abs(r[2].translation.x-t.translation.x)<150 and abs(r[2].translation.y-t.translation.y)<150]
    for j,anchor in enumerate(anchors):
        p=unreal.MathLibrary.transform_location(t,anchor)
        for cn,ci,ct in candidates:
            q=unreal.MathLibrary.inverse_transform_location(ct,p)
            core=abs(q.x)<47.5 and abs(q.y)<47.5 and 0<q.z<320
            cap=abs(q.x)<50 and abs(q.y)<50 and 320<=q.z<323.5
            if core or cap:
                matches.append({'anchor':j,'cliff_component':cn,'cliff_index':ci,'volume':'core' if core else 'cap'});break
    rows.append({'component':name,'index':i,'position_cm':[t.translation.x,t.translation.y,t.translation.z],'embedded_root_samples':matches,'root_overlap_verified':bool(matches)})
(root/'Docs/BlenderRebuild/MossFringe/root-attachment.json').write_text(json.dumps({'world':world.get_path_name(),'count':209,'with_root_overlap':sum(r['root_overlap_verified'] for r in rows),'anchor_points_cm':[[v.x,v.y,v.z] for v in anchors],'method':'Six points inside the authored moss root cushion tested against the exact 95 x 95 x 320 cm cliff core and 100 x 100 x 3.5 cm cap, transformed per instance. This checks root intersection, not full visible contact or collision response.','instances':rows},indent=2))
unreal.log('BLENDER_MOSS_ROOTS_INSPECTED')
