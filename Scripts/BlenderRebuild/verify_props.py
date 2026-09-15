import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(),'Inspect unsaved map changes before reloading'
levels.eject_pilot_level_actor();assert levels.load_level('/Game/Terrarium/Blender/Maps/HomesteadBlender')
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};rows=[]
for key,label in [('Cottage','Reference_Cottage'),('Lantern','Reference_Lantern'),('Sign','Blender_Sign_Courtyard')]:
    ob=scene[label];mesh=ob.static_mesh_component.static_mesh;path='/Game/Terrarium/Blender/'+key
    assert mesh.get_path_name()==path+'/SM_Blender_'+key+'.SM_Blender_'+key
    assert mesh.get_material(0).get_path_name()==path+'/M_'+key+'.M_'+key
    assert len(mesh.static_materials)==1
    p=ob.get_actor_location();s=ob.get_actor_scale3d()
    rows.append({'asset':key,'reopened_binding':True,'mesh':mesh.get_path_name(),'material':mesh.get_material(0).get_path_name(),'location':[p.x,p.y,p.z],'scale':[s.x,s.y,s.z]})
levels.pilot_level_actor(scene['Blender_Props_Review']);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
(root/'Docs/BlenderRebuild/Props/saved-world-verification.json').write_text(json.dumps({'world':'/Game/Terrarium/Blender/Maps/HomesteadBlender','assets':rows,'fidelity':'not_complete'},indent=2))
