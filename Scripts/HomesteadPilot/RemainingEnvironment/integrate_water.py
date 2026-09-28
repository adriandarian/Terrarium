"""Coordinator-only Unreal editor operation: import, migrate, save and reopen.

Only StartingHome and RemainingEnvironment assets are changed. A 12-triangle
closed tile replaces each inherited water tile; all world bounds are retained.
Shared materials/meshes/FoliageTypes and the baseline map are never saved.
"""
import unreal, hashlib, json, math
from collections import Counter
from pathlib import Path

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
DOC = ROOT/'Docs/HomesteadPilot/RemainingEnvironment'
SRC = ROOT/'Scripts/HomesteadPilot/RemainingEnvironment'
DEST = '/Game/Terrarium/HomesteadPilot/RemainingEnvironment'
LEVEL = '/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
E = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
M = unreal.MaterialEditingLibrary
T = unreal.AssetToolsHelpers.get_asset_tools()
world = E.get_editor_world()
assert world.get_path_name().split('.')[0] == LEVEL
assert not E.get_game_world(), 'Stop PIE before water integration'
assert not (DOC/'unreal-validation.json').exists(), 'Already integrated; inspect receipt before rerunning'
manifest = json.loads((DOC/'manifest.json').read_text())
expected = manifest['water_instances_expected']
old_paths = {'/Game/Terrarium/Meshes/SM_'+k+'.SM_'+k:v for k,v in expected.items()}

def values(v): return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation
    return {'translation':values(t.translation),'scale':values(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def code(t):
    r=serial(t)
    return json.dumps({k:[round(v,4) for v in a] for k,a in r.items()},sort_keys=True)
def components(mesh):
    return [c for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent)
            if c.static_mesh==mesh and c.get_instance_count()]
def instances(mesh):
    return [c.get_instance_transform(i,world_space=True) for c in components(mesh) for i in range(c.get_instance_count())]
def unchanged_snapshot():
    rows=[];grass=0
    for a in A.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh: continue
            path=c.static_mesh.get_path_name()
            if path in old_paths or path.startswith(DEST+'/'): continue
            ts=[c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count())] if isinstance(c,unreal.InstancedStaticMeshComponent) else [c.get_world_transform()]
            if 'GrassTerrain' in path: grass+=len(ts)
            rows.extend(path+'|'+code(t) for t in ts)
    return {'sha256':hashlib.sha256('\n'.join(sorted(rows)).encode()).hexdigest(),'instances':len(rows),'grass':grass}
def file_for(asset):
    return ROOT/'Content'/(asset.get_path_name().split('.')[0].removeprefix('/Game/')+'.uasset')

before=unchanged_snapshot()
assert before['grass']==5841, ('Grass guard',before)
baseline=ROOT/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap'
baseline_hash=hashlib.sha256(baseline.read_bytes()).hexdigest()
registry=unreal.AssetRegistryHelpers.get_asset_registry()
types=[]
for data in registry.get_assets_by_path('/Game/Terrarium',recursive=True):
    if not str(data.asset_name).startswith('FT_'): continue
    ft=data.get_asset()
    if isinstance(ft,unreal.FoliageType_InstancedStaticMesh) and ft.get_editor_property('mesh') and ft.get_editor_property('mesh').get_path_name() in old_paths:
        types.append(ft)
jobs=[]
for path,count in old_paths.items():
    mesh=unreal.load_asset(path);ts=instances(mesh)
    assert len(ts)==count,(path,len(ts),count)
    fts=[ft for ft in types if ft.get_editor_property('mesh')==mesh]
    assert fts,path
    jobs.append((mesh,fts,ts))

