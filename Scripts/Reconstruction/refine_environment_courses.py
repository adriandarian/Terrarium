"""Integrate smaller stone courses and sparse readable wheat stalks."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadReference.' in str(levels.get_current_level())
assert not (out/'integration-stage5.json').exists()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();report=[]
jobs=[('SM_VoxelCliffStepped_'+v,'FT_Env_CliffColumn_v6'+v+'_Detail','SM_Env_Cliff_'+v) for v in 'ABC']
jobs.append(('SM_Recon_WheatField_R3','FT_Env_WheatPatch_v2_Detail','SM_Env_WheatPatch'))
for old,ftname,new in jobs:
    ft=unreal.load_asset('/Game/Terrarium/Environment/Foliage/'+ftname);assert ft
    mesh=unreal.load_asset('/Game/Terrarium/Environment/Meshes/'+new);assert mesh
    original=ft.get_editor_property('mesh');ob=original.get_bounds().box_extent;nb=mesh.get_bounds().box_extent
    ts=[]
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
            if c.static_mesh and c.static_mesh.get_name()==old:
                for i in range(c.get_instance_count()):
                    t=c.get_instance_transform(i,world_space=True)
                    if 'Wheat' in old:t.scale3d=unreal.Vector(t.scale3d.x*ob.x/nb.x,t.scale3d.y*ob.y/nb.y,t.scale3d.z/1.65)
                    ts.append(t)
    assert ts,old
    unreal.InstancedFoliageActor.remove_all_instances(world,ft);ft.set_editor_property('mesh',mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.add_instances(world,ft,ts)
    report.append({'old':old,'new':new,'instances':len(ts)})
assert levels.save_current_level();(out/'integration-stage5.json').write_text(json.dumps(report,indent=2))
