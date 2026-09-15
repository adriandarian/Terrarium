"""Read the saved working map and verify every documented Blender placement."""
import unreal,json,re
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild';world_path='/Game/Terrarium/Blender/Maps/HomesteadBlender'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
levels.eject_pilot_level_actor();assert levels.load_level(world_path)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};bindings=[]
for folder in sorted(out.iterdir()):
    path=folder/'world-placement.json'
    if not path.exists():continue
    record=json.loads(path.read_text())
    if record.get('world',record.get('level'))!=world_path:continue
    key=folder.name;ob=scene[record['actor']];mesh=ob.static_mesh_component.static_mesh;base='/Game/Terrarium/Blender/'+key
    assert mesh.get_path_name()==base+'/SM_Blender_'+key+'.SM_Blender_'+key
    expected_materials=record.get('materials',[base+'/M_'+key+'.M_'+key])
    assert len(mesh.static_materials)==len(expected_materials)
    assert [mesh.get_material(i).get_path_name() for i in range(len(mesh.static_materials))]==expected_materials
    p=ob.get_actor_location();actual=[p.x,p.y,p.z]
    expected_position=record.get('location_cm')
    if expected_position is None:expected_position=[float(re.search(axis+r':\s*(-?[\d.]+)',record['location']).group(1)) for axis in ['x','y','z']]
    assert len(expected_position)==3 and all(abs(v-e)<.02 for v,e in zip(actual,expected_position))
    if isinstance(record.get('scale'),(int,float)):
        s=ob.get_actor_scale3d();assert all(abs(v-record['scale'])<.0001 for v in [s.x,s.y,s.z])
    if 'yaw' in record:
        r=ob.get_actor_rotation();assert abs((r.yaw-record['yaw']+180)%360-180)<.001 and abs(r.pitch)+abs(r.roll)<.001
    bindings.append({'asset':key,'actor':ob.get_actor_label(),'mesh':mesh.get_path_name(),'material':mesh.get_material(0).get_path_name(),'location_cm':actual})
lodge=scene['Blender_Lodge_UpperTerrace'];ignored=[a for a in actors.get_all_level_actors() if a!=lodge];probes=[]
for j in range(3):
    # Masonry has a 6 mm joint allowance; probe a block face away from the center seam.
    x=-2170+(1.89+j*.29)*85;y=-140-.12*85;expected=880+(.22*(3-j)-.003)*85
    above=unreal.SystemLibrary.line_trace_single(lodge,unreal.Vector(x,y,1000),unreal.Vector(x,y,expected+.05),unreal.TraceTypeQuery.ECC_VISIBILITY,False,ignored,unreal.DrawDebugTrace.NONE,ignore_self=False)
    below=unreal.SystemLibrary.line_trace_single(lodge,unreal.Vector(x,y,1000),unreal.Vector(x,y,expected-.05),unreal.TraceTypeQuery.ECC_VISIBILITY,False,ignored,unreal.DrawDebugTrace.NONE,ignore_self=False)
    assert above is None and below is not None,('Stair collision differs from modeled surface',j,str(above),str(below))
    probes.append({'step':j+1,'expected_top_cm':expected,'collision_top_tolerance_cm':.05,'clear_above':above is None,'blocked_below':below is not None,'passed':True})
review_key=(root/'Saved/blender-import-asset.txt').read_text().strip()
review_path=out/review_key/'world-placement.json'
review_record=json.loads(review_path.read_text()) if review_path.exists() else {'camera':'Blender_Environment_Shrubs_Review'}
levels.pilot_level_actor(scene[review_record.get('camera','Blender_Lodge_Review')]);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
(out/'saved-world-verification.json').write_text(json.dumps({'world':world_path,'bindings':bindings,'lodge_stair_probes':probes,'limits':'Static point traces only; full character movement and performance not tested.','fidelity':'not_complete'},indent=2))
