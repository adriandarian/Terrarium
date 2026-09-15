"""Fit rebuilt courtyard parts, coarse ground and grouped planting to the reference."""
import unreal,json,sys,math
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment'
sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadReference.' in str(levels.get_current_level())
assert not (out/'integration-stage2.json').exists(),'Stage two already saved'
levels.eject_pilot_level_actor();assert levels.load_level('/Game/Terrarium/Maps/HomesteadReference')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();at=unreal.AssetToolsHelpers.get_asset_tools()
mat=unreal.load_asset('/Game/Terrarium/Environment/Materials/M_EnvironmentPigment');assert mat
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};report={'props':[],'foliage':[]}
for label,name,scale,yaw in [('Assembly_Cottage','Cottage',1.06,90),('Assembly_BlueShed','BlueShed',1.20,0),('Assembly_Tower','Tower',1.0,90),('Assembly_Lantern','Lantern',1.04,0),('Assembly_VegetableBed','VegetableBed',1.12,0),('Assembly_FlowerBorder','FlowerBorder',1.0,90)]:
    a=scene[label];sm=unreal.load_asset('/Game/Terrarium/Environment/Meshes/SM_Env_'+name);assert sm
    a.static_mesh_component.set_static_mesh(sm);a.static_mesh_component.set_material(0,mat)
    a.set_actor_scale3d(unreal.Vector(scale,scale,scale));a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    p=a.get_actor_location();p.z=564;a.set_actor_location(p,False,False)
    a.set_actor_label('Reference_'+name);a.set_folder_path('Reference/Courtyard')
    report['props'].append({'actor':a.get_actor_label(),'mesh':sm.get_path_name(),'scale':scale,'yaw':yaw,'ground_cm':564})
# Preserve every existing ground/path transform; new meshes keep their top pivot.
changes=[('SM_MeadowTile_v5_Detail2','MeadowTile'),('SM_MeadowTile_Edge_v6_Detail2','MeadowTile'),('SM_PathTile_v4_Detail','PathTile')]
for old,new in changes:
    mesh=unreal.load_asset('/Game/Terrarium/Environment/Meshes/SM_Env_'+new);assert mesh
    transforms=[];static_count=0
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh or c.static_mesh.get_name()!=old:continue
            if isinstance(c,unreal.FoliageInstancedStaticMeshComponent):
                transforms.extend(c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count()))
            else:c.set_static_mesh(mesh);c.set_material(0,mat);static_count+=1
    if transforms:
        ftname='FT_Env_'+old.removeprefix('SM_');ft=unreal.load_asset('/Game/Terrarium/Environment/Foliage/'+ftname) or at.create_asset(ftname,'/Game/Terrarium/Environment/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());assert ft
        ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[mat]);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
        oldft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+old.removeprefix('SM_').replace('_Detail2','_Detail'));assert oldft,old
        unreal.InstancedFoliageActor.remove_all_instances(world,oldft);unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
    report['foliage'].append({'old':old,'new':mesh.get_path_name(),'instances':len(transforms),'actors':static_count})
# Broad quiet spaces between tuft groups replace the former uniform fine scatter.
for old,ratio in [('SM_MeadowGrass_v2_Detail',.32),('SM_GroundPlants_v2_Detail',.44),('SM_MeadowFlowers_v2_Detail',.32)]:
    keep=[];count=0
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
            if not c.static_mesh or c.static_mesh.get_name()!=old:continue
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,world_space=True);p=t.translation;count+=1
                h=(math.sin(p.x*.017+p.y*.023)*43758.5453)%1
                cluster=math.sin(p.x/155)*math.cos(p.y/189)
                if h<ratio and cluster>-.35:keep.append(t)
    ft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+old.removeprefix('SM_'));assert ft
    unreal.InstancedFoliageActor.remove_all_instances(world,ft);unreal.InstancedFoliageActor.add_instances(world,ft,keep)
    report['foliage'].append({'mesh':old,'before':count,'after':len(keep)})
# Leaf masses in the supplied scene are smaller than the source asset showcase scale.
ft=unreal.load_asset('/Game/Terrarium/Environment/Foliage/FT_Env_Tree_v3_Detail');ts=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name()=='SM_Recon_HomesteadTree_R3':
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,world_space=True);t.scale3d=t.scale3d*.74;ts.append(t)
unreal.InstancedFoliageActor.remove_all_instances(world,ft);unreal.InstancedFoliageActor.add_instances(world,ft,ts)
# Match the bridge's shorter span without moving either established path route.
a=scene['Fidelity_PlankBridge_v4_001'];a.set_actor_scale3d(unreal.Vector(.9,1.27,1))
p=a.get_actor_location();px,py=ref.pixel(p.x,p.y,p.z);a.set_actor_location(unreal.Vector(*ref.world(px-2,py-3,p.z)),False,False)
assert levels.save_current_level();(out/'integration-stage2.json').write_text(json.dumps(report,indent=2))
unreal.log('REFERENCE_ENVIRONMENT_STAGE2_SAVED')
