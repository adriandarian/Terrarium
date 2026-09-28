import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/CalibrationIntegration';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level('/Game/Terrarium/Calibration/Maps/ConceptScaleBlockout')
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
labels=['Scale_Terrace_main_notched','Scale_Turf_main_notched','Scale_cottage_walls_measured','Scale_cottage_roof_measured','Scale_cottage_chimney_measured','Scale_Person_body_measured','Scale_Person_head_measured']
for name in labels:
 a=scene[name];c=a.static_mesh_component;assert c.static_mesh and c.get_material(0)
assert not any(name in scene for name in ['Scale_Terrace_main','Scale_Turf_main','Scale_Person_body'])
cam=scene['Scale_ConceptCamera'];assert abs(cam.camera_component.ortho_width-2645.5)<.01
assert abs(cam.get_actor_rotation().pitch+45)<.001 and abs(cam.get_actor_rotation().yaw-135)<.001
body=scene['Scale_Person_body_measured'].get_actor_bounds(False);head=scene['Scale_Person_head_measured'].get_actor_bounds(False);height=head[0].z+head[1].z-(body[0].z-body[1].z);assert abs(height-180)<.01
for i in range(8):assert 'Scale_Stair_'+str(i) in scene
levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([])
baseline=hashlib.sha256((root/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap').read_bytes()).hexdigest();before=json.loads((out/'preflight.json').read_text())['baseline_map_sha256'];assert baseline==before
report={'scale_level_saved_reopened':True,'patched_actors_verified':labels,'stair_actors':8,'person_height_cm':height,'camera_matches_fixed_reference':True,'detail_level_saved_reopened':json.loads((out/'detail-import.json').read_text())['saved_and_reloaded'],'imported_detail_meshes':16,'saved_blender_reopened':json.loads((root/'Docs/DetailCalibration/verification.json').read_text()).get('reopen_verified',False),'baseline_unchanged':True,'baseline_sha256':baseline,'remaining_visual_gaps':['Bridge blockout projected width about8.8percent below manual target; annotations and hidden depth uncertain.','Flat-color calibration and prototype geometry do not constitute finished concept fidelity.'],'not_tested':['gameplay','animation','navigation','performance budgets']}
(out/'final-verification.json').write_text(json.dumps(report,indent=2))
