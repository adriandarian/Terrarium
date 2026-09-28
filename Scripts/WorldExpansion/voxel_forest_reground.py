"""Coordinator-only native V5 contact update for two existing private forest types.

Identifies exact existing regional instances by their measured XY keys, snapshots
their actual transforms, traces only admitted V5 terrain, then persists updated Z
through each existing private FoliageType. Original pilot foliage is not targeted.
No mesh, FoliageType metadata, XY, quaternion, scale or count is changed.
"""
import unreal
import json
import hashlib
from pathlib import Path

ROOT=Path(unreal.Paths.project_dir()).resolve();assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);world=E.get_editor_world()
assert world.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion' and not E.get_game_world()
DOC=ROOT/'Docs/WorldExpansion/TerrainV5';DOC.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'SourceAssets/WorldExpansion/TerrainV5/manifest.json').read_text())
baseline=json.loads((ROOT/'SourceAssets/WorldExpansion/Terrain/manifest.json').read_text())
labels={'WX_'+r['name'] for r in manifest['assets']}
actors=A.get_all_level_actors();bylabel={a.get_actor_label():a for a in actors}
assert labels<=set(bylabel),'Admit all V5 terrain including apron before regrounding forest'
ignored=[a for a in actors if a.get_actor_label() not in labels]
request=ROOT/'Docs/WorldExpansion/forest-reground-request.json'
cfg=json.loads(request.read_text()) if request.exists() else {}
keys=cfg.get('groups',['BroadTree5m','ShrubGroundcover'])
assert set(keys)<={'BroadTree5m','ShrubGroundcover'}
def vec(p):return [p.x,p.y,p.z]
def xykey(p):return (round(p.x,1),round(p.y,1))
def invariant(t):
    q=t.rotation;p=t.translation;s=t.scale3d
    return [round(p.x,4),round(p.y,4)]+[round(v,7) for v in [q.x,q.y,q.z,q.w,s.x,s.y,s.z]]
def full(t):return invariant(t)+[round(t.translation.z,4)]
def asset_file(obj):return ROOT/'Content'/(obj.get_path_name().split('.')[0].removeprefix('/Game/')+'.uasset')
def all_components():
    return [c for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh and c.get_instance_count()]
def fingerprint_except(excluded):
    rows=[]
    for c in all_components():
        if c.get_path_name() in excluded:continue
        mesh=c.static_mesh.get_path_name()
        rows.extend(mesh+'|'+json.dumps(full(c.get_instance_transform(i,world_space=True)),separators=(',',':')) for i in range(c.get_instance_count()))
    return {'instances':len(rows),'sha256':hashlib.sha256('\n'.join(sorted(rows)).encode()).hexdigest()}
def find_instances(mesh,expected):
    found={};components=[]
    for c in all_components():
        if c.static_mesh!=mesh:continue
        local=[]
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,world_space=True);k=xykey(t.translation)
            if k in expected:local.append((k,t))
        if not local:continue
        assert len(local)==c.get_instance_count(),('Mixed component rejected',c.get_path_name())
        components.append(c)
        for k,t in local:
            assert k not in found,('Duplicate forest XY',k)
            found[k]=t
    assert set(found)==set(expected),('Existing private forest coordinates/count mismatch',len(found),len(expected))
    return found,components
