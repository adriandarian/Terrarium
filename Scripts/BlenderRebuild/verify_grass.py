"""Reload all meadow instances and verify source binding, transforms and sampled physical surfaces."""
import unreal,json,hashlib
from pathlib import Path
from collections import Counter
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/GrassTerrain';r=json.loads((folder/'instance-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(r['world'])
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mesh=unreal.load_asset(r['mesh']);oldmesh=unreal.load_asset(r['old_mesh'])
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def code(t):return json.dumps({k:[round(v,5) for v in values] for k,values in t.items()},sort_keys=True)
components=[];actual=[];oldcount=0;profiles=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh==oldmesh:oldcount+=c.get_instance_count()
        if c.static_mesh!=mesh:continue
        components.append(c);assert c.get_material(0)==mesh.get_material(0)
        assert c.get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS
        assert c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)==unreal.CollisionResponseType.ECR_BLOCK
        profiles.append({'component':c.get_name(),'count':c.get_instance_count(),'profile':str(c.get_collision_profile_name())})
        actual.extend(serial(c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count()))
expected=[t for group in r['groups'] for t in group['transforms']]
assert len(actual)==r['count']==5841 and oldcount==0
assert Counter(code(t) for t in actual)==Counter(code(t) for t in expected)
for group in r['groups']:
    assert unreal.load_asset(group['old_foliage_type']).get_editor_property('mesh')==oldmesh
    ft=unreal.load_asset(group['new_foliage_type']);assert ft.get_editor_property('mesh')==mesh
    candidates=[c for c in components if c.get_instance_count()==group['count']]
    assert len(candidates)==1
    assert Counter(code(serial(candidates[0].get_instance_transform(i,world_space=True))) for i in range(group['count']))==Counter(code(t) for t in group['transforms'])
source=root/'SourceAssets/Voxel/terrain_grass_top_v9.png';copy=root/'SourceAssets/Blender/GrassTerrain/GrassTerrain_BaseColor.png'
assert source.read_bytes()==copy.read_bytes()
exported=json.loads((folder/'mesh-validation.json').read_text());imported=json.loads((folder/'unreal-import.json').read_text())
assert imported['source_fbx_sha256']==exported['files']['SM_Blender_GrassTerrain.fbx']['sha256']
sample=json.loads((folder/'height-samples.json').read_text());zlocal=sample['center_surface_z_m']*100
checks=[]
for c in components:
    for i in range(0,c.get_instance_count(),max(1,c.get_instance_count()//12)):
        t=c.get_instance_transform(i,world_space=True);p=t.translation;expected_z=p.z+zlocal*t.scale3d.z
        start=unreal.Vector(p.x,p.y,p.z+3)
        # Query the meadow component itself: solid cliffs can cover lower edge tiles.
        # Keep the unfiltered world result separately instead of calling an overlap
        # a grass geometry failure or claiming the meadow is the exposed surface.
        world_above=unreal.SystemLibrary.line_trace_single(world,start,unreal.Vector(p.x,p.y,expected_z+.05),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE,ignore_self=False)
        def trace(z):return c.line_trace_component(start,unreal.Vector(p.x,p.y,z),trace_complex=True,show_trace=False,persistent_show_trace=False)
        above=trace(expected_z+.05);below=trace(expected_z-.05)
        assert above is None and below is not None,(c.get_name(),i,expected_z,str(above),str(below))
        checks.append({'component':c.get_name(),'index':i,'xy_cm':[p.x,p.y],'top_cm':expected_z,'tolerance_cm':.05,'passed':True,'trace_scope':'meadow_component','unfiltered_world_obstructed_above':world_above is not None})
# Preserve the staircase's old terrain record, adding the current component bindings.
stair=root/'Docs/BlenderRebuild/StoneStairs/terrain-adjustment.json'
data=json.loads(stair.read_text())
for row in data['instances']:
    if 'SM_Env_MeadowTile.' not in row['mesh']:continue
    matches=[]
    for c in components:
        for i in range(c.get_instance_count()):
            p=c.get_instance_transform(i,world_space=True).translation
            if all(abs(a-b)<.01 for a,b in zip(vec(p),row['after_cm'])):matches.append((c,i))
    assert len(matches)==1
    c,i=matches[0];row['replacement_component']=c.get_name();row['replacement_index']=i;row['replacement_mesh']=mesh.get_path_name()
stair.write_text(json.dumps(data,indent=2))
(folder/'saved-world-verification.json').write_text(json.dumps({'world':r['world'],'reloaded_from_disk':True,'count':len(actual),'all_transforms_verified':True,'groups':profiles,'source_albedo_byte_identical':True,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'import_export_hash_match':True,'surface_probes':checks,'limits':'Sampled component collision verifies the grass mesh. Unfiltered world obstructions are reported separately; some lower meadow edge tiles overlap solid cliffs. This does not establish exposed ground, character traversal or performance. Inferred relief and world appearance still require visual review.'},indent=2))
unreal.log('BLENDER_GRASS_RELOAD_VERIFIED')
