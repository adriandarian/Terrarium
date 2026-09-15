import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/Brambit';record=json.loads((out/'world-placement.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(record['world'])
scene=actors.get_all_level_actors();matching=[a for a in scene if a.get_actor_label()==record['actor']];assert len(matching)==1
actor=matching[0];c=actor.static_mesh_component;mesh=c.static_mesh
assert mesh.get_path_name()==record['mesh'] and sum(isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh==mesh for a in scene)==1
p=actor.get_actor_location();s=actor.get_actor_scale3d();r=actor.get_actor_rotation()
assert max(abs(v-e) for v,e in zip([p.x,p.y,p.z],record['location_cm']))<.001
assert all(abs(v-record['scale'])<1e-6 for v in [s.x,s.y,s.z]) and abs(r.yaw)+abs(r.pitch)+abs(r.roll)<.001
assert len(mesh.static_materials)==1;mat=mesh.get_material(0)
assert mat.get_path_name()==record['materials'][0] and c.get_material(0)==mat
mel=unreal.MaterialEditingLibrary
for prop in [unreal.MaterialProperty.MP_METALLIC,unreal.MaterialProperty.MP_EMISSIVE_COLOR]:
    node=mel.get_material_property_input_node(mat,prop);assert isinstance(node,unreal.MaterialExpressionConstant) and node.r==0
assert mat.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_OPAQUE
for kind,prop in [('BaseColor',unreal.MaterialProperty.MP_BASE_COLOR),('Roughness',unreal.MaterialProperty.MP_ROUGHNESS)]:
    node=mel.get_material_property_input_node(mat,prop);assert isinstance(node,unreal.MaterialExpressionTextureSample)
    assert node.texture.get_path_name()==f'/Game/Terrarium/Blender/Brambit/T_Brambit_{kind}.T_Brambit_{kind}'
    assert node.texture.get_editor_property('srgb')==(kind=='BaseColor')
    assert (root/f'SourceAssets/Blender/Brambit/Brambit_{kind}.png').read_bytes()[24]==8
components={(a.get_actor_label(),c.get_name()):c for a in scene for c in a.get_components_by_class(unreal.StaticMeshComponent)}
probes=[]
for sample in record['support_probes']:
    px,py=sample['xy'];terrain=components[(sample['ground_actor'],sample['ground_component'])]
    ground=terrain.line_trace_component(unreal.Vector(px,py,800),unreal.Vector(px,py,500),True,False,False)
    assert ground and abs(ground[0].z-sample['ground_z'])<.01
    foot=c.line_trace_component(unreal.Vector(px,py,ground[0].z-5),unreal.Vector(px,py,ground[0].z+90),True,False,False)
    expected=p.z+sample['local_bottom_m']*100*s.z
    assert foot and abs(foot[0].z-expected)<.02
    clearance=foot[0].z-ground[0].z;assert 0<=clearance<.55
    probes.append({'foot':sample['foot'],'xy':[px,py],'ground_z':ground[0].z,'imported_sole_z':foot[0].z,'clearance_cm':clearance,'passed':True})
fbx=root/'SourceAssets/Blender/Brambit/SM_Blender_Brambit.fbx';digest=hashlib.sha256(fbx.read_bytes()).hexdigest()
assert digest==json.loads((out/'unreal-import.json').read_text())['source_fbx_sha256']==json.loads((out/'mesh-validation.json').read_text())['files'][fbx.name]['sha256']
assert mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')==unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
(out/'saved-world-verification.json').write_text(json.dumps({'reload_verified':True,'actor':record['actor'],'source_fbx_sha256':digest,'source_blend_sha256':record['source_blend_sha256'],'material_verified':True,'foot_samples':probes,'max_clearance_cm':max(p['clearance_cm'] for p in probes),'limits':'Static imported model, shader and sampled foot support. No rigging, animation, locomotion, rigid-body simulation, full collision or performance certification.'},indent=2))
