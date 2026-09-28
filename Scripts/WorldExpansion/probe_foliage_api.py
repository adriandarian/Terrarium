import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve()
(R/'Docs/WorldExpansion/foliage-api.json').write_text(json.dumps({n:str(getattr(unreal.InstancedFoliageActor,n).__doc__) for n in dir(unreal.InstancedFoliageActor) if 'foliage' in n.lower() or 'instance' in n.lower()},indent=2))