materials={}
for key,bias in [('WaterTile_v4_Detail',0),('WaterShallow_v4_Detail',.12),('WaterDeep_v4_Detail',-.12)]:
    name='M_HP_River'+('Shallow' if 'Shallow' in key else 'Deep' if 'Deep' in key else 'Current')
    mat=unreal.load_asset(DEST+'/Materials/'+name)
    if not mat: mat=T.create_asset(name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    mat.set_editor_property('used_with_instanced_static_meshes',True)
    mat.set_editor_property('tangent_space_normal',False)
    pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-700,0)
    time=M.create_material_expression(mat,unreal.MaterialExpressionTime,-700,180)
    normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS,-700,360)
    depth=M.create_material_expression(mat,unreal.MaterialExpressionConstant,-700,540);depth.r=bias
    for script,prop,y,inputs in [('river_color.hlsl',unreal.MaterialProperty.MP_BASE_COLOR,0,[('World',pos),('Seconds',time),('DepthBias',depth)]),
                               ('river_normal.hlsl',unreal.MaterialProperty.MP_NORMAL,300,[('World',pos),('Seconds',time),('SurfaceNormal',normal)])]:
        custom=M.create_material_expression(mat,unreal.MaterialExpressionCustom,-320,y)
        custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
        pins=[]
        for name,node in inputs:
            pin=unreal.CustomInput();pin.set_editor_property('input_name',name);pins.append(pin)
        custom.set_editor_property('inputs',pins)
        custom.set_editor_property('code',(SRC/script).read_text())
        for name,node in inputs: assert M.connect_material_expressions(node,'',custom,name)
        assert M.connect_material_property(custom,'',prop)
    for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.36,600),(unreal.MaterialProperty.MP_SPECULAR,.30,700)]:
        n=M.create_material_expression(mat,unreal.MaterialExpressionConstant,-320,y);n.r=value
        assert M.connect_material_property(n,'',prop)
    M.recompile_material(mat)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    materials[key]=mat

asset=manifest['assets'][0];source=ROOT/asset['fbx']
assert hashlib.sha256(source.read_bytes()).hexdigest()==asset['fbx_sha256']
opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False
opts.import_as_skeletal=False;opts.import_animations=False;opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
d=opts.static_mesh_import_data;d.combine_meshes=True;d.generate_lightmap_u_vs=False;d.auto_generate_collision=False
d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
task=unreal.AssetImportTask();task.filename=str(source);task.destination_path=DEST+'/Meshes';task.destination_name=asset['mesh_name']
task.automated=True;task.replace_existing=True;task.save=True;task.options=opts;task.factory=unreal.FbxFactory()
T.import_asset_tasks([task]);new=unreal.load_asset(DEST+'/Meshes/'+asset['mesh_name']);assert new
new.set_material(0,materials['WaterTile_v4_Detail'])
nb=new.get_bounding_box();size=nb.max-nb.min
assert max(abs(a-b*100) for a,b in zip(values(size),asset['dimensions_m']))<.05
assert unreal.EditorAssetLibrary.save_loaded_asset(new)

def fitted(t,ob):
    # Exact affine local-bound fitting, including rotation of the pivot offset.
    old_s=values(t.scale3d);old_lo=values(ob.min);old_hi=values(ob.max)
    new_lo=values(nb.min);new_hi=values(nb.max)
    scale=[old_s[i]*(old_hi[i]-old_lo[i])/(new_hi[i]-new_lo[i]) for i in range(3)]
    v=[old_lo[i]*old_s[i]-new_lo[i]*scale[i] for i in range(3)]
    q=t.rotation;u=[q.x,q.y,q.z];w=q.w
    cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    uv=cross(u,v);uuv=cross(u,uv);off=[v[i]+2*(w*uv[i]+uuv[i]) for i in range(3)]
    result=unreal.Transform();result.translation=unreal.Vector(*[a+b for a,b in zip(values(t.translation),off)])
    result.scale3d=unreal.Vector(*scale);result.rotation=q
    return result

