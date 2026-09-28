"""Run only through verified Terrarium editor MCP. V6 native admission."""
import unreal,json,hashlib
from pathlib import Path
from collections import defaultdict
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
D=R/'Docs/WorldExpansion/V6';data=json.loads((D/'layout.json').read_text())
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w=E.get_editor_world();assert w.get_path_name().split('.')[0]==data['map'];assert not E.get_game_world()
L.eject_pilot_level_actor()
AT=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;DEST='/Game/Terrarium/WorldExpansion/V6'
archive='/Game/Terrarium/WorldExpansion/Maps/ValleyRegionV5Archive'
if not unreal.EditorAssetLibrary.does_asset_exist(archive):
 assert L.save_current_level();assert unreal.EditorAssetLibrary.duplicate_asset(data['map'],archive);assert unreal.EditorAssetLibrary.save_asset(archive)
src=R/'SourceAssets/WorldExpansion/V6/T_LimestonePaving.png';tex=unreal.load_asset(DEST+'/Textures/T_LimestonePaving')
if not tex:
 t=unreal.AssetImportTask();t.filename=str(src);t.destination_path=DEST+'/Textures';t.destination_name='T_LimestonePaving';t.automated=True;t.save=True;AT.import_asset_tasks([t]);tex=unreal.load_asset(DEST+'/Textures/T_LimestonePaving')
assert tex
tex.set_editor_property('srgb',True);tex.set_editor_property('power_of_two_mode',unreal.TexturePowerOfTwoSetting.STRETCH_TO_POWER_OF_TWO);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP)
unreal.EditorAssetLibrary.set_metadata_tag(tex,'TerrariumImagegenSourceSHA256',hashlib.sha256(src.read_bytes()).hexdigest());assert unreal.EditorAssetLibrary.save_loaded_asset(tex)
mat=unreal.load_asset(DEST+'/Materials/M_LimestonePaving') or AT.create_asset('M_LimestonePaving',DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
M.delete_all_material_expressions(mat)
sample=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);sample.texture=tex
pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);mask=M.create_material_expression(mat,unreal.MaterialExpressionComponentMask);mask.set_editor_property('r',True);mask.set_editor_property('g',True);mask.set_editor_property('b',False);mask.set_editor_property('a',False)
div=M.create_material_expression(mat,unreal.MaterialExpressionDivide);div.set_editor_property('const_b',200)
assert M.connect_material_expressions(pos,'',mask,'');assert M.connect_material_expressions(mask,'',div,'A');assert M.connect_material_expressions(div,'',sample,'UVs')
assert M.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
for prop,val in [(unreal.MaterialProperty.MP_ROUGHNESS,.93),(unreal.MaterialProperty.MP_SPECULAR,.12)]:
 c=M.create_material_expression(mat,unreal.MaterialExpressionConstant);c.set_editor_property('r',val);assert M.connect_material_property(c,'',prop)
