"""Reload and verify the Delver Mark's mounting, uniqueness and shader bindings."""
import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/DeepDelverMark';record=json.loads((out/'world-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(record['world'])
scene=actors.get_all_level_actors();found=[a for a in scene if a.get_actor_label()==record['actor']];assert len(found)==1
a=found[0];c=a.static_mesh_component;mesh=c.static_mesh;assert mesh.get_path_name()==record['mesh']
delver_mesh_actors=[ob for ob in scene if isinstance(ob,unreal.StaticMeshActor) and ob.static_mesh_component.static_mesh and 'DeepDelver' in ob.static_mesh_component.static_mesh.get_name()]
assert delver_mesh_actors==found,[(ob.get_actor_label(),ob.static_mesh_component.static_mesh.get_path_name()) for ob in delver_mesh_actors]
p=a.get_actor_location();sc=a.get_actor_scale3d();r=a.get_actor_rotation()
assert all(abs(v-e)<.001 for v,e in zip([p.x,p.y,p.z],record['location_cm']))
assert all(abs(v-record['scale'])<1e-6 for v in [sc.x,sc.y,sc.z]) and abs(r.yaw)+abs(r.pitch)+abs(r.roll)<1e-6
slots=json.loads((out/'material-bindings.json').read_text())['slots'];assert len(mesh.static_materials)==3
for slot in slots:
    i=slot['index'];mat=mesh.get_material(i)
    assert mat.get_path_name()==slot['material'] and c.get_material(i)==mat
    assert str(mesh.static_materials[i].get_editor_property('imported_material_slot_name'))==slot['imported_name']
    assert mat.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_OPAQUE
    for key,value in slot['parameters'].items():assert abs(unreal.MaterialEditingLibrary.get_material_default_scalar_parameter_value(mat,key)-value)<1e-6
counter=next(o for o in scene if o.get_actor_label()==record['support_actor']).static_mesh_component;probes=[]
for sample in record['wall_samples']:
    x,z=sample['xz'];hit=counter.line_trace_component(unreal.Vector(x,670,z),unreal.Vector(x,600,z),True,False,False)
    assert hit and abs(hit[0].y-sample['y'])<.005;probes.append({'xz':[x,z],'y':hit[0].y})
back=p.y+mesh.get_bounding_box().min.y*sc.y;gap=back-max(q['y'] for q in probes)
assert abs(gap-record['back_clearance_cm'])<.005
export=json.loads((out/'mesh-validation.json').read_text());imported=json.loads((out/'unreal-import.json').read_text())
fbx=root/'SourceAssets/Blender/DeepDelverMark/SM_Blender_DeepDelverMark.fbx'
assert hashlib.sha256(fbx.read_bytes()).hexdigest()==export['files'][fbx.name]['sha256']==imported['source_fbx_sha256']
for kind in ['BaseColor','Emission','Roughness']:
    tex=unreal.load_asset(imported['textures'][kind]);assert tex.get_editor_property('srgb')==(kind!='Roughness')
(out/'saved-world-verification.json').write_text(json.dumps({'reload_verified':True,'actor':record['actor'],'materials_verified':3,'wall_samples':probes,'back_clearance_cm':gap,'source_hash_verified':True,'limits':'Static mounting samples and shader persistence. Wall hardware, pickup gameplay, full collision and performance are not tested. Visual fidelity remains open.'},indent=2))

