"""Coordinator-only: pilot-copy the fourteen retained environment variants.

Keep LOD0, materials, collision, transforms and actor placements. Generate real
lower LODs on substantial meshes; small stone meshes remain single LOD. Shared
mesh/FoliageType/material assets are never saved or edited by this operation.
"""
import unreal,json,hashlib,struct
from collections import Counter
from pathlib import Path

R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
D=R/'Docs/HomesteadPilot/RemainingEnvironment'
DEST='/Game/Terrarium/HomesteadPilot/RemainingEnvironment/Retained'
LEVEL='/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
S=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
world=E.get_editor_world();assert world.get_path_name().split('.')[0]==LEVEL and not E.get_game_world()
assert not (D/'inherited-lod-validation.json').exists(),'Already admitted'
plan=json.loads((D/'inherited-lod-plan.json').read_text())['meshes']
old_paths={r['mesh'] for r in plan};mapping={};protected={};rows=[]
build_progress_path=D/'inherited-lod-build-progress.json'
completed_builds={r['mesh'].split('.')[0]:r for r in json.loads(build_progress_path.read_text())['meshes']} if build_progress_path.exists() else {}

def asset_file(path):return R/'Content'/(path.split('.')[0].removeprefix('/Game/')+'.uasset')
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation
    return [round(v,5) for v in (*vec(t.translation),*vec(t.scale3d),q.x,q.y,q.z,q.w)]
def code(t):return json.dumps(serial(t))
def instances(mesh):
    return [c.get_instance_transform(i,world_space=True) for a in A.get_all_level_actors()
            for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent)
            if c.static_mesh==mesh for i in range(c.get_instance_count())]
def snapshot():
    result=[];grass=0;counts=Counter()
    inverse={v:k for k,v in mapping.items()}
    for a in A.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            path=inverse.get(c.static_mesh.get_path_name(),c.static_mesh.get_path_name())
            ts=[c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count())] if isinstance(c,unreal.InstancedStaticMeshComponent) else [c.get_world_transform()]
            mats=[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]
            if 'GrassTerrain' in path:grass+=len(ts)
            counts[path]+=len(ts)
            state=[path,mats,str(c.get_collision_enabled()),str(c.get_collision_profile_name()),c.get_editor_property('visible'),c.get_editor_property('hidden_in_game')]
            result.extend(json.dumps([state,serial(t)],sort_keys=True) for t in ts)
    return {'hash':hashlib.sha256('\n'.join(sorted(result)).encode()).hexdigest(),'grass':grass,'counts':dict(counts)}
def contract(mesh):
    b=mesh.get_bounding_box();body=mesh.get_editor_property('body_setup')
    return {'lod0_triangles':mesh.get_num_triangles(0),'lod0_vertices':mesh.get_num_vertices(0),'lod0_sections':mesh.get_num_sections(0),
            'bounds':[vec(b.min),vec(b.max)],'materials':[(str(s.get_editor_property('material_slot_name')),s.get_editor_property('material_interface').get_path_name() if s.get_editor_property('material_interface') else None) for s in mesh.static_materials],
            'collision_flag':str(body.get_editor_property('collision_trace_flag')) if body else None,
            'collision_lod':mesh.get_editor_property('lod_for_collision'),
            'simple_collision_count':S.get_simple_collision_count(mesh),'nanite':S.get_nanite_settings(mesh).get_editor_property('enabled')}

def lod0_geometry_hash(mesh):
    """Fingerprint actual render LOD0 positions/connectivity independent of bounds.

    StaticMesh bounds include generated LODs and can expand slightly despite an
    unchanged LOD0. Canonical cyclic ordering tolerates triangle index/order
    changes while preserving exact floating point positions and face winding.
    """
    dynamic=unreal.DynamicMesh()
    requested=unreal.GeometryScriptMeshReadLOD()
    requested.set_editor_property('lod_type',unreal.GeometryScriptLODType.RENDER_DATA)
    requested.set_editor_property('lod_index',0)
    _,outcome=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dynamic,unreal.GeometryScriptCopyMeshFromAssetOptions(),requested)
    assert outcome==unreal.GeometryScriptOutcomePins.SUCCESS
    assert dynamic.get_triangle_count()==mesh.get_num_triangles(0)
    triangles=[]
    for i in range(dynamic.get_triangle_count()):
        valid,a,b,c=dynamic.get_triangle_positions(i);assert valid
        points=[tuple(vec(v)) for v in (a,b,c)]
        canonical=min(tuple(points),tuple(points[1:]+points[:1]),tuple(points[2:]+points[:2]))
        triangles.append(struct.pack('<9d',*(v for p in canonical for v in p)))
    return hashlib.sha256(b''.join(sorted(triangles))).hexdigest()