M.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
materials={'paving':mat,'stone':unreal.load_asset('/Game/Terrarium/WorldExpansion/TerrainV5/Materials/M_VoxelStone'),'roof':unreal.load_asset('/Game/Terrarium/HomesteadPilot/Architecture/Materials/M_HP_Roof')}
assert all(materials.values())
records={'revision':6,'archive':archive,'texture':tex.get_path_name(),'texture_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'retired_actors':[],'retired_foliage_types':[],'geometry':[],'actors':[],'foliage':[]}
# Retain old actor geometry in the map but deactivate it explicitly.
old=json.loads((R/'Docs/WorldExpansion/settlement-layout.json').read_text())
labels={q['label'] for q in old['placements']}
labels.update(q['label'] for q in json.loads((R/'Docs/WorldExpansion/settlement-dressing-layout.json').read_text())['placements'])
for a in A.get_all_level_actors():
 if a.get_actor_label() in labels:
  a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.set_folder_path('WorldExpansion/RetiredSettlementsV5')
  for c in a.get_components_by_class(unreal.StaticMeshComponent):c.set_visibility(False);c.set_hidden_in_game(True);c.set_collision_profile_name('NoCollision')
  records['retired_actors'].append(a.get_actor_label())
for folder in ['/Game/Terrarium/WorldExpansion/SettlementFoliage','/Game/Terrarium/WorldExpansion/DressingFoliage']:
 for p in unreal.EditorAssetLibrary.list_assets(folder,recursive=True,include_folder=False):
  ft=unreal.load_asset(p)
  if isinstance(ft,unreal.FoliageType_InstancedStaticMesh):unreal.InstancedFoliageActor.remove_all_instances(w,ft);records['retired_foliage_types'].append(p)
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
for row in data['geometry']:
 path=DEST+'/Meshes/SM_'+row['name']+row.get('asset_suffix','');mesh=unreal.load_asset(path)
 if not mesh:
  source=json.loads((R/row['source']).read_text());buf=unreal.GeometryScriptSimpleMeshBuffers();buf.vertices=[unreal.Vector(*(v*100 for v in p)) for p in source['vertices']];buf.triangles=[unreal.IntVector(a,c,b) for a,b,c in source['triangles']];buf.uv0=[unreal.Vector2D(*p) for p in source['uv0']]
  buf.vertex_colors=[unreal.LinearColor(1,1,1,1) for p in source['vertices']];dm=unreal.DynamicMesh();dm.append_buffers_to_mesh(buf);unreal.GeometryScript_Normals.set_per_face_normals(dm)
  opts=unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=True,enable_recompute_normals=False,enable_recompute_tangents=False)
  mesh,outcome=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm,path,opts);assert mesh
  bs=mesh.get_editor_property('body_setup');bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);bs.set_editor_property('double_sided_geometry',True)
  unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumSourceSHA256',row['sha256'])
 else:assert unreal.EditorAssetLibrary.get_metadata_tag(mesh,'TerrariumSourceSHA256')==row['sha256']
 mesh.set_material(0,materials[row['material']]);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 label='WX6_'+row['name'];a=actors.get(label) or A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(label);a.set_actor_location(unreal.Vector(0,0,0),False,False);a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll');a.set_folder_path('WorldExpansion/V6/LandmarksAndLanes');records['geometry'].append({'label':label,'mesh':mesh.get_path_name(),'triangles':row['triangles'],'material':materials[row['material']].get_path_name()})
meshes={k:unreal.load_asset(p) for k,p in data['assets'].items()};assert all(meshes.values())
def transform(row):
 m=meshes[row['asset']];x,y,z=[v*100 for v in row['location_m']];z-=m.get_bounding_box().min.z*row['scale'][2]
 return unreal.Transform(location=unreal.Vector(x,y,z),rotation=unreal.Rotator(pitch=0,yaw=row['yaw_deg'],roll=0),scale=unreal.Vector(*row['scale']))
for row in data['placements']:
 a=actors.get(row['label']) or A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(row['label']);a.static_mesh_component.set_static_mesh(meshes[row['asset']]);a.set_actor_transform(transform(row),False,False);a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_editor_property('forced_lod_model',0);a.set_folder_path('WorldExpansion/V6/'+row['settlement']);records['actors'].append({'label':row['label'],'mesh':meshes[row['asset']].get_path_name()})
groups=defaultdict(list)
for row in data['instances']:groups[row['asset']].append(row)
for k,rows in groups.items():
 name='FT_WX6_'+k;ft=unreal.load_asset(DEST+'/Foliage/'+name) or AT.create_asset(name,DEST+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());ft.set_editor_property('mesh',meshes[k])
 body=ft.get_editor_property('body_instance');body.set_editor_property('collision_profile_name','BlockAll' if k=='MossCliff4m' else 'NoCollision');body.set_editor_property('collision_enabled',unreal.CollisionEnabled.QUERY_AND_PHYSICS if k=='MossCliff4m' else unreal.CollisionEnabled.NO_COLLISION);ft.set_editor_property('body_instance',body)
 assert unreal.EditorAssetLibrary.save_loaded_asset(ft);unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 before={c.get_path_name():c.get_instance_count() for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent)}
 unreal.InstancedFoliageActor.add_instances(w,ft,[transform(row) for row in rows]);components=[]
 for a in A.get_all_level_actors():
  for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
   n=c.get_instance_count()-before.get(c.get_path_name(),0)
   if n>0:components.append({'path':c.get_path_name(),'count':n})
 assert sum(c['count'] for c in components)==len(rows)
 records['foliage'].append({'asset':k,'type':ft.get_path_name(),'count':len(rows),'components':components})
# Regional trade routes take the same stone surface; original home approach is protected.
records['road_materials']=[]
for a in A.get_all_level_actors():
 if a.get_actor_label().startswith('WX_') and 'Road' in a.get_actor_label():
  for c in a.get_components_by_class(unreal.StaticMeshComponent):c.set_material(0,mat)
  records['road_materials'].append(a.get_actor_label())
assert L.save_current_level();(D/'integration.json').write_text(json.dumps(records,indent=2));print('V6 integrated: '+json.dumps(data['summary']))



