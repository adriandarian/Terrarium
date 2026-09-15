"""Check all modeled plank surfaces and a character-sized capsule through the rail corridor."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/RiverBridge';r=json.loads((folder/'world-placement.json').read_text())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);scene={a.get_actor_label():a for a in actors.get_all_level_actors()};ob=scene[r['actor']]
assert ob.static_mesh_component.static_mesh.get_path_name()==r['mesh']
ignored=[a for a in actors.get_all_level_actors() if a!=ob];s=r['scale'];p=r['location_cm'];ang=math.radians(r['yaw']);co=math.cos(ang);si=math.sin(ang)
def world(x,y,z):return unreal.Vector(p[0]+(x*co-y*si)*s,p[1]+(x*si+y*co)*s,z)
probes=[]
for i in range(10):
    y=-(-142+i*31.5);a=world(0,y,500)
    above=unreal.SystemLibrary.line_trace_single(ob,a,world(0,y,r['deck_top_cm']+.04),unreal.TraceTypeQuery.ECC_VISIBILITY,False,ignored,unreal.DrawDebugTrace.NONE,ignore_self=False)
    below=unreal.SystemLibrary.line_trace_single(ob,a,world(0,y,r['deck_top_cm']-.04),unreal.TraceTypeQuery.ECC_VISIBILITY,False,ignored,unreal.DrawDebugTrace.NONE,ignore_self=False)
    assert above is None and below is not None,('Plank collision mismatch',i)
    probes.append({'plank':i+1,'top_cm':r['deck_top_cm'],'tolerance_cm':.04,'passed':True})
start=world(0,142,r['deck_top_cm']+90);end=world(0,-141.5,r['deck_top_cm']+90)
hit=unreal.SystemLibrary.capsule_trace_single(ob,start,end,34,88,unreal.TraceTypeQuery.ECC_VISIBILITY,False,ignored,unreal.DrawDebugTrace.NONE,ignore_self=False)
assert hit is None,'Rail corridor obstructs a 68 cm wide, 176 cm tall capsule'
(folder/'collision-verification.json').write_text(json.dumps({'plank_probes':probes,'capsule_corridor_clear':True,'capsule_radius_cm':34,'capsule_half_height_cm':88,'limits':'Static sweeps and point traces against the bridge only. No character movement, step-up behavior, bank approach sweep or performance test.'},indent=2))
unreal.log('BLENDER_BRIDGE_COLLISION_VERIFIED')
