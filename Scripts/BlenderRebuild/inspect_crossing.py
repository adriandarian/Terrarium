"""Read existing bridge geometry, transforms and nearby approach surfaces."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
def v(p):return [p.x,p.y,p.z]
def t(a):
    q=a.get_actor_transform().rotation
    return {'translation':v(a.get_actor_location()),'scale':v(a.get_actor_scale3d()),'rotation_xyzw':[q.x,q.y,q.z,q.w],'rotator':str(a.get_actor_rotation())}
report={'world':world.get_path_name(),'bridges':[],'stairs':[],'nearby':[]}
for a in actors.get_all_level_actors():
    if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh:
        m=a.static_mesh_component.static_mesh;name=a.get_actor_label()+' '+m.get_name()
        if any(x in name.lower() for x in ['bridge','crossing','stair']):
            b=m.get_bounding_box();c,e=a.get_actor_bounds(False)
            row={'actor':a.get_actor_label(),'mesh':m.get_path_name(),'transform':t(a),'mesh_bounds':{'min':v(b.min),'max':v(b.max)},'world_center':v(c),'world_extent':v(e)}
            report['bridges' if any(x in name.lower() for x in ['bridge','crossing']) else 'stairs'].append(row)
(root/'Saved/blender-crossing-before.json').write_text(json.dumps(report,indent=2))
