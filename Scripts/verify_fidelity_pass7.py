"""Inspect actual native world state after save/reopen; separate visual verdict."""
import unreal,json,math
from pathlib import Path
from collections import Counter
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Fidelity/Pass7'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/HomesteadBeforePass7')
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
counts=Counter();materials={};transforms={};normals={}
for actor in actors.get_all_level_actors():
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh=component.static_mesh
        if not mesh:continue
        name=mesh.get_name()
        if not mesh.get_path_name().startswith('/Game/Terrarium/Meshes/'):continue
        n=component.get_instance_count() if isinstance(component,unreal.InstancedStaticMeshComponent) else 1
        if n<=0:continue
        counts[name]+=n
        materials[name]=component.get_material(0).get_path_name()
        assert not component.get_material(0).get_editor_property('two_sided')
        if not isinstance(component,unreal.InstancedStaticMeshComponent):
            transforms[actor.get_actor_label()]={'location':str(actor.get_actor_location()),'scale':str(actor.get_actor_scale3d()),'bounds':str(actor.get_actor_bounds(False))}
        evidence=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
        assert evidence['saved_normal_errors']==0
        normals[name]={'triangles':evidence['triangles'],'saved_normal_errors':0}
expected=json.loads((out/'layout.json').read_text())['counts']
counts_match=dict(counts)=={'SM_'+k:v for k,v in expected.items()}
assert counts['SM_FencePost']>=18 and counts['SM_FenceRails']>=12, 'Both original fence runs must remain'
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
camera=scene['Baseline_Orthographic_Review'];cc=camera.camera_component
assert cc.projection_mode==unreal.CameraProjectionMode.ORTHOGRAPHIC
assert abs(cc.ortho_width-2645.5)<.01
assert cc.post_process_blend_weight==1.0, 'Camera must actually apply distant softness'
blendables=cc.post_process_settings.weighted_blendables.array
assert any(b.weight==1.0 and b.object.get_name()=='M_Pass7_DistantSoftness' for b in blendables)
cvars={n:unreal.SystemLibrary.get_console_variable_int_value(n) for n in ['r.DynamicGlobalIlluminationMethod','r.ReflectionMethod','r.GenerateMeshDistanceFields','r.Lumen.DiffuseIndirect.Allow','r.Lumen.Reflections.Allow','r.Shadow.Virtual.Enable']}
assert all(v==1 for v in cvars.values())
pp=scene['Baseline_FixedExposure_EV12'].settings
assert pp.auto_exposure_method==unreal.AutoExposureMethod.AEM_MANUAL
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([]);assert levels.save_current_level()
report={'project':unreal.Paths.get_project_file_path(),'engine':unreal.SystemLibrary.get_engine_version(),'saved_reopened':True,'actual_counts':dict(counts),'counts_match_composition':counts_match,'mesh_geometry':normals,'materials':materials,'static_actor_transforms':transforms,'lumen':cvars,'exposure_bias':pp.auto_exposure_bias,'visual_acceptance':'requires direct review of latest native screenshot'}
(out/'editor-validation.json').write_text(json.dumps(report,indent=2))
assert counts_match,(dict(counts),expected)
unreal.log('PASS7_SAVED_REOPENED_VALIDATED')
