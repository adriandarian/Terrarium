import unreal
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
s=(R/'Scripts/WorldExpansion/observe_play.py').read_text();s=s.replace("OUT = ROOT / 'Docs/WorldExpansion'","OUT = ROOT / 'Docs/WorldExpansion/V6'").replace('_world_expansion_traversal_runner','_world_expansion_v6_traversal_runner').replace('_world_expansion_observer','_world_expansion_v6_observer')
exec(compile(s,'v6_observation','exec'))
