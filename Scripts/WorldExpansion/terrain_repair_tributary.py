"""Coordinator-only focused water seam repair, preserving every terrain mesh."""
import json
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve();assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
assert not E.get_game_world()
SRC=ROOT/'SourceAssets/WorldExpansion/Terrain'
manifest=json.loads((SRC/'manifest.json').read_text())
row=next(r for r in manifest['assets'] if r['name']=='HomeTributary')
prior=json.loads((SRC/'tributary-before-seam.json').read_text())
source=json.loads((ROOT/row['source']).read_text())
path='/Game/Terrarium/WorldExpansion/Terrain/Meshes/SM_HomeTributary_SeamV4'
mat=unreal.load_asset('/Game/Terrarium/HomesteadPilot/RemainingEnvironment/Materials/M_HP_RiverCurrent');assert mat
mesh=unreal.load_asset(path)
if mesh:
    assert unreal.EditorAssetLibrary.get_metadata_tag(mesh,'TerrariumSourceSHA256')==row['sha256']
else:
    d=unreal.DynamicMesh();buf=unreal.GeometryScriptSimpleMeshBuffers()
    buf.vertices=[unreal.Vector(*(v*100 for v in p)) for p in source['vertices']]
    buf.triangles=[unreal.IntVector(a,c,b) for a,b,c in source['triangles']]
    buf.vertex_colors=[unreal.LinearColor(*rgb,1) for rgb in source['colors']]
    buf.uv0=[unreal.Vector2D(p[0]/4,p[1]/4) for p in source['vertices']]
    d.append_buffers_to_mesh(buf);unreal.GeometryScript_Normals.set_per_face_normals(d)
    assert d.get_triangle_count()==48
    options=unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=False,enable_recompute_normals=False,enable_recompute_tangents=False)
    mesh,outcome=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(d,path,options)
    assert mesh and outcome==unreal.GeometryScriptOutcomePins.SUCCESS
    mesh.set_material(0,mat)
    unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumSourceSHA256',row['sha256'])
    unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumRevision','Tributary overlap seam v4')
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='WX_HomeTributary')
component=actor.static_mesh_component
previous=component.static_mesh
assert unreal.EditorAssetLibrary.get_metadata_tag(previous,'TerrariumSourceSHA256') in (prior['sha256'],row['sha256'])
component.set_static_mesh(mesh)
component.set_collision_profile_name('NoCollision')
component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
assert str(component.get_collision_profile_name())=='NoCollision'
assert component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
receipt={'actor':actor.get_actor_label(),'before':previous.get_path_name(),'after':mesh.get_path_name(),
         'half_width_m':7.5,'start_x_m':35.5,'water_z_m':.05,'triangles':48,
         'collision_profile':str(component.get_collision_profile_name()),'collision_enabled':str(component.get_collision_enabled()),
         'terrain_changed':False,'sha256':row['sha256']}
(ROOT/'Docs/WorldExpansion/tributary-seam-repair.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
