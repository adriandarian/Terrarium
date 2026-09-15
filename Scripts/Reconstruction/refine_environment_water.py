"""World-aligned faceted river pigment and rebuilt bank/field geometry."""
import unreal,json,math
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadReference.' in str(levels.get_current_level())
assert not (out/'integration-stage3.json').exists()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();at=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary
mat=at.create_asset('M_ReferenceFacetedWater','/Game/Terrarium/Environment/Materials',unreal.Material,unreal.MaterialFactoryNew());assert mat
mat.set_editor_property('used_with_instanced_static_meshes',True)
p=lib.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-450,0)
c=lib.create_material_expression(mat,unreal.MaterialExpressionCustom,-150,0);c.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
pin=unreal.CustomInput();pin.set_editor_property('input_name','World');c.set_editor_property('inputs',[pin])
c.set_editor_property('code','''
float2 q=World.xy/float2(43,31);
float2 id=floor(q), f=frac(q);
float h=frac(sin(dot(id,float2(127.1,311.7)))*43758.5453);
float pool=sin(World.x*.0023+sin(World.y*.003))*sin(World.y*.0034)*.5+.5;
float3 col=lerp(float3(.014,.086,.092),float3(.037,.161,.145),pool);
float facet=step(f.x+f.y,1.0);
col*=lerp(.82,1.18,h)*lerp(.94,1.04,facet);
float glint=step(.90,h)*step(.62,f.y)*(1-step(.74,f.y))*step(.16,f.x)*(1-step(.72,f.x));
return lerp(col,float3(.115,.245,.222),glint*.7);
''')
assert lib.connect_material_expressions(p,'',c,'World');assert lib.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.72,170),(unreal.MaterialProperty.MP_SPECULAR,.12,280)]:
    n=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-150,y);n.set_editor_property('r',value);lib.connect_material_property(n,'',prop)
lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
report=[]
def swap(old,new,material,fit_xy=False,z_scale=1):
    oldmesh=unreal.load_asset('/Game/Terrarium/Meshes/'+old);mesh=unreal.load_asset(new);assert mesh
    oldb=oldmesh.get_bounds().box_extent;newb=mesh.get_bounds().box_extent
    ts=[]
    for a in actors.get_all_level_actors():
        for co in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
            if co.static_mesh and co.static_mesh.get_name()==old:
                for i in range(co.get_instance_count()):
                    t=co.get_instance_transform(i,world_space=True)
                    if fit_xy:t.scale3d=unreal.Vector(t.scale3d.x*oldb.x/newb.x,t.scale3d.y*oldb.y/newb.y,t.scale3d.z*z_scale)
                    ts.append(t)
    assert ts,old
    ftname='FT_Env_'+old.removeprefix('SM_');ft=at.create_asset(ftname,'/Game/Terrarium/Environment/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());assert ft
    ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[material]);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    oldft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+old.removeprefix('SM_'));assert oldft
    unreal.InstancedFoliageActor.remove_all_instances(world,oldft);unreal.InstancedFoliageActor.add_instances(world,ft,ts)
    report.append({'old':old,'mesh':new,'material':material.get_path_name(),'instances':len(ts)})
for n in ['WaterTile_v4_Detail','WaterShallow_v4_Detail','WaterDeep_v4_Detail']:swap('SM_'+n,'/Game/Terrarium/Meshes/SM_'+n,mat)
pigment=unreal.load_asset('/Game/Terrarium/Environment/Materials/M_EnvironmentPigment')
swap('SM_WheatPatch_v2_Detail','/Game/Terrarium/Reconstruction/Meshes/SM_Recon_WheatField_R3',pigment,True,1.65)
swap('SM_Reeds_Detail','/Game/Terrarium/Reconstruction/Meshes/SM_Recon_Riverbank_R3',pigment,True,.62)
assert levels.save_current_level();(out/'integration-stage3.json').write_text(json.dumps(report,indent=2))
unreal.log('REFERENCE_ENVIRONMENT_STAGE3_SAVED')
