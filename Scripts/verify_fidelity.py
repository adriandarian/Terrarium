"""Structural save/reload checks, kept separate from pixel-parity measurements."""
import unreal,json,math
from pathlib import Path
from collections import Counter
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset('/Game/Terrarium/Materials/M_SculptedPalette'))
assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/Homestead')
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
counts=Counter();materials=set()
for a in actors.get_all_level_actors():
    if not isinstance(a,(unreal.StaticMeshActor,unreal.InstancedFoliageActor)):continue
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        sm=c.static_mesh
        if not sm:continue
        assert sm.get_path_name().startswith('/Game/Terrarium/Meshes/')
        n=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
        if n<=0:continue
        counts[sm.get_name()]+=n
        for i in range(c.get_num_materials()):
            m=c.get_material(i);assert m and not m.get_editor_property('two_sided')
            materials.add(m.get_path_name())
manifest=root/'Docs/Fidelity/Details/current-layout.json'
if not manifest.exists():manifest=root/'Docs/Fidelity/pass-5-layout.json'
expected=json.loads(manifest.read_text())['counts']
assert dict(counts)=={'SM_'+k:v for k,v in expected.items()},dict(counts)
normals={}
for name in counts:
    r=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
    assert r['saved_normal_errors']==0 and r['visual_review'].startswith('passed')
    authorization=root/'Docs/Fidelity/iteration-authorization.json'
    assert r['refinement_pass']<=3 or (authorization.exists() and json.loads(authorization.read_text()).get('iteration_limits_lifted') is True)
    normals[name]={'triangles':r['triangles'],'asset_refinement_pass':r['refinement_pass'],'saved_normal_errors':0}
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
pp=scene['Baseline_FixedExposure_EV12'].settings
assert pp.auto_exposure_method==unreal.AutoExposureMethod.AEM_MANUAL
ev=math.log2(pp.depth_of_field_fstop**2*pp.camera_shutter_speed*100/pp.camera_iso)
cvars={n:unreal.SystemLibrary.get_console_variable_int_value(n) for n in ['r.DynamicGlobalIlluminationMethod','r.ReflectionMethod','r.GenerateMeshDistanceFields','r.Lumen.DiffuseIndirect.Allow','r.Lumen.Reflections.Allow','r.Shadow.Virtual.Enable']}
assert all(v==1 for v in cvars.values())
cache=unreal.SystemLibrary.get_console_variable_float_value('r.EyeAdaptation.CachedLightingPreExposure')
assert cache-12<=ev-pp.auto_exposure_bias<=cache+8
camera=scene['Baseline_Orthographic_Review'];cc=camera.camera_component
assert cc.projection_mode==unreal.CameraProjectionMode.ORTHOGRAPHIC
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
report={'project':unreal.Paths.get_project_file_path(),'engine':unreal.SystemLibrary.get_engine_version(),'map':'/Game/Terrarium/Maps/HomesteadFidelity','saved_and_reopened':True,'unique_meshes':len(counts),'placements':sum(counts.values()),'counts':dict(counts),'meshes':normals,'materials':sorted(materials),'camera':{'orthographic_width':cc.ortho_width,'aspect':cc.aspect_ratio,'rotation':str(camera.get_actor_rotation())},'exposure':{'manual_ev100':ev,'compensation':pp.auto_exposure_bias,'cached_lighting_pre_exposure':cache},'lumen_cvars':cvars,'broad_scene_passes':json.loads(manifest.read_text()).get('broad_visual_pass',5),'pixel_parity':'not proven by these structural checks; see comparison-metrics.json'}
(root/'Docs/Fidelity/editor-validation.json').write_text(json.dumps(report,indent=2))
unreal.log('FIDELITY_SAVED_REOPENED_VALIDATED')
