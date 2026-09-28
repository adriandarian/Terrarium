"""Coordinator-only explicit non-destructive home apron revision.

Creates versioned assets ONLY for changed terrain chunks and relinks existing
WX actors. Original meshes remain available. Optional terrain-apron-request.json
{ "offset": 0, "limit": 8 } batches changed chunks, not the complete manifest.
"""
import json
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve();assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
assert not E.get_game_world()
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SRC=ROOT/'SourceAssets/WorldExpansion/Terrain';DOC=ROOT/'Docs/WorldExpansion'
before=json.loads((SRC/'manifest-before-apron.json').read_text())
after=json.loads((SRC/'manifest.json').read_text());old={r['name']:r for r in before['assets']}
changed=[r for r in after['assets'] if r['name'] not in old or r['sha256']!=old[r['name']]['sha256']]
assert changed and all(r['kind']=='terrain' for r in changed),'Revision must only alter terrain chunks'
assert before['roads']==after['roads'] and before['pads']==after['pads']
assert before['route_samples']==after['route_samples']
assert before['forest_instances']==after['forest_instances'],'Forest placements must remain identical'
assert len(changed)==5 and {r['name'] for r in changed}=={'Terrain_3_3','Terrain_3_4','Terrain_4_3','Terrain_4_4','HomeApron'}
cfgpath=DOC/'terrain-apron-request.json';cfg=json.loads(cfgpath.read_text()) if cfgpath.exists() else {}
rows=changed[cfg.get('offset',0):cfg.get('offset',0)+cfg.get('limit',1000)]
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
mat=unreal.load_asset('/Game/Terrarium/WorldExpansion/Terrain/Materials/M_ValleySculpted');assert mat
records=[]
for row in rows:
    source=json.loads((ROOT/row['source']).read_text())
    path='/Game/Terrarium/WorldExpansion/Terrain/Meshes/SM_'+row['name']+'_HomeApronV3'
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
        assert d.get_triangle_count()==row['triangles']
        options=unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=True,enable_recompute_normals=False,enable_recompute_tangents=False)
        mesh,outcome=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(d,path,options)
        assert mesh and outcome==unreal.GeometryScriptOutcomePins.SUCCESS
        mesh.set_material(0,mat)
        body=mesh.get_editor_property('body_setup');assert body
        body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        body.set_editor_property('double_sided_geometry',True)
        unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumSourceSHA256',row['sha256'])
        unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumRevision','Measured home perimeter apron v3')
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    label='WX_'+row['name'];actor=actors.get(label)
    if not actor:
        assert row['name']=='HomeApron'
        actor=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));actor.set_actor_label(label)
        actor.set_folder_path('WorldExpansion/Terrain')
    previous=actor.static_mesh_component.static_mesh
    if previous:
        assert unreal.EditorAssetLibrary.get_metadata_tag(previous,'TerrariumSourceSHA256') in (old.get(row['name'],row)['sha256'],row['sha256']),(label,'Unexpected existing mesh revision')
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    records.append({'actor':label,'before':previous.get_path_name() if previous else None,'after':mesh.get_path_name(),'sha256':row['sha256'],'triangles':row['triangles']})
assert L.save_current_level()
receipt={'changed_chunks_total':len(changed),'offset':cfg.get('offset',0),'records':records,
         'roads_pads_route_samples_exactly_unchanged':True,'original_meshes_retained':True}
(DOC/f'terrain-apron-{cfg.get("offset",0):03d}.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
