import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadPilot/Maps/StartingHome.' in str(L.get_current_level())
changes=[]
for a in A.get_all_level_actors():
 if isinstance(a,unreal.SkyLight):
  before=a.light_component.get_editor_property('intensity');a.light_component.set_intensity(2.7);changes.append({'actor':a.get_actor_label(),'property':'sky_intensity','before':before,'after':2.7})
 if isinstance(a,unreal.DirectionalLight):
  before=a.light_component.get_editor_property('light_source_angle');a.light_component.set_editor_property('light_source_angle',3.);changes.append({'actor':a.get_actor_label(),'property':'source_angle','before':before,'after':3.})
assert L.save_current_level()
(R/'Docs/HomesteadPilot/lighting.json').write_text(json.dumps({'scope':'Pilot level light components only; shared materials unchanged','changes':changes},indent=2))
