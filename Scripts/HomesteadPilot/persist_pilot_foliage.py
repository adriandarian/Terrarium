"""Persist pilot foliage through pilot-owned FoliageTypes, then save/reopen/verify.

The root's reopened-site-details.json confirmed that converted transforms survived
while component mesh overrides reverted to the shared FoliageType mesh. Therefore
this migration copies CURRENT transforms unchanged. It never rescales them.
"""
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
OUT = ROOT / 'Docs/HomesteadPilot/Runtime'
LEVEL = '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
DEST = '/Game/Terrarium/HomesteadPilot/Landscape/Foliage'
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world = editor.get_editor_world()
assert world.get_path_name().split('.')[0] == LEVEL
assert not editor.get_game_world(), 'Stop PIE before migrating foliage'
assert (ROOT / 'Docs/HomesteadPilot/reopened-site-details.json').exists(), 'Reopen-transform diagnosis required'
receipt_path = OUT / 'foliage-migration-receipt.json'
assert not receipt_path.exists(), 'Migration already completed; use its saved/reopened receipt'
specs = [
    ('CliffColumn', 'FineCliffColumn1m', 2076, 'BlockAll'),
    ('MeadowShrub', 'ShrubGroundcover', 618, 'NoCollision'),
    ('HomesteadTree', 'BroadTree5m', 14, 'BlockAll'),
    ('WheatPatch', 'WheatPatch2m', 40, 'NoCollision'),
]

def serial(t):
    p, s, q = t.translation, t.scale3d, t.rotation
    return {'translation': [p.x,p.y,p.z], 'scale': [s.x,s.y,s.z], 'rotation_xyzw': [q.x,q.y,q.z,q.w]}

def code(t):
    return json.dumps(serial(t), sort_keys=True)

def instances(mesh):
    return [c.get_instance_transform(i, world_space=True)
            for a in actors.get_all_level_actors()
            for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent)
            if c.get_editor_property('static_mesh') == mesh
            for i in range(c.get_instance_count())]

def components(mesh):
    return [{'component': c.get_path_name(), 'count': c.get_instance_count(),
             'collision_enabled': str(c.get_collision_enabled()),
             'transforms': [serial(c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count())]}
            for a in actors.get_all_level_actors()
            for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent)
            if c.get_editor_property('static_mesh') == mesh and c.get_instance_count()]

def verify_transforms(expected, actual):
    """Unordered matching with float-storage tolerances and equivalent quaternion signs."""
    assert len(expected) == len(actual), (len(expected), len(actual))
    bins = defaultdict(set)
    cell = lambda p: tuple(math.floor(v/10.) for v in p)
    for index,row in enumerate(expected):
        bins[cell(row['translation'])].add(index)
    maximum = {'translation_cm':0., 'scale':0., 'quaternion':0.}
    for row in actual:
        base = cell(row['translation'])
        found = None
        for offset in itertools.product((-1,0,1), repeat=3):
            key = tuple(a+b for a,b in zip(base,offset))
            for index in bins.get(key, ()):
                wanted = expected[index]
                errors = [max(abs(a-b) for a,b in zip(row['translation'],wanted['translation'])),
                          max(abs(a-b) for a,b in zip(row['scale'],wanted['scale'])),
                          min(max(abs(a-b) for a,b in zip(row['rotation_xyzw'],wanted['rotation_xyzw'])),
                              max(abs(a+b) for a,b in zip(row['rotation_xyzw'],wanted['rotation_xyzw'])))]
                if errors[0] <= .02 and errors[1] <= .00002 and errors[2] <= .00002:
                    found = (key,index,errors)
                    break
            if found:
                break
        assert found, ('An instance transform changed beyond storage tolerance', row)
        key,index,errors = found
        bins[key].remove(index)
        for name,value in zip(maximum,errors):
            maximum[name] = max(maximum[name],value)
    assert not any(bins.values())
    return maximum

def asset_file(asset):
    return ROOT/'Content'/(asset.get_path_name().split('.')[0].removeprefix('/Game/')+'.uasset')

registry = unreal.AssetRegistryHelpers.get_asset_registry()
type_assets = []
for data in registry.get_assets_by_path('/Game/Terrarium', recursive=True):
    # All authored foliage assets in this project use the FT_ prefix. This avoids
    # loading every mesh and texture merely to find their associated foliage type.
    if not str(data.asset_name).startswith('FT_'):
        continue
    obj = data.get_asset()
    if isinstance(obj, unreal.FoliageType_InstancedStaticMesh) and not obj.get_path_name().startswith(DEST+'/'):
        type_assets.append(obj)

jobs = []
before = {'level':LEVEL, 'transform_policy':'Copy current reopened transforms unchanged; no scale or position conversion',
          'diagnosis':'Docs/HomesteadPilot/reopened-site-details.json', 'families':[]}
for old_key,new_key,count,collision in specs:
    old_mesh = unreal.load_asset('/Game/Terrarium/Blender/'+old_key+'/SM_Blender_'+old_key)
    mesh = unreal.load_asset('/Game/Terrarium/HomesteadPilot/Landscape/Meshes/SM_'+new_key)
    assert old_mesh and mesh
    initial = instances(old_mesh)
    assert len(initial) == count, (old_key,len(initial),count)
    assert not instances(mesh), ('Existing pilot foliage would duplicate instances',new_key)
    old_types = sorted([ft for ft in type_assets if ft.get_editor_property('mesh')==old_mesh],key=lambda ft:ft.get_path_name())
    assert old_types, old_key
    source_hashes = {ft.get_path_name():hashlib.sha256(asset_file(ft).read_bytes()).hexdigest() for ft in old_types}
    row = {'family':new_key, 'old_mesh':old_mesh.get_path_name(), 'new_mesh':mesh.get_path_name(),
           'count':count,'collision':collision,'source_foliage_types':list(source_hashes),
           'source_foliage_type_sha256':source_hashes,'components':components(old_mesh)}
    before['families'].append(row)
    jobs.append((row,old_mesh,mesh,old_types,initial))
