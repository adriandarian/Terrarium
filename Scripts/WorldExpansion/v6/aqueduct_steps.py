"""Create a supported, stepped descent instead of an unwalkably steep trail."""
import unreal,json,math
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
s=(R/'Scripts/WorldExpansion/v6/landmarks.py').read_text();exec(compile(s[:s.index('\nrecords=[]')],'landmark_helpers','exec'))
mats['stone']=unreal.load_asset('/Game/Terrarium/WorldExpansion/V6/Materials/M_CutMasonry')
points=[[-225,390],[-205,425],[-205,445],[-195,469],[-195,490]];width=2.4;vs=[];ts=[];uv=[];center=[];prev=None
def face(p):
 n=len(vs);vs.extend(p);uv.extend([[q[0]/2,q[1]/2] for q in p]);ts.extend([[n,n+i,n+i+1] for i in range(1,len(p)-1)])
for a,b in zip(points,points[1:]):
 dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);nx=-dy/ln*width/2;ny=dx/ln*width/2;n=math.ceil(ln/.28)
 for i in range(n):
  aa=[a[0]+dx*i/n,a[1]+dy*i/n];bb=[a[0]+dx*(i+1)/n,a[1]+dy*(i+1)/n]
  quad=[[aa[0]-nx,aa[1]-ny],[bb[0]-nx,bb[1]-ny],[bb[0]+nx,bb[1]+ny],[aa[0]+nx,aa[1]+ny]];heights=[ground(*p) for p in quad];top=max(heights)+.04
  if prev is not None:top=max(top,prev-.175)
  low=min(heights)-.15;prev=top;p=[q+[low] for q in quad]+[q+[top] for q in quad]
  for f in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:face([p[j] for j in f])
  center.append([(aa[0]+bb[0])/2,(aa[1]+bb[1])/2,top])
source={'vertices':vs,'triangles':ts,'uv0':uv};(R/'SourceAssets/WorldExpansion/V6/AqueductStepsR3.json').write_text(json.dumps(source));actor=meshactor('AqueductStepsR3',source,'stone')
prior=actors.get('WX6_AqueductStepsR2')
if prior:
 prior.static_mesh_component.set_visibility(False);prior.static_mesh_component.set_hidden_in_game(True);prior.static_mesh_component.set_collision_profile_name('NoCollision');prior.set_actor_hidden_in_game(True)
old=actors['WX6_AqueductTrail'];old.static_mesh_component.set_visibility(False);old.static_mesh_component.set_hidden_in_game(True);old.static_mesh_component.set_collision_profile_name('NoCollision');old.set_actor_hidden_in_game(True)
receipt=json.loads((D/'landmark-integration.json').read_text());q=next(p for p in receipt['paths'] if p['name']=='AqueductTrail');q['points']=points;q['native_ground_centerline']=center;q['construction']='Supported masonry steps, maximum 17.5cm descent per tread';q['mesh_name']='AqueductStepsR3'
(D/'landmark-integration.json').write_text(json.dumps(receipt,indent=2));assert L.save_current_level();print('Aqueduct descent',len(center),'treads')

