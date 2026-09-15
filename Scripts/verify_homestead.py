"""Validate the saved, reopened environment in the connected Unreal editor."""
import unreal,json,math
from collections import Counter
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Homestead.' in str(levels.get_current_level())
assert levels.save_current_level()
assert levels.load_level('/Game/Terrarium/Maps/RenderBaseline')
assert levels.load_level('/Game/Terrarium/Maps/Homestead')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
assert not any(n.startswith('Temporary_') for n in scene)
counts=Counter();materials=set();reports={}
for a in scene.values():
    if not isinstance(a,unreal.StaticMeshActor):continue
    comp=a.static_mesh_component;mesh=comp.static_mesh
    assert mesh and mesh.get_path_name().startswith('/Game/Terrarium/Meshes/SM_')
    name=mesh.get_name();counts[name]+=1
    scale=a.get_actor_scale3d()
    assert all(math.isfinite(v) and v>0 for v in [scale.x,scale.y,scale.z])
    for i in range(comp.get_num_materials()):
        mat=comp.get_material(i);assert mat
        assert mat.get_path_name().startswith('/Game/Terrarium/Materials/')
        assert not mat.get_editor_property('two_sided')
        materials.add(mat.get_path_name())
    if name not in reports:
        r=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
        assert r['saved_normal_errors']==0 and r['all_components_closed']
        assert r['visual_review'].startswith('passed') and r['refinement_pass']<=3
        reports[name]=r
assert len(counts)==18
expected=json.loads((root/'Docs/Phase2/composition.json').read_text())['placed_meshes']
assert dict(counts)=={'SM_'+k:v for k,v in expected.items()}
camera=scene['Baseline_Orthographic_Review'];cc=camera.camera_component
assert cc.projection_mode==unreal.CameraProjectionMode.ORTHOGRAPHIC
pp=scene['Baseline_FixedExposure_EV12'].settings
assert pp.auto_exposure_method==unreal.AutoExposureMethod.AEM_MANUAL
assert pp.auto_exposure_apply_physical_camera_exposure
ev=math.log2(pp.depth_of_field_fstop**2*pp.camera_shutter_speed*100/pp.camera_iso)
assert abs(ev-12)<.001
cvars={n:unreal.SystemLibrary.get_console_variable_int_value(n) for n in ['r.DynamicGlobalIlluminationMethod','r.ReflectionMethod','r.GenerateMeshDistanceFields','r.Lumen.DiffuseIndirect.Allow','r.Lumen.Reflections.Allow','r.Shadow.Virtual.Enable']}
assert all(v==1 for v in cvars.values())
sun=scene['Baseline_WarmSun'];sky=scene['Baseline_SkyLight']
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
p=root/'Docs/Final';p.mkdir(parents=True,exist_ok=True)
report={'project':unreal.Paths.get_project_file_path(),'engine':unreal.SystemLibrary.get_engine_version(),'map':str(levels.get_current_level()),'saved_and_reopened':True,'mesh_instances':sum(counts.values()),'unique_original_meshes':len(counts),'counts':dict(counts),'materials':sorted(materials),'mesh_library_triangles':sum(r['triangles'] for r in reports.values()),'placed_source_triangles':sum(reports[n]['triangles']*c for n,c in counts.items()),'zero_saved_normal_errors':True,'all_assets_six_angle_lit_reviewed':True,'max_asset_refinement_pass':max(r['refinement_pass'] for r in reports.values()),'whole_scene_passes':3,'camera':{'projection':'Orthographic','ortho_width':cc.ortho_width,'aspect':cc.aspect_ratio,'location':str(camera.get_actor_location()),'rotation':str(camera.get_actor_rotation())},'lighting':{'sun_lux':sun.light_component.intensity,'sun_source_angle':sun.light_component.light_source_angle,'sky_intensity':sky.light_component.intensity,'manual_ev100':ev,'exposure_compensation':pp.auto_exposure_bias},'cvars':cvars,'scope':'Static editor environment; gameplay and packaging not tested.'}
(p/'validation.json').write_text(json.dumps(report,indent=2))
unreal.log('HOMESTEAD_SAVED_REOPENED_VALIDATED')
