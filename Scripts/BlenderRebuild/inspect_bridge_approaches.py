"""Bracket actual collision surface heights at the two existing bank approaches."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
record=json.loads((root/'Docs/BlenderRebuild/RiverBridge/world-placement.json').read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert record['world']+'.' in world.get_path_name()
p=record['location_cm'];a=math.radians(record['yaw']);result=[]
for along in [-420,-365,-330,330,365,420]:
    x=p[0]-along*math.sin(a);y=p[1]+along*math.cos(a)
    def blocked(endz):return unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,600),unreal.Vector(x,y,endz),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[],unreal.DrawDebugTrace.NONE) is not None
    if not blocked(0):result.append({'along_cm':along,'xy_cm':[x,y],'surface_cm':None});continue
    low=0.;high=600.
    for _ in range(16):
        mid=(low+high)*.5
        if blocked(mid):low=mid
        else:high=mid
    result.append({'along_cm':along,'xy_cm':[x,y],'surface_cm':(low+high)*.5,'tolerance_cm':.01})
(root/'Docs/BlenderRebuild/RiverBridge/approach-heights.json').write_text(json.dumps(result,indent=2))
