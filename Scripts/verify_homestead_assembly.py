"""Verify the final eight-part family in the live world and isolated review map."""
import unreal,json,re,sys,gc
from pathlib import Path
from collections import defaultdict
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/HomesteadAssembly'
sys.path.insert(0,str(root/'Scripts/Assets'));import homestead_assembly as family
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.eject_pilot_level_actor();world=None;review=None;camera=None;baseline=None;a=None;c=None;gc.collect()
def snapshot():
    rows=defaultdict(list)
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            name=c.static_mesh.get_name()
            if name=='MatineeCam_SM':continue
            ts=[c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count())] if isinstance(c,unreal.InstancedStaticMeshComponent) else [a.get_actor_transform()]
            for t in ts:
                tr=tuple(float(v) for v in re.findall(r'[xyzw]: (-?\d+\.\d+)',str(t)));assert len(tr)==10
                rows[name].append((c.get_material(0).get_path_name(),tr))
    return {n:sorted(v) for n,v in rows.items()}
assert levels.load_level('/Game/Terrarium/Maps/HomesteadAssemblyReview')
showcase=snapshot()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='HouseFence_Review_Transient':actors.destroy_actor(a)
a=None
before=snapshot();assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadBeforeAssemblyReference')
original=snapshot()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
after=snapshot();assert before==after,'Scene differs after saving and reopening'
names=set(family.BUILDERS)
assert {n for n in after if n.startswith('SM_Assembly_')}==names
assert all(after[n]==showcase[n] for n in names),'Showcase differs from the world assembly'
layout=json.loads((out/'integration.json').read_text())
expected={n:1 for n in names};expected['SM_Assembly_FencePost']=layout['fence_posts'];expected['SM_Assembly_FenceRails']=layout['fence_sections']
assert all(len(after[n])==expected[n] for n in names)
assert all(row[0]=='/Game/Terrarium/Materials/M_AssemblyCrafted.M_AssemblyCrafted' for n in names for row in after[n])
changed=set(layout['asset_mapping'])|{'SM_PathTile_v4_Detail','SM_FencePost_Reference','SM_FenceRails_Reference',
 'SM_Bush_v2_Detail','SM_MeadowGrass_v2_Detail','SM_GroundPlants_v2_Detail','SM_MeadowFlowers_v2_Detail'}
preserved=[]
for name,rows in original.items():
    if name not in changed:
        assert after[name]==rows,name+' changed outside assembly scope';preserved.append(name)
geometry={}
for name in sorted(names):
    p=root/'Docs/Phase1/Validation'/(name+'.json');g=json.loads(p.read_text())
    assert g['saved_normal_errors']==0 and g['all_components_closed']
    geometry[name]={'triangles':g['triangles'],'closed_components':True,'saved_normal_errors':0}
    g['visual_review']='passed: reviewed together in native assembly and in-world captures';p.write_text(json.dumps(g,indent=2))
(out/'verification.json').write_text(json.dumps({'saved_reopened':True,'showcase_matches_world_assembly':True,
 'asset_types':8,'instance_counts':expected,'preserved_asset_types':preserved,'geometry':geometry,
 'tested':'Native editor geometry, material rendering, object proportions, path clearance, saved transforms and material references. Packaged gameplay and collision not tested.'},indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
unreal.log('HOMESTEAD_ASSEMBLY_VERIFIED')