def compare_contract(source,duplicate,label,enforce_bounds=True):
    non_bounds=lambda d:{k:v for k,v in d.items() if k!='bounds'}
    assert non_bounds(source)==non_bounds(duplicate),('LOD0/material/collision contract changed',label,source,duplicate)
    differences=[abs(a-b) for sa,da in zip(source['bounds'],duplicate['bounds']) for a,b in zip(sa,da)]
    delta=max(differences)
    characteristic_size=max(hi-lo for lo,hi in zip(*source['bounds']))
    # LOD screen thresholds apply to the whole projected object. Use a 1% of
    # longest-axis bound budget, not a fixed world-unit value or thin slab height.
    # This bounds envelope drift at reduced LODs only; LOD0 positions remain exact.
    limit=characteristic_size*.01
    if enforce_bounds:assert delta<=limit,('Aggregate all-LOD bounds exceed 1% of original longest dimension',label,delta,limit)
    return {'maximum_cm':delta,'limit_cm':limit,'fraction_of_longest_dimension':delta/characteristic_size,
            'within_budget':delta<=limit,
            'policy':'Aggregate reduced-LOD envelope only; exact render LOD0 geometry hash separately required'}

before=snapshot();assert before['grass']==5841
for p in plan:assert before['counts'].get(p['mesh'])==p['expected_instances'],p
baseline=R/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap';baseline_hash=hashlib.sha256(baseline.read_bytes()).hexdigest()
registry=unreal.AssetRegistryHelpers.get_asset_registry();types=[]
for data in registry.get_assets_by_path('/Game/Terrarium',recursive=True):
    if not str(data.asset_name).startswith('FT_'):continue
    ft=data.get_asset()
    if isinstance(ft,unreal.FoliageType_InstancedStaticMesh) and ft.get_editor_property('mesh') and ft.get_editor_property('mesh').get_path_name() in old_paths:types.append(ft)

# Build and validate every duplicate before any scene migration.
for p in plan:
    old=unreal.load_asset(p['mesh']);assert old
    old_contract=contract(old);assert old_contract['lod0_triangles']==p['triangles'][0]
    old_geometry=lod0_geometry_hash(old)
    protected[p['mesh']]=hashlib.sha256(asset_file(p['mesh']).read_bytes()).hexdigest()
    target=DEST+'/Meshes/'+old.get_name()
    new=unreal.load_asset(target)
    if new:
        known_partial=target in (DEST+'/Meshes/SM_Env_FlowerBorder',DEST+'/Meshes/SM_Blender_TrailPatch',DEST+'/Meshes/SM_MeadowFlowers_v2_Detail')
        assert known_partial or target in completed_builds,'Partial admission needs inspection: '+target
        assert not (D/'inherited-lod-migration-progress.json').exists(),'Cannot resume after scene migration'
        if target in completed_builds:
            saved=completed_builds[target]
            assert saved['source']==p['mesh'] and saved['lod0_render_triangle_positions_sha256']==old_geometry
        compare_contract(old_contract,contract(new),target,enforce_bounds=target in completed_builds)
        assert lod0_geometry_hash(new)==old_geometry,'Partial asset LOD0 geometry differs'
    else:
        new=unreal.EditorAssetLibrary.duplicate_asset(p['mesh'],target);assert new
    attempts=[]
    if target in completed_builds:
        # Completed and independently checked duplicates need no repeated rebuild.
        saved=completed_builds[target]
        triangles=[new.get_num_triangles(i) for i in range(S.get_lod_count(new))]
        assert triangles==saved['triangles']
        sizes=list(S.get_lod_screen_sizes(new));policy=saved['policy']
        attempts=saved.get('reduction_attempts',[])
    elif old_contract['lod0_triangles']>=512:
        thin=any(t in old.get_name() for t in ('Grass','Plants','Flowers','Bush','Tree','Riverbank','Fringe','FlowerBorder'))
        sizes=[1.,.18,.06] if thin else [1.,.24,.08]
        candidates=([1.,.75,.50] if thin else [1.,.60,.32],[1.,.85,.70],[1.,.94,.88])
        accepted=False
        for fractions in candidates:
            options=unreal.StaticMeshReductionOptions();options.set_editor_property('auto_compute_lod_screen_size',False)
            options.set_editor_property('reduction_settings',[unreal.StaticMeshReductionSettings(percent_triangles=f,screen_size=s) for f,s in zip(fractions,sizes)])
            assert S.set_lods(new,options)==3
            assert S.set_lod_screen_sizes(new,sizes)
            triangles=[new.get_num_triangles(i) for i in range(3)]
            review=compare_contract(old_contract,contract(new),target,enforce_bounds=False)
            reducing=triangles[0]>triangles[1]>triangles[2]>0
            attempts.append({'fractions':fractions,'triangles':triangles,'aggregate_bounds_review':review,'actually_reduces':reducing})
            if reducing and review['within_budget']:
                accepted=True
                policy='Generated lower LODs within 1% aggregate envelope budget; original LOD0 retained'
                break
        if not accepted:
            # Keep the reviewed near mesh when every conservative simplification
            # exceeds the fixed envelope budget. Never relax it per asset.
            S.remove_lods(new)
            assert S.get_lod_count(new)==1
            triangles=[new.get_num_triangles(0)];sizes=list(S.get_lod_screen_sizes(new))
            policy='Single-LOD exemption: generated lower LODs exceeded fixed 1% envelope budget or did not reduce geometry'
    else:
        triangles=[new.get_num_triangles(i) for i in range(S.get_lod_count(new))]
        sizes=list(S.get_lod_screen_sizes(new));policy='Under 512 triangles; retain minimal original mesh without redundant LODs'
    new_contract=contract(new)
    bounds_review=compare_contract(old_contract,new_contract,target)
    assert lod0_geometry_hash(new)==old_geometry,('Actual render LOD0 triangle positions changed',target)
    assert unreal.EditorAssetLibrary.save_loaded_asset(new)
    mapping[p['mesh']]=new.get_path_name()
    rows.append({'source':p['mesh'],'mesh':new.get_path_name(),'triangles':triangles,'screen_sizes':sizes,'policy':policy,
                 'source_contract':old_contract,'contract':new_contract,'aggregate_bounds_review':bounds_review,
                 'lod0_render_triangle_positions_sha256':old_geometry,'reduction_attempts':attempts,'instances':p['expected_instances']})
    (D/'inherited-lod-build-progress.json').write_text(json.dumps({'meshes':rows},indent=2))

