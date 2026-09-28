"""Verify the serialized pilot level, instanced replacements and unchanged baseline."""
import unreal,json,hashlib,collections
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);assert not editor.get_game_world()
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LEVEL='/Game/Terrarium/HomesteadPilot/Maps/StartingHome'

def grass_state():
 rows=[]
 for a in A.get_all_level_actors():
  for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
   if not c.static_mesh or c.static_mesh.get_name()!='SM_Blender_GrassTerrain':continue
   assert c.get_editor_property('visible') and not c.get_editor_property('hidden_in_game')
   assert not a.is_temporarily_hidden_in_editor() and not a.get_editor_property('hidden')
   assert c.get_material(0)
   for i in range(c.get_instance_count()):
    t=c.get_instance_transform(i,world_space=True);p=t.translation;s=t.scale3d;q=t.rotation
    rows.append([round(v,5) for v in (p.x,p.y,p.z,s.x,s.y,s.z,q.x,q.y,q.z,q.w)])
 assert len(rows)==5841,('Missing retained grass terrain',len(rows))
 return {'count':len(rows),'visible':True,'transform_hash':hashlib.sha256(json.dumps(sorted(rows)).encode()).hexdigest()}
def snapshot():
 counts=collections.Counter();labels={};transforms=collections.defaultdict(list)
 for a in A.get_all_level_actors():
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   mesh=c.static_mesh
   if mesh and mesh.get_path_name().startswith('/Game/Terrarium/HomesteadPilot/'):
    count=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
    counts[mesh.get_path_name()]+=count
    labels[a.get_actor_label()]={'mesh':mesh.get_path_name(),'instances':count}
    ts=[c.get_instance_transform(i,world_space=True) for i in range(count)] if isinstance(c,unreal.InstancedStaticMeshComponent) else [c.get_world_transform()]
    for t in ts:
     p=t.translation;s=t.scale3d;q=t.rotation
     transforms[mesh.get_path_name()].append([round(v,5) for v in (p.x,p.y,p.z,s.x,s.y,s.z,q.x,q.y,q.z,q.w)])
 hashes={key:hashlib.sha256(json.dumps(sorted(rows)).encode()).hexdigest() for key,rows in transforms.items()}
 return dict(counts),labels,hashes
before,labels,before_hashes=snapshot();assert len(before)==11,(len(before),before)
grass_before=grass_state()
assert L.save_current_level();L.eject_pilot_level_actor()
assert L.load_level('/Game/Terrarium/Calibration/Maps/ConceptScaleBlockout')
assert L.load_level(LEVEL)
after,after_labels,after_hashes=snapshot();assert after==before,(before,after)
assert after_hashes==before_hashes,'Pilot instance transforms changed on reload'
grass_after=grass_state();assert grass_after==grass_before,'Retained grass terrain changed on reload'
for required in ('Reference_Cottage','HP_Bridge_0','HP_Bridge_1','HP_TerraceStairs','HP_KitchenGarden','HP_EntryLanding','HP_UpperTerraceModule'):
 assert required in after_labels,required
scene={a.get_actor_label():a for a in A.get_all_level_actors()}
assert 'HP_InteriorWarmLight' in scene and 'HP_PlayerStart' in scene
baseline=R/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap'
expected=json.loads((R/'Docs/HomesteadPilot/working-level.json').read_text())['baseline_sha256']
actual=hashlib.sha256(baseline.read_bytes()).hexdigest();assert actual==expected
cam=scene['HP_ExplorationView'];L.pilot_level_actor(cam);L.set_exact_camera_view(True);L.editor_set_game_view(True);A.set_selected_level_actors([])
(R/'Docs/HomesteadPilot/reopen-verification.json').write_text(json.dumps({'level':LEVEL,'saved_and_reopened':True,'pilot_mesh_families':len(after),'instances_by_mesh':after,'transform_hashes':after_hashes,'transforms_unchanged':True,'baseline_map_unchanged':True,'baseline_sha256':actual,'interior_light_and_player_start_present':True,'scope':'Actual map serialization and component mesh persistence, including foliage instances; runtime and visual checks reported separately'},indent=2))
(R/'Docs/HomesteadPilot/grass-reopen-verification.json').write_text(json.dumps({'saved_and_reopened':True,'grass':grass_after,'scope':'Retained terrain presence, visibility and transforms; inspect the final exported image separately'},indent=2))
