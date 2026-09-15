"""Upgrade wheat geometry while preserving all forty existing instance transforms."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
root=Path(unreal.Paths.project_dir())
report=json.loads((root/'Docs/Phase1/Validation/SM_WheatPatch_v2.json').read_text())
assert report['saved_normal_errors']==0 and report['visual_review'].startswith('passed')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

def instances(name):
    result=[]
    for a in actors.get_all_level_actors():
        if not isinstance(a,unreal.InstancedFoliageActor):continue
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if c.static_mesh and c.static_mesh.get_name()==name:
                for i in range(c.get_instance_count()):
                    t=c.get_instance_transform(i,world_space=True)
                    if isinstance(t,tuple):t=next(x for x in t if isinstance(x,unreal.Transform))
                    assert isinstance(t,unreal.Transform)
                    result.append(t)
    return result

old=instances('SM_WheatPatch');new=instances('SM_WheatPatch_v2')
assert len(old) in [0,40] and len(new) in [0,40]
assert old or new
path='/Game/Terrarium/Foliage/FT_WheatPatch_v2'
ft=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset('FT_WheatPatch_v2','/Game/Terrarium/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
ft.set_editor_property('mesh',unreal.load_asset('/Game/Terrarium/Meshes/SM_WheatPatch_v2'))
assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
if not new:
    unreal.InstancedFoliageActor.add_instances(world,ft,old)
    assert len(instances('SM_WheatPatch_v2'))==40
if old:
    unreal.InstancedFoliageActor.remove_all_instances(world,unreal.load_asset('/Game/Terrarium/Foliage/FT_WheatPatch'))
assert len(instances('SM_WheatPatch'))==0
assert len(instances('SM_WheatPatch_v2'))==40
assert levels.save_current_level()
p=root/'Docs/Fidelity/Details'
layout=json.loads((p/'current-layout.json').read_text())
layout['counts']['WheatPatch_v2']=layout['counts'].pop('WheatPatch',40)
layout['asset_detail_revision']='shed, bridge and wheat pass 2; existing placement transforms retained'
(p/'current-layout.json').write_text(json.dumps(layout,indent=2))
(p/'wheat-integration.json').write_text(json.dumps({'old_instances_remaining':0,'new_instances':40,'placement_source':'existing saved world transforms','earlier_foliage_type_unchanged':'/Game/Terrarium/Foliage/FT_WheatPatch','asset_detail_pass':2},indent=2))
