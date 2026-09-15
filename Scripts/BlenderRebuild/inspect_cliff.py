"""Read existing cliff module dimensions and placements before Blender reconstruction."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Game/Terrarium/Blender/Maps/HomesteadBlender.' in str(levels.get_current_level())
def vec(v):return [v.x,v.y,v.z]
rows=[]
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        mesh=c.static_mesh
        if not mesh or 'Cliff' not in mesh.get_name():continue
        b=mesh.get_bounding_box();samples=[]
        for i in range(min(c.get_instance_count(),5)):
            t=c.get_instance_transform(i,world_space=True);q=t.rotation
            samples.append({'index':i,'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]})
        rows.append({'component':c.get_name(),'mesh':mesh.get_path_name(),'count':c.get_instance_count(),'bounds_cm':{'min':vec(b.min),'max':vec(b.max)},'samples':samples})
folder=root/'Docs/BlenderRebuild/CliffFace';folder.mkdir(exist_ok=True)
(folder/'existing-cliff-inspection.json').write_text(json.dumps(rows,indent=2))
unreal.log('BLENDER_CLIFF_INSPECTED')