groups=[];removed_groups=[];all_expected=[];protected_hashes={}
try:
    for old,fts,initial in jobs:
        key=old.get_name().removeprefix('SM_');ob=old.get_bounding_box()
        for old_ft in fts:
            old_path=old_ft.get_path_name();protected_hashes[old_path]=hashlib.sha256(file_for(old_ft).read_bytes()).hexdigest()
            pending=instances(old)
            unreal.InstancedFoliageActor.remove_all_instances(world,old_ft)
            remaining=Counter(code(t) for t in instances(old));removed=[]
            for t in pending:
                c=code(t)
                if remaining[c]:remaining[c]-=1
                else:removed.append(t)
            assert not +remaining
            if not removed:continue
            removed_groups.append((old_ft,removed))
            suffix=hashlib.sha256(old_path.encode()).hexdigest()[:8]
            ft_path=DEST+'/Foliage/FT_HP_River_'+key+'_'+suffix
            assert not unreal.load_asset(ft_path),'Partial prior migration needs inspection: '+ft_path
            ft=unreal.EditorAssetLibrary.duplicate_asset(old_path,ft_path);assert ft
            ft.set_editor_property('mesh',new);ft.set_editor_property('override_materials',[materials[key]])
            body=ft.get_editor_property('body_instance');body.set_editor_property('collision_profile_name','NoCollision')
            body.set_editor_property('collision_enabled',unreal.CollisionEnabled.NO_COLLISION);ft.set_editor_property('body_instance',body)
            assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
            transformed=[fitted(t,ob) for t in removed]
            group={'old_type':old_path,'new_type':ft.get_path_name(),'count':len(removed),
                   'material':materials[key].get_path_name(),'old_bounds_cm':{'min':values(ob.min),'max':values(ob.max)},
                   'before':[serial(t) for t in removed],'after':[serial(t) for t in transformed]}
            groups.append(group);all_expected.extend(transformed)
            (DOC/'migration-progress.json').write_text(json.dumps({'groups':groups},indent=2))
            unreal.InstancedFoliageActor.add_instances(world,ft,transformed)
        assert not instances(old)
    assert len(instances(new))==190
    assert before==unchanged_snapshot(),'Non-water content changed'
    assert L.save_current_level()
except Exception:
    for g in groups:unreal.InstancedFoliageActor.remove_all_instances(world,unreal.load_asset(g['new_type']))
    for old_ft,ts in removed_groups:unreal.InstancedFoliageActor.add_instances(world,old_ft,ts)
    assert before==unchanged_snapshot()
    assert L.save_current_level()
    raise

assert L.load_level(LEVEL);world=E.get_editor_world()
new=unreal.load_asset(DEST+'/Meshes/'+asset['mesh_name'])
actual=instances(new);assert len(actual)==190
# Reimport/reload stores floats; compare unordered transforms at 0.01 cm precision.
def approximate(t):
    r=serial(t);return tuple(round(x,2 if k=='translation' else 4) for k in sorted(r) for x in r[k])
assert Counter(approximate(t) for t in actual)==Counter(approximate(t) for t in all_expected),'Reload transform mismatch'
assert before==unchanged_snapshot(),'Non-water content changed on reopen'
for path,digest in protected_hashes.items():assert hashlib.sha256(file_for(unreal.load_asset(path)).read_bytes()).hexdigest()==digest
assert hashlib.sha256(baseline.read_bytes()).hexdigest()==baseline_hash
for g in groups:
    ft=unreal.load_asset(g['new_type']);assert ft.get_editor_property('mesh')==new
    assert ft.get_editor_property('override_materials')[0].get_path_name()==g['material']
    assert str(ft.get_editor_property('body_instance').get_editor_property('collision_profile_name'))=='NoCollision'
for path in old_paths:assert not instances(unreal.load_asset(path))
receipt={'status':'Imported, saved and reopened; shader appearance and animation require coordinator visual review',
         'mesh':new.get_path_name(),'instances':190,'triangles_per_tile':12,'total_water_triangles':2280,
         'groups':groups,'protected_non_water_snapshot':before,'shared_foliage_files_unchanged':True,
         'baseline_map_unchanged':True,'saved_reopened':True,'world_envelopes_fitted':True,
         'new_bounds_cm':{'min':values(nb.min),'max':values(nb.max)}}
(DOC/'unreal-validation.json').write_text(json.dumps(receipt,indent=2))
unreal.log('HOMESTEAD_REMAINING_WATER_SAVED_REOPENED: 190 tiles, 5841 grass preserved')
