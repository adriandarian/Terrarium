"""Import isolated Blender calibration specimens and stage a separate review map."""
import unreal,json,hashlib,math
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir()).resolve()
assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
OUT=ROOT/'Docs/CalibrationIntegration';DATA=json.loads((ROOT/'Docs/DetailCalibration/manifest.json').read_text())
DEST='/Game/Terrarium/Calibration/Detail';LEVEL='/Game/Terrarium/Calibration/Maps/DetailDensityReview'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(),'Preserve dirty map before switching'
assert not unreal.EditorAssetLibrary.does_asset_exist(LEVEL),'Existing calibration level must be inspected'
tools=unreal.AssetToolsHelpers.get_asset_tools();mel=unreal.MaterialEditingLibrary;materials={}
for p in DATA['palette']:
 name=p['name'];mat=unreal.load_asset(DEST+'/Materials/'+name)
 if not mat:mat=tools.create_asset(name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 assert mat
 mel.delete_all_material_expressions(mat)
 n=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0);n.set_editor_property('constant',unreal.LinearColor(*p['linear_rgba']));mel.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,value in [(unreal.MaterialProperty.MP_ROUGHNESS,p['roughness']),(unreal.MaterialProperty.MP_SPECULAR,.15)]:
  n=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-250,180);n.r=value;mel.connect_material_property(n,'',prop)
 mel.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat);materials[name]=mat
meshes={};verified=[]
for row in DATA['specimens']:
 source=Path(row['fbx']).resolve();assert source.is_relative_to(ROOT/'SourceAssets/Blender/DetailCalibration') and source.is_file()
 name='SM_'+row['name'];opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.import_animations=False;opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opts.static_mesh_import_data;d.combine_meshes=True;d.generate_lightmap_u_vs=False;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
 task=unreal.AssetImportTask();task.filename=str(source);task.destination_path=DEST+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;task.options=opts;task.factory=unreal.FbxFactory();tools.import_asset_tasks([task])
 mesh=unreal.load_asset(DEST+'/Meshes/'+name);assert isinstance(mesh,unreal.StaticMesh)
 assigned=[]
 for i,slot in enumerate(mesh.static_materials):
  slotname=str(slot.get_editor_property('imported_material_slot_name'))
  matching=[key for key in materials if slotname==key or slotname.startswith(key+'.') or slotname.startswith(key+'_')]
  assert matching,('Unknown imported material slot',slotname)
  key=max(matching,key=len);mesh.set_material(i,materials[key]);assigned.append(key)
 b=mesh.get_bounding_box();size=b.max-b.min;actual=[size.x,size.y,size.z];expected=[x*100 for x in row['dimensions_m']]
 assert max(abs(a-e) for a,e in zip(actual,expected))<.1,(name,actual,expected)
 assert unreal.EditorAssetLibrary.save_loaded_asset(mesh);meshes[row['name']]=mesh
 verified.append({'name':name,'mesh':mesh.get_path_name(),'dimensions_cm':actual,'expected_cm':expected,'materials':assigned,'fbx_sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
levels.eject_pilot_level_actor();assert levels.new_level(LEVEL)
def spawn(cls,label,loc=(0,0,0)):
 a=actors.spawn_actor_from_class(cls,unreal.Vector(*loc));a.set_actor_label(label);a.set_folder_path('Calibration/Detail');return a
placements=[]
for row in DATA['specimens']:
 # Blender +Y becomes Unreal -Y in this project's established FBX conversion.
 x,y,z=row['placement_m'];loc=(x*100,-y*100,z*100)
 a=spawn(unreal.StaticMeshActor,row['name'],loc);a.static_mesh_component.set_static_mesh(meshes[row['name']]);placements.append({'actor':a.get_actor_label(),'mesh':a.static_mesh_component.static_mesh.get_path_name(),'location_cm':loc})
 # A second identical figure beside each row provides a local size reference.
 if row['column']==0:
  figure=spawn(unreal.StaticMeshActor,'ScalePerson_'+row['family'],(-250,-y*100,0));figure.static_mesh_component.set_static_mesh(meshes['DC_Person'])
floor=spawn(unreal.StaticMeshActor,'ReviewFloor',(500,-1200,-16));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(23,33,.30));floor.static_mesh_component.set_material(0,materials['M_DC_StoneDark'])
sun=spawn(unreal.DirectionalLight,'ReviewSun');sun.set_actor_rotation(unreal.Rotator(pitch=-48,yaw=-145,roll=0),False);sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);sun.light_component.set_intensity(25000);sun.light_component.set_editor_property('light_source_angle',6.);sun.light_component.set_editor_property('atmosphere_sun_light',True)
spawn(unreal.SkyAtmosphere,'ReviewAtmosphere');sky=spawn(unreal.SkyLight,'ReviewSky');sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);sky.light_component.set_editor_property('real_time_capture',True);sky.light_component.set_intensity(2.)
pp=spawn(unreal.PostProcessVolume,'ReviewExposure');pp.set_editor_property('unbound',True);s=pp.get_editor_property('settings')
for k,v in [('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL),('auto_exposure_apply_physical_camera_exposure',True),('camera_iso',100.),('camera_shutter_speed',64.),('depth_of_field_fstop',8.),('auto_exposure_bias',0.),('motion_blur_amount',0.),('vignette_intensity',0.),('bloom_intensity',0.)]:
 s.set_editor_property('override_'+k,True);s.set_editor_property(k,v)
pp.set_editor_property('settings',s)
camera=spawn(unreal.CameraActor,'Detail_Overview',(550,1950,3350));camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(550,-1150,100)),False)
cc=camera.camera_component;cc.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC);cc.set_ortho_width(2350);cc.set_editor_property('aspect_ratio',1.0);cc.set_editor_property('constrain_aspect_ratio',True);cc.set_editor_property('post_process_blend_weight',0.)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([]);assert levels.save_current_level()
levels.eject_pilot_level_actor();assert levels.load_level(LEVEL);scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
for r in placements:
 a=scene[r['actor']];c=a.static_mesh_component;assert c.static_mesh.get_path_name()==r['mesh'];assert all(c.get_material(i) for i in range(c.get_num_materials()))
camera=scene['Detail_Overview'];levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
p=camera.get_actor_location();r=camera.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(OUT/'detail-capture.json').write_text(json.dumps(args))
(OUT/'detail-import.json').write_text(json.dumps({'level':LEVEL,'saved_and_reloaded':True,'meshes':verified,'placements':placements,'materials':len(materials),'fidelity':'Unapproved construction specimens, not finished replacements'},indent=2))
