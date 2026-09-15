"""Read actual scene geometry/material bindings before and after a native map reopen."""
import unreal,json,sys,math,gc
from pathlib import Path
from collections import Counter
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment';sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
target='/Game/Terrarium/Maps/HomesteadReference';assert '/HomesteadReference.' in str(levels.get_current_level())
def vec(v):return [v.x,v.y,v.z]
def transforms(t):return [*vec(t.translation),t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w,*vec(t.scale3d)]
def snapshot():
    meshes=[];contacts=[];landmarks=[];counts=Counter();ground=[]
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh or c.static_mesh.get_name()=='MatineeCam_SM':continue
            ts=[c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count())] if isinstance(c,unreal.InstancedStaticMeshComponent) else [a.get_actor_transform()]
            name=c.static_mesh.get_name();counts[name]+=len(ts)
            materials=[c.get_material(i).get_path_name() for i in range(c.get_num_materials())];assert all(materials)
            meshes.append({'mesh':c.static_mesh.get_path_name(),'materials':materials,'transforms':sorted([transforms(t) for t in ts])})
            if name=='SM_Env_MeadowTile':ground.extend(vec(t.translation) for t in ts)
        label=a.get_actor_label()
        if label in ['Reference_Cottage','Reference_BlueShed','Reference_Tower','Reference_Lantern','Reference_VegetableBed','Reference_FlowerBorder','Reference_Player']:
            p=a.get_actor_location();o,e=a.get_actor_bounds(False);err=o.z-e.z-560
            assert abs(err)<.02,(label,err)
            contacts.append({'actor':label,'minimum_z_cm':o.z-e.z,'terrain_z_cm':560,'error_cm':err})
            landmarks.append({'actor':label,'reference_pixel':ref.pixel(p.x,p.y,p.z),'position_cm':vec(p),'scale':vec(a.get_actor_scale3d()),'yaw':a.get_actor_rotation().yaw})
    assert len(contacts)==7
    assert counts['SM_Recon_Player_R3']==1 and counts['SM_Traveler_v2_Detail']==0
    assert counts['SM_Env_Cottage']==1 and counts['SM_Env_BlueShed']==1
    assert counts['SM_Env_WheatPatch']==40
    assert sum(counts['SM_Env_Cliff_'+v+'_R2'] for v in 'ABC')==2076
    assert counts['SM_Env_MeadowTile']==5841 and counts['SM_PathTile_v4_Detail']==84
    assert counts['SM_Recon_HomesteadTree_R3']==14
    camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review');cc=camera.camera_component
    assert cc.projection_mode==unreal.CameraProjectionMode.ORTHOGRAPHIC and abs(cc.ortho_width-2645.5)<.001
    assert abs(camera.get_actor_rotation().pitch+45)<.01 and abs(camera.get_actor_rotation().yaw-135)<.01
    pixel=next(x['reference_pixel'] for x in landmarks if x['actor']=='Reference_Player');assert math.dist(pixel,[177,394])<.001
    return {'bindings':sorted(meshes,key=lambda r:(r['mesh'],str(r['transforms']))),'counts':dict(sorted(counts.items())),'contacts':sorted(contacts,key=lambda r:r['actor']),'landmarks':sorted(landmarks,key=lambda r:r['actor']),'camera':{'position':vec(camera.get_actor_location()),'yaw':135,'pitch':-45,'orthographic_width_cm':cc.ortho_width,'aspect_ratio':cc.aspect_ratio,'auto_activate':str(camera.get_editor_property('auto_activate_for_player'))}}
levels.eject_pilot_level_actor();before=snapshot();assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Reconstruction/Maps/ReviewStage')
assert levels.load_level(target)
after=snapshot();assert before==after,'Native saved/reopened scene differs'
(out/'scene-state.json').write_text(json.dumps(after,indent=2))
report={k:v for k,v in after.items() if k!='bindings'}
report.update({'project':unreal.Paths.get_project_file_path(),'map':target,'saved_and_reopened_identically':True,'material_bindings_verified':True,'ground_contact_tolerance_cm':.02,'source_image':'C:/Users/hello/.codex/attachments/1ccf9c86-0559-4bb2-8197-f3f4da9c0f7f/image-1.png','visual_acceptance':'pending final rendered comparison','gameplay_collision_animation_tested':False})
(out/'verification.json').write_text(json.dumps(report,indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([])
unreal.log('REFERENCE_ENVIRONMENT_NATIVE_VERIFIED')
