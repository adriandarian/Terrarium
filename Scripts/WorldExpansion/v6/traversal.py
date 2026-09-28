import unreal
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
s=(R/'Scripts/WorldExpansion/validate_traversal.py').read_text();s=s.replace("OUT = ROOT / 'Docs/WorldExpansion'","OUT = ROOT / 'Docs/WorldExpansion/V6'").replace('_world_expansion_traversal_runner','_world_expansion_v6_traversal_runner')
exec(compile(s,'v6_traversal','exec'))
