import unreal
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
s=(R/'Scripts/WorldExpansion/snapshot_world.py').read_text();s=s.replace("OUT = ROOT / 'Docs/WorldExpansion'","OUT = ROOT / 'Docs/WorldExpansion/V6'")
exec(compile(s,'v6_snapshot','exec'))
