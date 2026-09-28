import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
# Reuse the admitted geometry helper without executing its scene assembly.
s=(R/'Scripts/WorldExpansion/v6/landmarks.py').read_text();exec(compile(s[:s.index('\nrecords=[]')],'landmark_helpers','exec'))
mats['stone']=unreal.load_asset('/Game/Terrarium/WorldExpansion/V6/Materials/M_CutMasonry');mats['brass']=unreal.load_asset('/Game/Terrarium/HomesteadPilot/Architecture/Materials/M_HP_Brass')
rows=[r for r in layout['geometry'] if r['name'] in ['BellTowerStone','CivicRamp']]+json.loads((D/'refinements.json').read_text())['geometry']
for q in rows:
 old=actors.get('WX6_'+q['name']);name=q['name']+q.get('asset_suffix','');a=meshactor(name,json.loads((R/q['source']).read_text()),q['material'])
 if old and old!=a:
  old.static_mesh_component.set_static_mesh(a.static_mesh_component.static_mesh);old.static_mesh_component.set_material(0,mats[q['material']]);A.destroy_actor(a)
for i,(x,y) in enumerate([(279.5,295),(279.5,311),(319.5,295),(319.5,311)]):
 for j,(dx,dy) in enumerate([(-.9,-.9),(.9,.9),(-.9,.9),(.9,-.9)]):
  mesh=unreal.load_asset(layout['assets']['ShrubGroundcover']);label=f'WX6_PlanterShrub_{i}_{j}';a=actors.get(label) or A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));a.set_actor_label(label);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_location(unreal.Vector((x+dx)*100,(y+dy)*100,2580-mesh.get_bounding_box().min.z),False,False);a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_folder_path('WorldExpansion/V6/CivicGarden')
views=json.loads((R/'Docs/WorldExpansion/views.json').read_text());v=next(v for v in views if v['name']=='RiverMill');v['position_m']=[24,-307,15];v['target_m']=[61,-282,5]
(R/'Docs/WorldExpansion/views.json').write_text(json.dumps(views,indent=2));assert L.save_current_level();(D/'refinement-integration.json').write_text(json.dumps({'geometry':[r['name'] for r in rows],'planter_shrubs':16},indent=2))
