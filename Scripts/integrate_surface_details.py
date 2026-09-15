"""Replace ground/water foliage meshes at identical saved world transforms."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());p=root/'Docs/Fidelity/Surfaces';p.mkdir(exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
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
def numeric(t):
    p=t.translation;r=t.rotation;s=t.scale3d
    return [p.x,p.y,p.z,r.x,r.y,r.z,r.w,s.x,s.y,s.z]
changes=[]
layout=json.loads((root/'Docs/Fidelity/Details/current-layout.json').read_text())
for old,new,count in [('MeadowTile_v2','MeadowTile_v3',3718),('WaterTile_v2','WaterTile_v3',190)]:
    report=json.loads((root/'Docs/Phase1/Validation'/('SM_'+new+'.json')).read_text())
    assert report['saved_normal_errors']==0 and report['visual_review'].startswith('passed')
    original=instances('SM_'+old)
    assert len(original)==count and not instances('SM_'+new)
    before=sorted(numeric(t) for t in original)
    path='/Game/Terrarium/Foliage/FT_'+new
    ft=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset('FT_'+new,'/Game/Terrarium/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
    ft.set_editor_property('mesh',unreal.load_asset('/Game/Terrarium/Meshes/SM_'+new))
    assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.add_instances(world,ft,original)
    current=instances('SM_'+new)
    assert len(current)==count
    after=sorted(numeric(t) for t in current)
    deviation=max(abs(a-b) for x,y in zip(before,after) for a,b in zip(x,y))
    assert deviation<.001,deviation
    unreal.InstancedFoliageActor.remove_all_instances(world,unreal.load_asset('/Game/Terrarium/Foliage/FT_'+old))
    assert not instances('SM_'+old)
    layout['counts'][new]=layout['counts'].pop(old)
    changes.append({'old_mesh':old,'new_mesh':new,'instances':count,'max_transform_component_deviation':deviation,'asset_refinement_pass':3})
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
layout['asset_detail_revision']='ground and water pass 3 following five asset detail updates'
(root/'Docs/Fidelity/Details/current-layout.json').write_text(json.dumps(layout,indent=2))
(p/'integration.json').write_text(json.dumps({'changes':changes,'placement_transforms_preserved':True,'camera_and_lighting_unchanged':True},indent=2))
