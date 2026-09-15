"""Compare the other task's preserved map with the already verified environment."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
preserved=json.loads((root/'Saved/plaster-map-preservation.json').read_text())
expected=json.loads((out/'scene-state.json').read_text())['bindings']
def vec(v):return [v.x,v.y,v.z]
def snapshot():
    rows=[];cameras=[]
    for a in actors.get_all_level_actors():
        if isinstance(a,unreal.CameraActor):cameras.append(a.get_actor_label())
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh or c.static_mesh.get_name()=='MatineeCam_SM':continue
            ts=[c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count())] if isinstance(c,unreal.InstancedStaticMeshComponent) else [a.get_actor_transform()]
            values=[[*vec(t.translation),t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w,*vec(t.scale3d)] for t in ts]
            rows.append({'mesh':c.static_mesh.get_path_name(),'materials':[c.get_material(i).get_path_name() for i in range(c.get_num_materials())],'transforms':sorted(values)})
    return sorted(rows,key=lambda r:(r['mesh'],str(r['transforms']))),cameras
levels.eject_pilot_level_actor();assert levels.load_level(preserved['restore'])
backup,cameras=snapshot();assert backup==expected,'Preserved map has unaccounted scene edits; inspect before proceeding'
assert levels.load_level('/Game/Terrarium/Maps/HomesteadReference')
original,original_cameras=snapshot();assert original==expected,'Original no longer equals the verified saved scene'
(out/'editor-coordination.json').write_text(json.dumps({'preservation_map':preserved['restore'],'backup_matches_verified_scene':True,'saved_map_matches_verified_scene':True,'backup_cameras':cameras,'saved_cameras':original_cameras,'scene_changes_lost':False},indent=2))
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
