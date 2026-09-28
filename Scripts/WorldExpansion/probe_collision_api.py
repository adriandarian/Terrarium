import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve()
names=[n for n in dir(unreal) if 'Sphyl' in n or 'AggregateGeom' in n or 'BoxElem' in n]
mesh=unreal.load_asset('/Game/Terrarium/HomesteadPilot/Landscape/Meshes/SM_BroadTree5m')
body=mesh.get_editor_property('body_setup')
data={n:str(getattr(unreal,n).__doc__) for n in names}
data['body']=str(body);data['trace_flag']=str(body.get_editor_property('collision_trace_flag'))
data['aggregate']=str(body.get_editor_property('agg_geom'));data['bounds']=str(mesh.get_bounding_box())
(R/'Docs/WorldExpansion/collision-api.json').write_text(json.dumps(data,indent=2))
