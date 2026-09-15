"""Read current foliage bindings and placements before a Blender replacement."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
key=(root/'Saved/blender-import-asset.txt').read_text().strip()
oldname={'HomesteadTree':'SM_Recon_HomesteadTree_R3','AncientTree':'SM_Recon_AncientTree_R3','WheatField':'SM_Env_WheatPatch','Riverbank':'SM_Recon_Riverbank_R3','GrassTerrain':'SM_Env_MeadowTile','MossFringe':'SM_CliffMoss_v1_Detail','TrailTerrain':'SM_PathTile_v4_Detail'}[key]
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Terrarium/Blender/Maps/HomesteadBlender.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
report={'asset':key,'world':world.get_path_name(),'components':[],'foliage_types':[],'static_actors':[]}
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name()==oldname:
            b=c.static_mesh.get_bounding_box()
            report['components'].append({'component':c.get_path_name(),'mesh':c.static_mesh.get_path_name(),'bounds':{'min':vec(b.min),'max':vec(b.max)},'transforms':[serial(c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count())]})
    if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==oldname:
        report['static_actors'].append({'actor':a.get_actor_label(),'transform':serial(a.get_actor_transform())})
for path in unreal.EditorAssetLibrary.list_assets('/Game/Terrarium/Environment/Foliage',recursive=True)+unreal.EditorAssetLibrary.list_assets('/Game/Terrarium/Foliage',recursive=True):
    ft=unreal.load_asset(path)
    if isinstance(ft,unreal.FoliageType_InstancedStaticMesh):
        mesh=ft.get_editor_property('mesh')
        if mesh and mesh.get_name()==oldname:report['foliage_types'].append({'path':ft.get_path_name(),'mesh':mesh.get_path_name()})
(root/'Saved'/('blender-foliage-'+key+'.json')).write_text(json.dumps(report,indent=2))
