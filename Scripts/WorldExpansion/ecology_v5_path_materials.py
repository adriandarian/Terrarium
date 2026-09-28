"""Apply imagegen gravel to ONLY the two private region paving foliage types.

Preserve authored cobble/stone detail slots and every native instance transform.
No original home mesh/material/foliage type is edited. Coordinator editor only.
"""
import json, hashlib
from collections import Counter
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve();assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not E.get_game_world();world=E.get_editor_world();assert world.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
path_material=unreal.load_asset('/Game/Terrarium/WorldExpansion/TerrainV5/Materials/M_VoxelPath');assert path_material
types=['/Game/Terrarium/WorldExpansion/SettlementFoliage/FT_WX_Settlement_WornPath2m',
       '/Game/Terrarium/WorldExpansion/DressingFoliage/FT_WX_Dressing_WornPath2m']

def components(mesh):
    return [c for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh]
def transforms(mesh):
    return [c.get_instance_transform(i,world_space=True) for c in components(mesh) for i in range(c.get_instance_count())]
def code(t):
    q=t.rotation
    return tuple(round(float(v),6) for v in [t.translation.x,t.translation.y,t.translation.z,t.scale3d.x,t.scale3d.y,t.scale3d.z,q.x,q.y,q.z,q.w])
records=[]
for path in types:
    ft=unreal.load_asset(path);assert isinstance(ft,unreal.FoliageType_InstancedStaticMesh),path
    mesh=ft.get_editor_property('mesh');assert mesh and mesh.get_name()=='SM_WornPath2m'
    source_file=ROOT/'Content'/(mesh.get_path_name().split('.')[0].removeprefix('/Game/')+'.uasset')
    source_hash=hashlib.sha256(source_file.read_bytes()).hexdigest()
    before=transforms(mesh);before_codes=Counter(code(t) for t in before)
    unreal.InstancedFoliageActor.remove_all_instances(world,ft)
    remaining=Counter(code(t) for t in transforms(mesh));removed=[]
    for t in before:
        key=code(t)
        if remaining[key]:remaining[key]-=1
        else:removed.append(t)
    assert not +remaining,'Removing one type changed unrelated transforms'
    assert removed,(path,'Expected region paving instances')
    # Slot0 is native M_PilotLandscape_Path. Slots1/2 are modeled pale/dark
    # stones; retain those exact source shaders instead of repainting the mesh.
    overrides=[s.material_interface for s in mesh.static_materials];assert len(overrides)==3
    overrides[0]=path_material
    ft.set_editor_property('override_materials',overrides)
    assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    before_components={c.get_path_name():c.get_instance_count() for c in components(mesh)}
    unreal.InstancedFoliageActor.add_instances(world,ft,removed)
    assert Counter(code(t) for t in transforms(mesh))==before_codes,'Native paving transforms changed'
    effective=[]
    for c in components(mesh):
        delta=c.get_instance_count()-before_components.get(c.get_path_name(),0)
        if delta:
            assert delta>0 and c.get_material(0)==path_material
            effective.append({'component':c.get_path_name(),'count':delta,
                'effective_materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]})
    assert sum(r['count'] for r in effective)==len(removed)
    assert hashlib.sha256(source_file.read_bytes()).hexdigest()==source_hash
    records.append({'foliage_type':ft.get_path_name(),'mesh':mesh.get_path_name(),'count':len(removed),
        'effective_components':effective,'transforms_preserved':True,'source_mesh_sha256':source_hash,'source_mesh_unchanged':True,
        'override_materials':[m.get_path_name() if m else None for m in overrides]})
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(ROOT/'Docs/WorldExpansion/ecology-v5-path-materials.json').write_text(json.dumps({'groups':records,
    'material':path_material.get_path_name(),'source_home_unchanged':True,'policy':'Only region private FT slot0 overrides; retained modeled stone slots'},indent=2))
print(json.dumps({'groups':len(records),'paving_instances':sum(r['count'] for r in records)}))
