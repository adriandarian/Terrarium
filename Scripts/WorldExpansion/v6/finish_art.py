import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion';assert not E.get_game_world();L.eject_pilot_level_actor()
M=unreal.MaterialEditingLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();tex=unreal.load_asset('/Game/Terrarium/WorldExpansion/V6/Textures/T_LimestonePaving')
for name,world_uv in [('M_LimestonePaving',True),('M_CutMasonry',False)]:
 mat=unreal.load_asset('/Game/Terrarium/WorldExpansion/V6/Materials/'+name) or AT.create_asset(name,'/Game/Terrarium/WorldExpansion/V6/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
 sample=M.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D);sample.texture=tex;sample.set_editor_property('parameter_name','LimestoneAlbedo')
 if world_uv:
  pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);mask=M.create_material_expression(mat,unreal.MaterialExpressionComponentMask)
  for ch in 'rgba':mask.set_editor_property(ch,ch in 'rg')
  div=M.create_material_expression(mat,unreal.MaterialExpressionDivide);div.set_editor_property('const_b',200);M.connect_material_expressions(pos,'',mask,'');M.connect_material_expressions(mask,'',div,'A');M.connect_material_expressions(div,'',sample,'UVs')
 mul=M.create_material_expression(mat,unreal.MaterialExpressionMultiply);mul.set_editor_property('const_b',.68 if world_uv else .85);assert M.connect_material_expressions(sample,'RGB',mul,'A');assert M.connect_material_property(mul,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,val in [(unreal.MaterialProperty.MP_ROUGHNESS,.95),(unreal.MaterialProperty.MP_SPECULAR,.1)]:
  c=M.create_material_expression(mat,unreal.MaterialExpressionConstant);c.set_editor_property('r',val);M.connect_material_property(c,'',prop)
 M.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
 if not world_uv:
  for a in A.get_all_level_actors():
   if a.get_actor_label() in ['WX6_BellTowerStone','WX6_StonegateBastions','WX6_RiverMillFoundation','WX6_OldAqueduct']:a.static_mesh_component.set_material(0,mat)
views=json.loads((R/'Docs/WorldExpansion/views.json').read_text())
layout=json.loads((R/'Docs/WorldExpansion/V6/layout.json').read_text())
bylabel={a.get_actor_label():a for a in A.get_all_level_actors()}
for q in layout['geometry']:
 if q.get('asset_suffix'):
  mesh=bylabel['WX6_'+q['name']].static_mesh_component.static_mesh;unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumSourceSHA256',q['sha256']);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
extra=[('RiverMill',[96,-314,24],[61,-280,5],60),('OldAqueduct',[-153,451,27],[-195,490,15],60),('CivicCourt',[326,274,30],[290,304,33],67)]
for name,p,t,fov in extra:
 if not any(v['name']==name for v in views):views.append({'name':name,'actor':'WX_Review_'+name,'position_m':p,'target_m':t,'fov':fov})
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
for v in views:
 a=actors.get(v['actor']) or A.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(0,0,0));a.set_actor_label(v['actor']);p=unreal.Vector(*[q*100 for q in v['position_m']]);t=unreal.Vector(*[q*100 for q in v['target_m']]);a.set_actor_location(p,False,False);a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(p,t),False);a.camera_component.set_field_of_view(v['fov']);a.camera_component.set_editor_property('post_process_blend_weight',0.);a.camera_component.set_editor_property('constrain_aspect_ratio',False);a.set_editor_property('auto_activate_for_player',unreal.AutoReceiveInput.DISABLED);a.set_folder_path('WorldExpansion/ReviewCameras')
(R/'Docs/WorldExpansion/views.json').write_text(json.dumps(views,indent=2));assert L.save_current_level();print('Materials and all review cameras saved')
