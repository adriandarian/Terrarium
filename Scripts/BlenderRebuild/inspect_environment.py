"""Read the current shrub instances and rock actors before replacing their assets."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Terrarium/Blender/Maps/HomesteadBlender.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def vec(v):return [v.x,v.y,v.z]
def transform(t):
    q=t.rotation
    return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def bounds(m):
    b=m.get_bounding_box();return {'min':vec(b.min),'max':vec(b.max)}
report={'world':world.get_path_name(),'foliage':[],'rocks':[],'foliage_types':[]}
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name()=='SM_Recon_MeadowShrub_R3':
            report['foliage'].append({'component':c.get_path_name(),'mesh':c.static_mesh.get_path_name(),'bounds':bounds(c.static_mesh),'transforms':[transform(c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count())]})
    if isinstance(a,unreal.StaticMeshActor):
        c=a.static_mesh_component
        if c.static_mesh and c.static_mesh.get_name()=='SM_Recon_MossRock_R3':
            report['rocks'].append({'actor':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'bounds':bounds(c.static_mesh),'transform':transform(a.get_actor_transform())})
for path in unreal.EditorAssetLibrary.list_assets('/Game/Terrarium/Environment/Foliage',recursive=True):
    ft=unreal.load_asset(path)
    if isinstance(ft,unreal.FoliageType_InstancedStaticMesh):
        mesh=ft.get_editor_property('mesh')
        if mesh and mesh.get_name()=='SM_Recon_MeadowShrub_R3':report['foliage_types'].append({'path':ft.get_path_name(),'mesh':mesh.get_path_name()})
(root/'Saved/blender-environment-before.json').write_text(json.dumps(report,indent=2))
unreal.log('BLENDER_ENVIRONMENT_INSPECTED')
