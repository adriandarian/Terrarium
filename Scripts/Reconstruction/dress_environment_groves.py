"""Add the smaller background groves and coarse turf pigment visible in the reference."""
import unreal,sys,math,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment';sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadReference.' in str(levels.get_current_level())
ground=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name()=='SM_Env_MeadowTile':ground.extend(c.get_instance_transform(i,world_space=True).translation for i in range(c.get_instance_count()))
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label().startswith('Reference_Grove_'):actors.destroy_actor(a)
mat=unreal.load_asset('/Game/Terrarium/Environment/Materials/M_EnvironmentPigment');mesh=unreal.load_asset('/Game/Terrarium/Meshes/SM_VoxelTree');assert mesh
rows=[]
for i,(x,y,h,s) in enumerate([(21,25,560,.68),(102,2,560,.62),(153,12,560,.62),(189,21,880,.66),(244,25,880,.58),(338,20,880,.60),(378,44,880,.64),(426,32,880,.59),(479,18,880,.80),(16,153,560,.45),(202,122,880,.42),(455,251,560,.40),(20,237,560,.46),(416,451,280,.42),(454,488,280,.5),(457,650,280,.55),(408,752,280,.58),(372,792,280,.60),(337,808,280,.49),(457,796,280,.74),(64,791,280,.50),(29,741,280,.48)]):
    p=unreal.Vector(*ref.world(x,y,h));q=min(ground,key=lambda v:(v.x-p.x)**2+(v.y-p.y)**2)
    if math.hypot(q.x-p.x,q.y-p.y)>60:continue
    p.z=q.z
    if ref.path_distance(*ref.pixel(p.x,p.y,p.z),p.z)<20:continue
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,p);a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,mat)
    a.set_actor_scale3d(unreal.Vector(s,s,s));a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=i*73,roll=0),False)
    a.set_actor_label('Reference_Grove_'+str(i));a.set_folder_path('Reference/Groves');rows.append({'actor':a.get_actor_label(),'reference_ground_pixel':ref.pixel(p.x,p.y,p.z),'ground_z_cm':p.z,'scale':s})
# Broad, discrete moss patches retain the source's small block rhythm without fine grit.
lib=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();name='M_ReferenceTurf'
turf=unreal.load_asset('/Game/Terrarium/Environment/Materials/'+name) or at.create_asset(name,'/Game/Terrarium/Environment/Materials',unreal.Material,unreal.MaterialFactoryNew())
lib.delete_all_material_expressions(turf);turf.set_editor_property('used_with_instanced_static_meshes',True)
v=lib.create_material_expression(turf,unreal.MaterialExpressionVertexColor,-450,-100);p=lib.create_material_expression(turf,unreal.MaterialExpressionWorldPosition,-450,100)
c=lib.create_material_expression(turf,unreal.MaterialExpressionCustom,-150,0);c.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
pins=[]
for key in ['Pigment','World']:
    pin=unreal.CustomInput();pin.set_editor_property('input_name',key);pins.append(pin)
c.set_editor_property('inputs',pins);c.set_editor_property('code','''
float2 id=floor(World.xy/22.0);
float h=frac(sin(dot(id,float2(127.1,311.7)))*43758.5453);
float group=sin(id.x*.21+sin(id.y*.18))*sin(id.y*.19-id.x*.11)*.5+.5;
float3 color=lerp(Pigment*float3(.90,.92,.94),Pigment*float3(1.07,1.12,.88),smoothstep(.28,.72,group));
return color*lerp(.84,1.16,floor(h*5)/4);
''')
lib.connect_material_expressions(v,'',c,'Pigment');lib.connect_material_expressions(p,'',c,'World');lib.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,1.0,180),(unreal.MaterialProperty.MP_SPECULAR,.03,290)]:
    n=lib.create_material_expression(turf,unreal.MaterialExpressionConstant,-150,y);n.set_editor_property('r',value);lib.connect_material_property(n,'',prop)
lib.recompile_material(turf);assert unreal.EditorAssetLibrary.save_loaded_asset(turf)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for ftname in ['FT_Env_MeadowTile_v5_Detail2','FT_Env_MeadowTile_Edge_v6_Detail2']:
    ft=unreal.load_asset('/Game/Terrarium/Environment/Foliage/'+ftname);assert ft
    ft.set_editor_property('override_materials',[turf]);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
for a in actors.get_all_level_actors():
    for co in a.get_components_by_class(unreal.StaticMeshComponent):
        if co.static_mesh and co.static_mesh.get_name()=='SM_Env_MeadowTile':co.set_material(0,turf)
assert levels.save_current_level();(out/'groves.json').write_text(json.dumps({'trees':rows,'turf_material':turf.get_path_name()},indent=2))