plans=[];exclude=set();failures=[]
for key in keys:
    every=1 if key=='BroadTree5m' else 3
    expected={(round(r['location_m'][0]*100,1),round(r['location_m'][1]*100,1)) for r in baseline['forest_instances'][::every]}
    ftpath='/Game/Terrarium/WorldExpansion/Forest/FT_WX_'+key;ft=unreal.load_asset(ftpath);assert ft
    mesh=ft.get_editor_property('mesh');assert mesh
    transforms,components=find_instances(mesh,expected);exclude.update(c.get_path_name() for c in components)
    minimum=mesh.get_bounding_box().min.z
    invariants={k:invariant(t) for k,t in transforms.items()};updated=[];contacts=[]
    for k,t in transforms.items():
        p=t.translation
        result=unreal.SystemLibrary.line_trace_single(world_context_object=world,
            start=unreal.Vector(p.x,p.y,90000),end=unreal.Vector(p.x,p.y,-3000),
            trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,trace_complex=True,actors_to_ignore=ignored,
            draw_debug_type=unreal.DrawDebugTrace.NONE,ignore_self=False)
        hit=result if isinstance(result,unreal.HitResult) else next((r for r in (result or []) if isinstance(r,unreal.HitResult)),None)
        ht=hit.to_tuple() if hit else None
        label=ht[9].get_actor_label() if ht and ht[9] else ''
        if not ht or not bool(ht[0]) or label not in labels:
            failures.append({'group':key,'xy_cm':list(k),'hit_actor':label});continue
        ground=ht[5];before=p.z;newz=ground.z-minimum*t.scale3d.z-8
        # Preserve the current native quaternion and scale exactly.
        t.translation=unreal.Vector(p.x,p.y,newz)
        assert invariant(t)==invariants[k]
        updated.append(t);contacts.append({'xy_cm':list(k),'before_z_cm':before,'after_z_cm':newz,
            'ground_cm':vec(ground),'normal':vec(ht[7]),'ground_actor':label,'root_embed_cm':8})
    plans.append({'key':key,'ft':ft,'mesh':mesh,'expected':expected,'transforms':updated,'contacts':contacts,
                  'invariants':invariants,'ft_sha256':hashlib.sha256(asset_file(ft).read_bytes()).hexdigest(),
                  'mesh_sha256':hashlib.sha256(asset_file(mesh).read_bytes()).hexdigest(),
                  'before_components':[c.get_path_name() for c in components]})
if failures:
    (DOC/'forest-reground-failures.json').write_text(json.dumps({'failures':failures,'mutations_performed':False},indent=2))
    raise RuntimeError(f'{len(failures)} native ground traces failed; no foliage modified')
untouched_before=fingerprint_except(exclude);records=[];new_exclude=set()
for p in plans:
    assert len(p['transforms'])==len(p['expected'])
    unreal.InstancedFoliageActor.remove_all_instances(world,p['ft'])
    unreal.InstancedFoliageActor.add_instances(world,p['ft'],p['transforms'])
    actual,components=find_instances(p['mesh'],p['expected'])
    new_exclude.update(c.get_path_name() for c in components)
    after_by_xy={xykey(t.translation):t for t in p['transforms']}
    maxz=0
    for k,t in actual.items():
        current=invariant(t);prior=p['invariants'][k]
        assert all(abs(a-b)<(.03 if i<2 else .000002) for i,(a,b) in enumerate(zip(current,prior))),(p['key'],k,'XY rotation or scale changed beyond native float precision')
        maxz=max(maxz,abs(t.translation.z-after_by_xy[k].translation.z))
    assert maxz<.1,(p['key'],'Foliage persistence transform discrepancy',maxz)
    assert hashlib.sha256(asset_file(p['ft']).read_bytes()).hexdigest()==p['ft_sha256'],'FoliageType metadata changed'
    assert hashlib.sha256(asset_file(p['mesh']).read_bytes()).hexdigest()==p['mesh_sha256'],'Source mesh changed'
    records.append({'group':p['key'],'foliage_type':p['ft'].get_path_name(),'mesh':p['mesh'].get_path_name(),
        'count':len(actual),'components':[{'component':c.get_path_name(),'count':c.get_instance_count()} for c in components],
        'xy_rotation_scale_preserved':True,'ft_sha256':p['ft_sha256'],'mesh_sha256':p['mesh_sha256'],
        'ft_and_mesh_files_unchanged':True,'maximum_native_z_error_cm':maxz,'native_contacts':p['contacts']})
untouched_after=fingerprint_except(new_exclude);assert untouched_after==untouched_before,('Non-target foliage changed',untouched_before,untouched_after)
assert L.save_current_level()
receipt_path=DOC/'forest-reground.json'
prior_receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
combined={r['group']:r for r in prior_receipt.get('groups',[])}
combined.update({r['group']:r for r in records})
receipt={'groups':list(combined.values()),'native_traces':sum(r['count'] for r in combined.values()),
         'only_private_existing_forest_types_updated':True,'count_xy_rotation_scale_preserved':True,
         'non_target_foliage_before':untouched_before,'non_target_foliage_after':untouched_after,
         'map_saved':True,'reopen_validation':'Coordinator must reopen and inspect receipt component counts/contacts'}
receipt_path.write_text(json.dumps(receipt,indent=2))
print(json.dumps({'updated':receipt['native_traces'],'groups':keys,'non_target_foliage_unchanged':True,'max_z_error_cm':max(r['maximum_native_z_error_cm'] for r in records)}))
