"""Reload the saved map and verify Grove placement, all slots, and counter contact."""
import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/Grove';record=json.loads((out/'world-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(record['world'])
scene=actors.get_all_level_actors();found=[a for a in scene if a.get_actor_label()==record['actor']];assert len(found)==1
a=found[0];c=a.static_mesh_component;mesh=c.static_mesh;assert mesh.get_path_name()==record['mesh']
assert sum(isinstance(o,unreal.StaticMeshActor) and o.static_mesh_component.static_mesh==mesh for o in scene)==1
p=a.get_actor_location();sc=a.get_actor_scale3d();r=a.get_actor_rotation()
assert all(abs(v-e)<.001 for v,e in zip([p.x,p.y,p.z],record['location_cm']))
assert all(abs(v-record['scale'])<1e-6 for v in [sc.x,sc.y,sc.z]) and abs(r.yaw)+abs(r.pitch)+abs(r.roll)<1e-6
expected=json.loads((out/'material-bindings.json').read_text())['slots'];assert len(mesh.static_materials)==3
bindings=[]
for slot in expected:
    i=slot['index'];mat=mesh.get_material(i)
    assert mat.get_path_name()==slot['material'] and c.get_material(i)==mat
    assert str(mesh.static_materials[i].get_editor_property('imported_material_slot_name'))==slot['imported_name']
    assert str(mat.get_editor_property('blend_mode'))==slot['blend_mode']
    mel=unreal.MaterialEditingLibrary
    emission=mel.get_material_property_input_node(mat,unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    assert isinstance(emission,unreal.MaterialExpressionConstant) and emission.r==0
    for kind,prop in [('BaseColor',unreal.MaterialProperty.MP_BASE_COLOR),('Roughness',unreal.MaterialProperty.MP_ROUGHNESS)]:
        node=mel.get_material_property_input_node(mat,prop)
        assert isinstance(node,unreal.MaterialExpressionTextureSample)
        assert node.texture.get_path_name()==f'/Game/Terrarium/Blender/Grove/T_Grove_{kind}.T_Grove_{kind}'
    for name,value in slot['parameters'].items():assert abs(unreal.MaterialEditingLibrary.get_material_default_scalar_parameter_value(mat,name)-value)<1e-6
    bindings.append({'role':slot['role'],'material':mat.get_path_name(),'passed':True})
counter=next(o for o in scene if o.get_actor_label()==record['support_actor']).static_mesh_component
probes=[]
for sample in record['support_probes']:
    x,y=sample['xy'];hit=counter.line_trace_component(unreal.Vector(x,y,670),unreal.Vector(x,y,630),True,False,False)
    assert hit and abs(hit[0].z-sample['z'])<.005
    probes.append({'xy':[x,y],'z':hit[0].z,'passed':True})
bottom=p.z+mesh.get_bounding_box().min.z*sc.z;gap=bottom-max(q['z'] for q in probes)
assert abs(gap-record['base_clearance_cm'])<.005
export=json.loads((out/'mesh-validation.json').read_text());imported=json.loads((out/'unreal-import.json').read_text())
fbx=root/'SourceAssets/Blender/Grove/SM_Blender_Grove.fbx'
assert hashlib.sha256(fbx.read_bytes()).hexdigest()==export['files'][fbx.name]['sha256']==imported['source_fbx_sha256']
for kind in ['BaseColor','Emission','Roughness']:
    tex=unreal.load_asset(imported['textures'][kind]);assert tex.get_editor_property('srgb')==(kind!='Roughness')
    assert (root/f'SourceAssets/Blender/Grove/Grove_{kind}.png').read_bytes()[24]==8
(out/'saved-world-verification.json').write_text(json.dumps({'reload_verified':True,'actor':record['actor'],'materials':bindings,'counter_support':probes,'base_clearance_cm':gap,'source_hash_verified':True,'limits':'Sampled static support and shader bindings; no gameplay, full collision or performance validation. Visual refinement remains open.'},indent=2))