groups=[];removed_groups=[];static_changes=[]
try:
    for row in rows:
        old=unreal.load_asset(row['source']);new=unreal.load_asset(row['mesh'])
        original=Counter(code(t) for t in instances(old))
        for old_ft in [ft for ft in types if ft.get_editor_property('mesh')==old]:
            path=old_ft.get_path_name();protected[path]=hashlib.sha256(asset_file(path).read_bytes()).hexdigest()
            pending=instances(old);unreal.InstancedFoliageActor.remove_all_instances(world,old_ft)
            remaining=Counter(code(t) for t in instances(old));removed=[]
            for t in pending:
                k=code(t)
                if remaining[k]:remaining[k]-=1
                else:removed.append(t)
            assert not +remaining
            if not removed:continue
            removed_groups.append((old_ft,removed))
            suffix=hashlib.sha256(path.encode()).hexdigest()[:8]
            target=DEST+'/Foliage/FT_HP_'+old.get_name()+'_'+suffix
            assert not unreal.load_asset(target),'Partial foliage admission needs inspection'
            ft=unreal.EditorAssetLibrary.duplicate_asset(path,target);assert ft
            ft.set_editor_property('mesh',new)
            # All type materials, collision, culling and placement settings persist.
            assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
            groups.append({'source':path,'type':ft.get_path_name(),'mesh':new.get_path_name(),'count':len(removed)})
            unreal.InstancedFoliageActor.add_instances(world,ft,removed)
        assert not instances(old)
        assert Counter(code(t) for t in instances(new))==original,'Foliage transform change'
        for a in A.get_all_level_actors():
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                if c.static_mesh!=old:continue
                assert not isinstance(c,unreal.FoliageInstancedStaticMeshComponent)
                static_changes.append((c,old))
                c.set_static_mesh(new)
        (D/'inherited-lod-migration-progress.json').write_text(json.dumps({'groups':groups,'static_components':[c.get_path_name() for c,o in static_changes]},indent=2))
    assert snapshot()==before,'Geometry admission changed transforms/materials/collision/visibility'
    assert L.save_current_level()
except Exception:
    for c,old in static_changes:c.set_static_mesh(old)
    for g in groups:unreal.InstancedFoliageActor.remove_all_instances(world,unreal.load_asset(g['type']))
    for ft,ts in removed_groups:unreal.InstancedFoliageActor.add_instances(world,ft,ts)
    assert snapshot()==before
    assert L.save_current_level()
    raise

assert L.load_level(LEVEL);world=E.get_editor_world()
assert snapshot()==before,'Saved/reopened content state changed'
for row in rows:
    mesh=unreal.load_asset(row['mesh']);assert contract(mesh)==row['contract']
    assert lod0_geometry_hash(mesh)==row['lod0_render_triangle_positions_sha256']
    assert [mesh.get_num_triangles(i) for i in range(S.get_lod_count(mesh))]==row['triangles']
    assert not instances(unreal.load_asset(row['source']))
for path,digest in protected.items():assert hashlib.sha256(asset_file(path).read_bytes()).hexdigest()==digest
assert hashlib.sha256(baseline.read_bytes()).hexdigest()==baseline_hash
for g in groups:assert unreal.load_asset(g['type']).get_editor_property('mesh').get_path_name()==g['mesh']
(D/'inherited-lod-validation.json').write_text(json.dumps({'meshes':rows,'foliage_groups':groups,'saved_reopened':True,
    'instances':sum(r['instances'] for r in rows),'shared_files_unchanged':True,'baseline_unchanged':True,
    'state_hash_preserved':before['hash'],'grass':5841,'lod0_material_collision_contract_preserved':True,
    'scope':'Actual imported lower LOD triangle counts and serialized persistence. Automatic transition visual acceptance remains separate.'},indent=2))
unreal.log('RETAINED_ENVIRONMENT_ADMITTED: 14 meshes, 1753 instances, original LOD0/materials/collision retained')