(OUT/'foliage-migration-before.json').write_text(json.dumps(before,indent=2),encoding='utf-8')

groups = []
removed_groups = []
unused = []
try:
    for row,old_mesh,mesh,old_types,initial in jobs:
        for old_ft in old_types:
            pending = instances(old_mesh)
            unreal.InstancedFoliageActor.remove_all_instances(world,old_ft)
            remaining = Counter(code(t) for t in instances(old_mesh))
            removed = []
            for t in pending:
                key = code(t)
                if remaining[key]:
                    remaining[key] -= 1
                else:
                    removed.append(t)
            assert not +remaining, 'Removing one type unexpectedly transformed other foliage'
            if not removed:
                unused.append(old_ft.get_path_name())
                continue
            removed_groups.append((old_ft,removed))
            suffix = hashlib.sha256(old_ft.get_path_name().encode()).hexdigest()[:8]
            destination = DEST+'/FT_HP_'+row['family']+'_'+suffix
            ft = unreal.load_asset(destination)
            if not ft:
                ft = unreal.EditorAssetLibrary.duplicate_asset(old_ft.get_path_name(),destination)
            assert isinstance(ft,unreal.FoliageType_InstancedStaticMesh)
            ft.set_editor_property('mesh',mesh)
            ft.set_editor_property('override_materials',[])
            body = ft.get_editor_property('body_instance')
            body.set_editor_property('collision_profile_name',row['collision'])
            body.set_editor_property('collision_enabled',unreal.CollisionEnabled.NO_COLLISION if row['collision']=='NoCollision' else unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            ft.set_editor_property('body_instance',body)
            assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
            group = {'family':row['family'],'old_foliage_type':old_ft.get_path_name(),
                     'new_foliage_type':ft.get_path_name(),'new_mesh':mesh.get_path_name(),
                     'collision':row['collision'],'count':len(removed),
                     'transforms_before':[serial(t) for t in removed]}
            groups.append(group)
            (OUT/'foliage-migration-progress.json').write_text(json.dumps({'groups':groups},indent=2),encoding='utf-8')
            existing_count = len(instances(mesh))
            unreal.InstancedFoliageActor.add_instances(world,ft,removed)
            assert len(instances(mesh)) == existing_count+len(removed)
        assert not instances(old_mesh), ('An old foliage type remains',row['family'])
        verify_transforms([serial(t) for t in initial],[serial(t) for t in instances(mesh)])
    assert levels.save_current_level()
except Exception:
    # Restore the captured source memberships in the current map if migration
    # fails. New pilot FT assets may remain, but no source asset is overwritten.
    for group in groups:
        unreal.InstancedFoliageActor.remove_all_instances(world,unreal.load_asset(group['new_foliage_type']))
    for old_ft,transforms in removed_groups:
        unreal.InstancedFoliageActor.add_instances(world,old_ft,transforms)
    for row,old_mesh,mesh,old_types,initial in jobs:
        verify_transforms([serial(t) for t in initial],[serial(t) for t in instances(old_mesh)])
    assert levels.save_current_level()
    raise

# Reopening is part of this migration, because component-only overrides failed
# exactly at that boundary. Reacquire the world and all components after reload.
assert levels.load_level(LEVEL)
world = editor.get_editor_world()
after = []
for row,old_mesh,mesh,old_types,initial in jobs:
    old_mesh = unreal.load_asset(row['old_mesh'])
    mesh = unreal.load_asset(row['new_mesh'])
    assert not instances(old_mesh), ('Old mesh reappeared after reload',row['family'])
    current = instances(mesh)
    assert len(current) == row['count']
    errors = verify_transforms([serial(t) for t in initial],[serial(t) for t in current])
    for ft in old_types:
        assert ft.get_editor_property('mesh') == old_mesh, 'Shared source foliage type changed'
        assert hashlib.sha256(asset_file(ft).read_bytes()).hexdigest() == row['source_foliage_type_sha256'][ft.get_path_name()]
    for group in [g for g in groups if g['family']==row['family']]:
        ft = unreal.load_asset(group['new_foliage_type'])
        assert ft.get_editor_property('mesh') == mesh
        body = ft.get_editor_property('body_instance')
        assert str(body.get_editor_property('collision_profile_name')) == row['collision']
    after.append({'family':row['family'],'mesh':mesh.get_path_name(),'count':len(current),
                  'maximum_transform_errors':errors,'collision':row['collision'],'components':components(mesh)})
receipt = {'level':LEVEL,'saved_and_reopened':True,'transform_policy':'Preserved current transforms without rescaling',
           'source_foliage_types_unchanged':True,'source_asset_hashes_unchanged':True,
           'total_instances':sum(row['count'] for row in after),'groups':groups,'unused_source_types':unused,'after':after}
receipt_path.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
unreal.log('Pilot foliage persisted and reopened: '+str(receipt['total_instances'])+' instances with unchanged transforms.')
