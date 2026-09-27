import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
l=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
def v(x):return [round(x.x,3),round(x.y,3),round(x.z,3)]
rows=[]
for o in a.get_all_level_actors():
 comps=[]
 for c in o.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh:
   b=c.static_mesh.get_bounding_box()
   comps.append({'mesh':c.static_mesh.get_path_name(),'local_min':v(b.min),'local_max':v(b.max),'instances':c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1})
 r=o.get_actor_rotation();b=o.get_actor_bounds(False)
 row={'label':o.get_actor_label(),'class':o.get_class().get_name(),'loc':v(o.get_actor_location()),'scale':v(o.get_actor_scale3d()),'rot':[r.pitch,r.yaw,r.roll],'center':v(b[0]),'extent':v(b[1]),'components':comps}
 if isinstance(o,unreal.CameraActor):row['camera']={'projection':str(o.camera_component.projection_mode),'width':o.camera_component.ortho_width}
 rows.append(row)
report={'project':str(root),'level':str(l.get_current_level()),'dirty':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'actors':rows}
(root/'Docs/SceneAssembly/live-inspection.json').write_text(json.dumps(report,indent=2))
