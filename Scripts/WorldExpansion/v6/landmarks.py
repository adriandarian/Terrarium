import unreal,json,math
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
D=R/'Docs/WorldExpansion/V6';data=json.loads((D/'landmarks.json').read_text());layout=json.loads((D/'layout.json').read_text())
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);w=E.get_editor_world()
assert w.get_path_name().split('.')[0]==layout['map'];assert not E.get_game_world();L.eject_pilot_level_actor()
actors={a.get_actor_label():a for a in A.get_all_level_actors()};ignored=[a for a in actors.values() if not a.get_actor_label().startswith('WX6_Terrain6_')]
def ground(x,y):
 hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x*100,y*100,90000),unreal.Vector(x*100,y*100,-3000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignored,unreal.DrawDebugTrace.NONE,False)
 hit=hit if isinstance(hit,unreal.HitResult) else next((h for h in (hit or []) if isinstance(h,unreal.HitResult)),None);assert hit and hit.to_tuple()[0];return hit.to_tuple()[5].z/100
mats={'stone':unreal.load_asset('/Game/Terrarium/WorldExpansion/V6/Terrain/Materials/M_VoxelStone'),'wood':unreal.load_asset('/Game/Terrarium/HomesteadPilot/Architecture/Materials/M_HP_Wood'),'paving':unreal.load_asset('/Game/Terrarium/WorldExpansion/TerrainV5/Materials/M_VoxelPath')}
def meshactor(name,source,material):
 path='/Game/Terrarium/WorldExpansion/V6/Meshes/SM_'+name;mesh=unreal.load_asset(path)
 if not mesh:
  b=unreal.GeometryScriptSimpleMeshBuffers();b.vertices=[unreal.Vector(*(v*100 for v in p)) for p in source['vertices']];b.triangles=[unreal.IntVector(a,c,b) for a,b,c in source['triangles']];b.uv0=[unreal.Vector2D(*p) for p in source['uv0']];b.vertex_colors=[unreal.LinearColor(1,1,1,1) for p in source['vertices']]
  d=unreal.DynamicMesh();d.append_buffers_to_mesh(b);unreal.GeometryScript_Normals.set_per_face_normals(d)
  mesh,result=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(d,path,unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=True,enable_recompute_normals=False,enable_recompute_tangents=False));assert mesh
  body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True)
 mesh.set_material(0,mats[material]);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 label='WX6_'+name;a=actors.get(label) or A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label(label);a.set_actor_location(unreal.Vector(0,0,0),False,False);a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll');a.set_folder_path('WorldExpansion/V6/JourneyLandmarks');return a
records=[]
for q in data['geometry']:records.append(meshactor(q['name'],json.loads((R/q['source']).read_text()),q['material']).get_actor_label())
for q in data['placements']:
 mesh=unreal.load_asset(layout['assets'][q['asset']]);x,y,z=q['location'];z-=mesh.get_bounding_box().min.z*q['scale'][2]/100
 label='WX6_'+q['name'];a=actors.get(label) or A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label(label);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_transform(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100),rotation=unreal.Rotator(pitch=0,yaw=q['yaw'],roll=0),scale=unreal.Vector(*q['scale'])),False,False);a.static_mesh_component.set_collision_profile_name('BlockAll');a.set_folder_path('WorldExpansion/V6/JourneyLandmarks');records.append(label)
for q in data['paths']:
 vs=[];ts=[];uv=[];center=[]
 for a,b in zip(q['points'],q['points'][1:]):
  dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);nx=-dy/ln*q['width']/2;ny=dx/ln*q['width']/2;n=math.ceil(ln/1.5)
  for i in range(n+1):
   x=a[0]+dx*i/n;y=a[1]+dy*i/n;center.append([x,y,ground(x,y)])
   for side in [-1,1]:
    xx=x+side*nx;yy=y+side*ny;vs.append([xx,yy,ground(xx,yy)+.045]);uv.append([xx/2,yy/2])
   if i:
    k=len(vs)-4;ts.extend([[k,k+1,k+2],[k+1,k+3,k+2]])
 source={'vertices':vs,'triangles':ts,'uv0':uv};(R/'SourceAssets/WorldExpansion/V6'/f"{q.get('mesh_name',q['name'])}.json").write_text(json.dumps(source));records.append(meshactor(q.get('mesh_name',q['name']),source,'paving').get_actor_label());q['native_ground_centerline']=center
 if q.get('mesh_name') and actors.get('WX6_'+q['name']):
  old=actors['WX6_'+q['name']];old.static_mesh_component.set_visibility(False);old.static_mesh_component.set_hidden_in_game(True);old.static_mesh_component.set_collision_profile_name('NoCollision');old.set_actor_hidden_in_game(True)
# Civic terrace perimeter gets planted edges rather than a bare stone apron.
for i,(x,y) in enumerate([(279,289),(279,316),(320,289),(320,316),(296,319),(309,319)]):
 label=f'WX6_CivicTree_{i}';mesh=unreal.load_asset(layout['assets']['BroadTree5m']);a=actors.get(label) or A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label(label);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_location(unreal.Vector(x*100,y*100,2550-mesh.get_bounding_box().min.z*1.1),False,False);a.set_actor_scale3d(unreal.Vector(1.1,1.1,1.1));a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_folder_path('WorldExpansion/V6/CivicGarden')
# Region-local atmospheric perspective. Preserve the original maps and source lighting.
for a in A.get_all_level_actors():
 if isinstance(a,unreal.ExponentialHeightFog):
  c=a.component;c.set_fog_density(.012);c.set_fog_height_falloff(.035);c.set_start_distance(17000);c.set_fog_max_opacity(.5)
assert L.save_current_level();(D/'landmark-integration.json').write_text(json.dumps({'actors':records,'paths':data['paths'],'waterwheel':'Static authored geometry; no milling simulation'},indent=2));print('Journey landmarks saved')
