"""Focused native geometry, texture and foliage validation, plus original preservation."""
import unreal,json,hashlib,math
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium');D=R/'Docs/WorldExpansion/V6'
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=E.get_editor_world();assert w.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion';assert not E.get_game_world()
data=json.loads((D/'layout.json').read_text());receipt=json.loads((D/'integration.json').read_text());actors={a.get_actor_label():a for a in A.get_all_level_actors()};errors=[]
for row in data['placements']:
 a=actors.get(row['label'])
 if not a:errors.append('Missing '+row['label']);continue
 c=a.static_mesh_component;t=a.get_actor_transform();expected=row['location_m'];expectedz=expected[2]*100-c.static_mesh.get_bounding_box().min.z*row['scale'][2]
 if max(abs(t.translation.x-expected[0]*100),abs(t.translation.y-expected[1]*100),abs(t.translation.z-expectedz))>.1:errors.append('Transform '+row['label'])
 if not c.is_visible() or str(c.get_collision_profile_name())!='BlockAll':errors.append('Visibility/collision '+row['label'])
for label in receipt['retired_actors']:
 c=actors[label].static_mesh_component
 if c.is_visible() or str(c.get_collision_profile_name())!='NoCollision':errors.append('Retired still active '+label)
foliage=[]
settlement_groups=json.loads((D/'detail-grounding.json').read_text())['groups'] if (D/'detail-grounding.json').exists() else receipt['foliage']
for row in settlement_groups+json.loads((D/'river-ecology.json').read_text())['groups']:
 count=0
 for c in row['components']:
  obj=unreal.load_object(None,c['path'])
  if obj:count+=obj.get_instance_count()
 if count!=row['count']:errors.append('Foliage '+row['type'])
 foliage.append({'type':row['type'],'expected':row['count'],'actual':count})
tex=unreal.load_asset(receipt['texture']);actualhash=hashlib.sha256((R/'SourceAssets/WorldExpansion/V6/T_LimestonePaving.png').read_bytes()).hexdigest()
if unreal.EditorAssetLibrary.get_metadata_tag(tex,'TerrariumImagegenSourceSHA256')!=actualhash:errors.append('Imagegen source hash mismatch')
material_textures=[]
for name in ['M_LimestonePaving','M_CutMasonry']:
 mat=unreal.load_asset('/Game/Terrarium/WorldExpansion/V6/Materials/'+name);used=unreal.MaterialEditingLibrary.get_used_textures(mat);material_textures.append({'material':mat.get_path_name(),'textures':[t.get_path_name() for t in used]})
 if tex not in used:errors.append('Material texture reference '+name)
terrain=[a for k,a in actors.items() if k.startswith('WX6_Terrain6_')]
if len(terrain)!=64:errors.append('Terrain count')
for a in terrain:
 c=a.static_mesh_component
 if a.get_actor_location().length()>.01 or not c.is_visible() or str(c.get_collision_profile_name())!='BlockAll':errors.append('Terrain state '+a.get_actor_label())
checks=[]
for name,x,y,z in [('Market',300,260,24.07),('Civic ramp mid',300,280,24.78),('Civic terrace',300,291,25.51),('Mill platform',69,-276,7.1),('Mill stair bottom',55.8,-288.7,1.5),('Gate opening',-320,311,35),('Home road hub',-25,55,5.6)]:
 hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x*100,y*100,(z+2)*100),unreal.Vector(x*100,y*100,(z-3)*100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,False)
 hit=hit if isinstance(hit,unreal.HitResult) else next((h for h in (hit or []) if isinstance(h,unreal.HitResult)),None);t=hit.to_tuple() if hit else None;actual=t[5].z/100 if t and t[0] else None;passed=actual is not None and abs(actual-z)<.35
 checks.append({'name':name,'expected_m':z,'actual_m':actual,'passed':passed,'actor':t[9].get_actor_label() if t and t[0] else None})
 if not passed:errors.append('Ground '+name)
out={'passed':not errors,'errors':errors,'buildings_checked':len(data['placements']),'terrain_chunks':len(terrain),'foliage':foliage,'ground':checks,'imagegen_source_sha256':actualhash,'native_texture':tex.get_path_name(),'material_textures':material_textures,'limits':['Full region navigation and physical held-key input not tested','New landmarks are static scenery','Terrain has one visible LOD and no streaming']}
(D/'validation.json').write_text(json.dumps(out,indent=2));print(json.dumps({'passed':not errors,'errors':errors}))
