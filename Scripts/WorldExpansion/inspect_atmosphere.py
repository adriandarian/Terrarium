import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve()
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=[]
for a in A.get_all_level_actors():
 if isinstance(a,unreal.DirectionalLight):
  c=a.light_component
  rows.append({'label':a.get_actor_label(),'kind':'sun','intensity':c.intensity,'atmosphere_sun_light':c.get_editor_property('atmosphere_sun_light'),'hidden':a.is_hidden_ed()})
 if isinstance(a,unreal.ExponentialHeightFog):
  c=a.component
  rows.append({'label':a.get_actor_label(),'kind':'fog','density':c.get_editor_property('fog_density'),'falloff':c.get_editor_property('fog_height_falloff'),'start':c.get_editor_property('start_distance')})
(R/'Docs/WorldExpansion/atmosphere-before.json').write_text(json.dumps(rows,indent=2))
