"""Rerun the existing collision traversal, keeping its historical receipt intact."""
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir()).resolve()
assert root==Path('C:/Users/hello/Projects/Terrarium')
path=root/'Scripts/HomesteadPilot/Runtime/validate_traversal.py'
source=path.read_text()
old="(OUT / 'traversal-receipt.json').write_text"
assert source.count(old)==1
source=source.replace(old,"(ROOT / 'Docs/HomesteadPilot/Completion/traversal-receipt.json').write_text")
exec(compile(source,str(path),'exec'),{})
