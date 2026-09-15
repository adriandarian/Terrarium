"""Replace exactly two mesh references at their saved transforms.

This is the second per-asset detail pass for shed/bridge. It does not perform
another broad scene, camera, layout, or lighting refinement.
"""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
changes=[]
def pose(a):
    p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
    return [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]
for a in actors.get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor):continue
    comp=a.static_mesh_component
    if not comp.static_mesh:continue
    old=comp.static_mesh.get_name()
    new={'SM_Shed':'SM_Shed_v2','SM_PlankBridge':'SM_PlankBridge_v2','SM_Shed_v2':'SM_Shed_v2','SM_PlankBridge_v2':'SM_PlankBridge_v2'}.get(old)
    if not new:continue
    report=json.loads((root/'Docs/Phase1/Validation'/(new+'.json')).read_text())
    assert report['saved_normal_errors']==0 and report['visual_review'].startswith('passed')
    before=pose(a)
    comp.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/'+new))
    # There were no actor material overrides on these two original placements.
    comp.set_material(0,unreal.load_asset('/Game/Terrarium/Materials/M_WeatheredDetails'))
    after=pose(a)
    assert before==after
    # Struct string repr includes an address, so compare actual coordinates.
    changes.append({'actor':a.get_actor_label(),'previous_mesh':old,'mesh':new,'pose_before':before,'pose_after':after,'transform_unchanged':True})
assert len(changes)==2,changes
bridge=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Fidelity_PlankBridge_001')
origin,extent=bridge.get_actor_bounds(False)
assert origin.z-extent.z<0,'Bridge piles do not reach the river'
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
camera=scene['Baseline_Orthographic_Review']
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
p=root/'Docs/Fidelity/Details'
(p/'integration.json').write_text(json.dumps({'changes':changes,'bridge_pile_bottom_world_z':origin.z-extent.z,'water_surface_z':0,'broad_scene_passes':5,'asset_detail_pass':2},indent=2))
layout=json.loads((root/'Docs/Fidelity/pass-5-layout.json').read_text())
for old,new in [('Shed','Shed_v2'),('PlankBridge','PlankBridge_v2')]:layout['counts'][new]=layout['counts'].pop(old)
layout['asset_detail_revision']='shed and bridge pass 2, unchanged actor transforms'
(p/'current-layout.json').write_text(json.dumps(layout,indent=2))
