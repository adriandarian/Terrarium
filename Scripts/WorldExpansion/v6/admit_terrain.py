import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion';assert not E.get_game_world()
L.eject_pilot_level_actor()
rows=json.loads((R/'SourceAssets/WorldExpansion/V6/Terrain/manifest.json').read_text())['geometry'];actors={a.get_actor_label():a for a in A.get_all_level_actors()}
req=json.loads((R/'Docs/WorldExpansion/V6/terrain-request.json').read_text());offset=req['offset'];limit=req['limit'];records=[]
mat=unreal.load_asset('/Game/Terrarium/WorldExpansion/V6/Terrain/Materials/M_VoxelGround');assert mat
for row in rows[offset:offset+limit]:
 path='/Game/Terrarium/WorldExpansion/V6/Terrain/Meshes/SM_'+row['name'];mesh=unreal.load_asset(path)
 if not mesh:
  s=json.loads((R/row['source']).read_text());b=unreal.GeometryScriptSimpleMeshBuffers();b.vertices=[unreal.Vector(*(v*100 for v in p)) for p in s['vertices']];b.triangles=[unreal.IntVector(a,c,b) for a,b,c in s['triangles']];b.uv0=[unreal.Vector2D(*p) for p in s['uv0']];b.vertex_colors=[unreal.LinearColor(1,1,1,1) for p in s['vertices']]
  d=unreal.DynamicMesh();d.append_buffers_to_mesh(b);unreal.GeometryScript_Normals.set_per_face_normals(d)
  mesh,result=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(d,path,unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=True,enable_recompute_normals=False,enable_recompute_tangents=False));assert mesh
  body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True)
  unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumSourceSHA256',row['sha256'])
 else:assert unreal.EditorAssetLibrary.get_metadata_tag(mesh,'TerrariumSourceSHA256')==row['sha256']
 mesh.set_material(0,mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 label='WX6_'+row['name'];a=actors.get(label) or A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(label);a.set_actor_location(unreal.Vector(0,0,0),False,False);a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll');a.set_folder_path('WorldExpansion/V6/Terrain');records.append(label)
# Switch surfaces only once all 64 replacements exist.
if all('WX6_'+q['name'] in {a.get_actor_label() for a in A.get_all_level_actors()} for q in rows):
 old=json.loads((R/'SourceAssets/WorldExpansion/TerrainV5/manifest.json').read_text())
 for ch in old['chunks']:
  if ch['old_actor']=='WX_HomeApron':continue
  for name in ch['assets']:
   a=actors['WX_'+name];c=a.static_mesh_component;c.set_visibility(False);c.set_hidden_in_game(True);c.set_collision_profile_name('NoCollision');a.set_actor_hidden_in_game(True);a.set_folder_path('WorldExpansion/RetainedTerrainV5')
 # Tower and bastions inherit the new limestone balance without touching shared art.
 stone=unreal.load_asset('/Game/Terrarium/WorldExpansion/V6/Terrain/Materials/M_VoxelStone')
 for label in ['WX6_BellTowerStone','WX6_StonegateBastions','WX6_CivicTerrace','WX6_CivicRamp']:
  a=actors[label];a.static_mesh_component.set_material(0,stone)
assert L.save_current_level();(R/f'Docs/WorldExpansion/V6/terrain-{offset:02d}.json').write_text(json.dumps({'admitted':records},indent=2));print('V6 terrain batch',offset,len(records))

