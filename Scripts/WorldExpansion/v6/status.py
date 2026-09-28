import unreal,json
from pathlib import Path
r=getattr(unreal,'_world_expansion_v6_traversal_runner',None)
out={'exists':r is not None}
if r:out.update({'finished':r.finished,'index':r.index,'route':r.route['name'] if hasattr(r,'route') else None,'waypoint':r.waypoint,'results':r.results,'pawn':str(r.pawn.get_actor_location()) if r.pawn else None})
(Path(unreal.Paths.project_dir())/'Docs/WorldExpansion/V6/traversal-status.json').write_text(json.dumps(out,indent=2))
