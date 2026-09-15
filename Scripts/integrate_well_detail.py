"""Install the reviewed open garden structure at its existing scene transform."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
root=Path(unreal.Paths.project_dir())
r=json.loads((root/'Docs/Phase1/Validation/SM_GardenWell_v2.json').read_text())
assert r['saved_normal_errors']==0 and r['visual_review'].startswith('passed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
matches=[a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_GardenWell']
assert len(matches)==1
a=matches[0];p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
pose=[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]
a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/SM_GardenWell_v2'))
assert levels.save_current_level()
layout=json.loads((root/'Docs/Fidelity/Details/current-layout.json').read_text())
layout['counts']['GardenWell_v2']=layout['counts'].pop('GardenWell')
layout['asset_detail_revision']='open garden well pass 2 and larger cliff courses pass 3'
(root/'Docs/Fidelity/Details/current-layout.json').write_text(json.dumps(layout,indent=2))
(root/'Docs/Fidelity/Structures/well-integration.json').write_text(json.dumps({'actor':a.get_actor_label(),'new_mesh':'SM_GardenWell_v2','pose':pose,'asset_refinement_pass':2,'instances':1},indent=2))
