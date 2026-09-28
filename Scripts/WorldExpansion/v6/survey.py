import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=E.get_editor_world()
assert R==Path('C:/Users/hello/Projects/Terrarium');assert w.get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion';assert not E.get_game_world()
ignored=[a for a in A.get_all_level_actors() if not a.get_actor_label().startswith('WX6_Terrain6_')]
pts=[(x,y) for x in [50,55,60,65,70,75,80,85,95,110,140,170,200,215] for y in [-290,-280,-270,-260,-250]]+[(x,y) for x in [-200,-190,-180,-170] for y in [470,480,490,500]]
out=[]
for x,y in pts:
 h=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x*100,y*100,90000),unreal.Vector(x*100,y*100,-3000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignored,unreal.DrawDebugTrace.NONE,False)
 h=h if isinstance(h,unreal.HitResult) else next((q for q in (h or []) if isinstance(q,unreal.HitResult)),None);t=h.to_tuple() if h else None
 if t and t[0]:out.append({'x':x,'y':y,'z':t[5].z/100,'normal_z':t[7].z})
(R/'Docs/WorldExpansion/V6/site-survey.json').write_text(json.dumps(out,indent=2))
