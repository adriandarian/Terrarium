"""Diagnose the new cliff collision observed above a sampled meadow surface."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
grass=next(c for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent) if c.get_name()=='FoliageInstancedStaticMeshComponent_5' and c.static_mesh and c.static_mesh.get_name()=='SM_Blender_GrassTerrain')
p=grass.get_instance_transform(62,world_space=True).translation
result={'point_cm':[p.x,p.y,p.z],'component_trace_methods':{n:str(getattr(type(grass),n).__doc__) for n in dir(grass) if 'trace' in n.lower()},'cliffs':[]}
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if not c.static_mesh or c.static_mesh.get_name()!='SM_Blender_CliffColumn':continue
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,world_space=True);local=unreal.MathLibrary.inverse_transform_location(t,p)
            if abs(local.x)<=50 and abs(local.y)<=50:
                result['cliffs'].append({'component':c.get_name(),'index':i,'local_point':str(local),'cap_z_cm':t.translation.z+323.5*t.scale3d.z})
(root/'Docs/BlenderRebuild/CliffColumn/grass-overlap-inspection.json').write_text(json.dumps(result,indent=2))
