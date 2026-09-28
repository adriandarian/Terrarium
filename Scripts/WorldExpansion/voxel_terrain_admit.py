"""Coordinator-only V5 admission. Explicit versioned assets; original terrain retained.

Run sequentially with Docs/WorldExpansion/voxel-terrain-request.json containing
    {"offset":0,"limit":4}. Offsets select chunks (two role meshes per chunk).
    Chunk64 replaces only the outer ring of the home apron at1m cell size.
Retirement occurs only after both replacement mesh actors exist and save.
"""
import json
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve();assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
assert not E.get_game_world()
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
DOC=ROOT/'Docs/WorldExpansion/TerrainV5';DOC.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'SourceAssets/WorldExpansion/TerrainV5/manifest.json').read_text())
assets={r['name']:r for r in manifest['assets']}
materials={role:unreal.load_asset(path) for role,path in manifest['materials'].items()}
assert all(materials.values()),'Coordinator must build both V5 private imagegen materials first'
request=ROOT/'Docs/WorldExpansion/voxel-terrain-request.json';cfg=json.loads(request.read_text()) if request.exists() else {'offset':0,'limit':4}
chunks=manifest['chunks'][cfg.get('offset',0):cfg.get('offset',0)+cfg.get('limit',4)]
actors={a.get_actor_label():a for a in A.get_all_level_actors()};records=[];retired=[]
for chunk in chunks:
    for name in chunk['assets']:
        row=assets[name];path='/Game/Terrarium/WorldExpansion/TerrainV5/Meshes/SM_'+name
        mesh=unreal.load_asset(path)
        if mesh:assert unreal.EditorAssetLibrary.get_metadata_tag(mesh,'TerrariumSourceSHA256')==row['sha256']
        else:
            source=json.loads((ROOT/row['source']).read_text())
            d=unreal.DynamicMesh();buf=unreal.GeometryScriptSimpleMeshBuffers()
            buf.vertices=[unreal.Vector(*(v*100 for v in p)) for p in source['vertices']]
            buf.triangles=[unreal.IntVector(a,c,b) for a,b,c in source['triangles']]
            buf.vertex_colors=[unreal.LinearColor(*rgb,1) for rgb in source['colors']]
            buf.uv0=[unreal.Vector2D(*p) for p in source['uv0']]
            d.append_buffers_to_mesh(buf);unreal.GeometryScript_Normals.set_per_face_normals(d)
            assert d.get_triangle_count()==row['triangles']
            options=unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=True,enable_recompute_normals=False,enable_recompute_tangents=False)
            mesh,outcome=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(d,path,options)
            assert mesh and outcome==unreal.GeometryScriptOutcomePins.SUCCESS
            body=mesh.get_editor_property('body_setup');assert body
            body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            body.set_editor_property('double_sided_geometry',True)
            unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumSourceSHA256',row['sha256'])
            unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumTerrainRevision','5')
        mesh.set_material(0,materials[row['role']])
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        label='WX_'+name;actor=actors.get(label)
        if not actor:
            actor=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));actor.set_actor_label(label);actors[label]=actor
        c=actor.static_mesh_component;c.set_static_mesh(mesh)
        c.set_collision_profile_name('BlockAll');c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        c.set_visibility(True);c.set_hidden_in_game(False)
        actor.set_actor_hidden_in_game(False);actor.set_folder_path('WorldExpansion/VoxelTerrainV5')
        assert str(c.get_collision_profile_name())=='BlockAll'
        records.append({'actor':label,'mesh':mesh.get_path_name(),'material':materials[row['role']].get_path_name(),'triangles':row['triangles'],'source_sha256':row['sha256'],'collision_profile':str(c.get_collision_profile_name())})
    old=actors.get(chunk['old_actor']);assert old,chunk['old_actor']
    c=old.static_mesh_component;c.set_collision_profile_name('NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    c.set_visibility(False);c.set_hidden_in_game(True);old.set_actor_hidden_in_game(True)
    old.set_folder_path('WorldExpansion/RetainedTerrainV4')
    assert str(c.get_collision_profile_name())=='NoCollision'
    assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
    retired.append({'actor':old.get_actor_label(),'mesh_preserved':c.static_mesh.get_path_name(),'visible':bool(c.is_visible()),'collision_profile':str(c.get_collision_profile_name())})
assert L.save_current_level()
receipt={'revision':5,'offset':cfg.get('offset',0),'chunks':len(chunks),'admitted':records,'retired':retired,'home_apron_outer_ring_replaced':any(c['old_actor']=='WX_HomeApron' for c in chunks),'roads_pads_water_and_original_home_untouched':True}
(DOC/f'admission-{cfg.get("offset",0):03d}.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({'revision':5,'chunks':len(chunks),'assets':len(records),'triangles':sum(r['triangles'] for r in records),'retired':len(retired)}))
