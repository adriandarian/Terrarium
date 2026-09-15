"""Apply reviewed second-pass garden/stair meshes at saved scene transforms."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mapping={'SM_GardenBed':'SM_GardenBed_v2','SM_StoneStairs':'SM_StoneStairs_v2'}
for name in mapping.values():
    r=json.loads((root/'Docs/Phase1/Validation'/(name+'.json')).read_text())
    assert r['saved_normal_errors']==0 and r['visual_review'].startswith('passed')
changes=[]
def pose(a):
    p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
    return [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]
for a in actors.get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor):continue
    c=a.static_mesh_component
    if not c.static_mesh:continue
    old=c.static_mesh.get_name();new=mapping.get(old)
    if not new:continue
    before=pose(a)
    c.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/'+new))
    assert pose(a)==before
    changes.append({'actor':a.get_actor_label(),'old_mesh':old,'new_mesh':new,'pose':before,'transform_unchanged':True})
assert len(changes)==3,changes
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
p=root/'Docs/Fidelity/Details'
layout=json.loads((p/'current-layout.json').read_text())
for old,new in [('GardenBed','GardenBed_v2'),('StoneStairs','StoneStairs_v2')]:layout['counts'][new]=layout['counts'].pop(old)
layout['asset_detail_revision']='shed, bridge, wheat, garden and stairs pass 2; existing placement transforms retained'
(p/'current-layout.json').write_text(json.dumps(layout,indent=2))
(p/'garden-stairs-integration.json').write_text(json.dumps({'changes':changes,'asset_detail_pass':2},indent=2))
