"""Apply the calibrated river color only to this level's water components."""
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
mat=unreal.load_asset('/Game/Terrarium/Materials/M_QuietRiverPalette');assert mat
count=0
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(a,unreal.InstancedFoliageActor):continue
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name()=='SM_WaterTile_v3' and c.get_instance_count():
            c.set_material(0,mat);count+=c.get_instance_count()
assert count==190
assert levels.save_current_level()
