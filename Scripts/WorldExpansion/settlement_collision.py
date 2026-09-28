"""Use actual authored LOD2 for collision on private REGION architecture copies.

Coordinator runs in verified ValleyRegion with PIE stopped. Original meshes,
materials, visual LOD chains and all original home actor assignments are preserved.
"""
import hashlib, json
from collections import Counter
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
DOC=ROOT/'Docs/WorldExpansion'
data=json.loads((DOC/'settlement-layout.json').read_text())
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
S=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert not E.get_game_world()
assert E.get_editor_world().get_path_name().split('.')[0]==data['map']
DEST='/Game/Terrarium/WorldExpansion/Architecture/Meshes'
rows={r['label']:r for r in data['placements']}
scene={a.get_actor_label():a for a in A.get_all_level_actors()}
assert set(rows)<=set(scene), 'Integrate all settlement actors first'

def digest(mesh):
    path=ROOT/'Content'/(mesh.get_path_name().split('.')[0].removeprefix('/Game/')+'.uasset')
    return hashlib.sha256(path.read_bytes()).hexdigest()

def signature(actor):
    t=actor.get_actor_transform()
    return {'transform':{'location':[t.translation.x,t.translation.y,t.translation.z],
                         'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z],
                         'quaternion':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]},
            'meshes':[c.static_mesh.get_path_name() if c.static_mesh else None
                      for c in actor.get_components_by_class(unreal.StaticMeshComponent)]}

def same_transform(a,b):
    # Native Transform repr includes an allocation address; compare values only.
    return (max(abs(x-y) for x,y in zip(a['location'],b['location']))<=.001
            and max(abs(x-y) for x,y in zip(a['scale'],b['scale']))<=.000001
            and min(max(abs(x-y) for x,y in zip(a['quaternion'],b['quaternion'])),
                    max(abs(x+y) for x,y in zip(a['quaternion'],b['quaternion'])))<=.000001)

preserved={label:signature(actor) for label,actor in scene.items() if label not in rows}
actor_counts=Counter(row['asset'] for row in rows.values())
copies={};evidence=[]
for key,count in sorted(actor_counts.items()):
    source=unreal.load_asset(data['assets'][key]);assert isinstance(source,unreal.StaticMesh)
    original_hash=digest(source)
    original_lod=source.get_editor_property('lod_for_collision')
    original_flag=source.get_editor_property('body_setup').get_editor_property('collision_trace_flag')
    assert S.get_lod_count(source)==3,(key,'Expected actual three-LOD admitted asset')
    triangles=[source.get_num_triangles(i) for i in range(3)]
    assert triangles[0]>triangles[1]>triangles[2]>0,(key,triangles)
    path=DEST+'/SM_WX_'+key
    mesh=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset(source.get_path_name().split('.')[0],path)
    assert isinstance(mesh,unreal.StaticMesh) and mesh!=source
    assert S.get_lod_count(mesh)==3
    assert [mesh.get_num_triangles(i) for i in range(3)]==triangles
    body=mesh.get_editor_property('body_setup');source_body=source.get_editor_property('body_setup')
    assert body and body!=source_body,'Private duplicate must own its BodySetup'
    mesh.modify();body.modify()
    # Authored LOD2 retains the real doors, stairways and open spaces; no whole-
    # building box is introduced. All rendering geometry/materials remain intact.
    body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    body.set_editor_property('double_sided_geometry',source_body.get_editor_property('double_sided_geometry'))
    mesh.set_editor_property('lod_for_collision',2)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    assert mesh.get_editor_property('lod_for_collision')==2
    assert body.get_editor_property('collision_trace_flag')==unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
    assert [mesh.get_num_triangles(i) for i in range(3)]==triangles
    assert [str(s.material_interface) for s in mesh.static_materials]==[str(s.material_interface) for s in source.static_materials]
    assert digest(source)==original_hash
    assert source.get_editor_property('lod_for_collision')==original_lod
    assert source_body.get_editor_property('collision_trace_flag')==original_flag
    copies[key]=mesh
    evidence.append({'asset':key,'source':source.get_path_name(),'private_mesh':mesh.get_path_name(),
        'source_sha256':original_hash,'source_disk_unchanged':True,'source_collision_lod':original_lod,
        'source_collision_flag':str(original_flag),'native_lod_count':S.get_lod_count(mesh),
        'native_triangles':triangles,'collision_lod':2,'collision_triangles_per_instance':triangles[2],
        'actor_count':count,'visual_geometry_and_materials_unchanged':True})

changes=[]
for label,row in rows.items():
    actor=scene[label];comp=actor.static_mesh_component
    before=signature(actor);enabled=comp.get_collision_enabled();profile=comp.get_collision_profile_name()
    comp.set_static_mesh(copies[row['asset']]);comp.set_collision_profile_name(profile);comp.set_collision_enabled(enabled)
    comp.set_editor_property('forced_lod_model',0)
    assert same_transform(signature(actor)['transform'],before['transform']),(label,'Transform changed')
    changes.append({'actor':label,'mesh':copies[row['asset']].get_path_name(),'collision_lod':2})
for label,before in preserved.items():
    after=signature(scene[label])
    assert same_transform(after['transform'],before['transform']) and after['meshes']==before['meshes'],(label,'Non-settlement actor changed')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
mapping={'map':data['map'],'assets':{key:mesh.get_path_name() for key,mesh in copies.items()},
         'policy':'Private exact render copies; existing authored LOD2 complex collision; original assets and home unchanged'}
(DOC/'settlement-collision-assets.json').write_text(json.dumps(mapping,indent=2))
receipt={'map':data['map'],'native_mesh_evidence':evidence,'actor_changes':changes,
         'non_settlement_actor_assignments_and_transforms_preserved':True,
         'sum_collision_triangles_at_placements_before':sum(r['native_triangles'][r['source_collision_lod']]*r['actor_count'] for r in evidence),
         'sum_collision_triangles_at_placements_after':sum(r['collision_triangles_per_instance']*r['actor_count'] for r in evidence),
         'validation_scope':'Native counts/properties/materials/source hashes/actor transforms. Collision traversal and navigation warning readback require coordinator tests.'}
(DOC/'settlement-collision.json').write_text(json.dumps(receipt,indent=2))
# Keep integration receipt authoritative for the final bindings.
p=DOC/'settlement-integration.json'
if p.exists():
    integration=json.loads(p.read_text())
    for row in integration['actors']:row['mesh']=mapping['assets'][row['asset']]
    integration['architecture_collision']='Private mesh copies with authored LOD2 complex collision'
    p.write_text(json.dumps(integration,indent=2))
print(json.dumps({'changed_actors':len(changes),'private_meshes':len(copies),
                  'before':receipt['sum_collision_triangles_at_placements_before'],
                  'after':receipt['sum_collision_triangles_at_placements_after']}))
