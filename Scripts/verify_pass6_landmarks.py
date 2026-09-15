"""Verify revised hero placements and the level-specific water material."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
def bymesh(name):
    found=[a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==name]
    assert len(found)==1,(name,len(found));return found[0]
bridge=bymesh('SM_PlankBridge_v2');center,extent=bridge.get_actor_bounds(False)
assert center.z-extent.z<0
scale=bridge.get_actor_scale3d()
assert abs(scale.x-.9)<.0001 and abs(scale.y-1.4)<.0001
assert abs(bridge.get_actor_rotation().yaw+4)<.0001
traveler=bymesh('SM_Traveler');cottage=bymesh('SM_Cottage_v4')
water=[]
for a in actors:
    if isinstance(a,unreal.InstancedFoliageActor):
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if c.static_mesh and c.static_mesh.get_name()=='SM_WaterTile_v3' and c.get_instance_count():
                assert c.get_material(0).get_name()=='M_QuietRiverPalette'
                water.append(c.get_instance_count())
assert sum(water)==190
root=Path(unreal.Paths.project_dir())
assert unreal.EditorAssetLibrary.does_asset_exist('/Game/Terrarium/Maps/HomesteadBeforePass6')
(root/'Docs/Fidelity/Pass6/landmark-validation.json').write_text(json.dumps({'bridge_scale':[scale.x,scale.y,scale.z],'bridge_yaw':bridge.get_actor_rotation().yaw,'bridge_pile_bottom_z':center.z-extent.z,'water_z':0,'water_instances_with_calibrated_material':sum(water),'traveler_actor':traveler.get_actor_label(),'cottage_actor':cottage.get_actor_label(),'previous_scene_snapshot':'/Game/Terrarium/Maps/HomesteadBeforePass6'},indent=2))
