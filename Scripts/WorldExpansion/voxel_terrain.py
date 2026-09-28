"""Source-only stepped Terrarium terrain. Original maps and binary assets untouched.

Real horizontal shelves, vertical risers and projecting broken stone courses;
not a low-poly heightfield with a pixel shader. Source metres; UVs every 2 m.
The previous exact triangles remain in protected traversal corridors.
"""
import math
import json
import hashlib
from pathlib import Path
import terrain_source as previous

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'SourceAssets/WorldExpansion/TerrainV5'
BASE=ROOT/'SourceAssets/WorldExpansion/Terrain'
CELL=5
N=320
HEIGHTS={}
BASE_MANIFEST=json.loads((BASE/'manifest.json').read_text())
for row in BASE_MANIFEST['assets']:
    if row['name'].startswith('Terrain_'):
        data=json.loads((ROOT/row['source']).read_text())
        HEIGHTS.update({(p[0],p[1]):p[2] for p in data['vertices']})

def smooth(a,b,v):
    t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)

def noise(i,j,s=0):
    n=(i*374761393+j*668265263+s*982451653)&0xffffffff
    n=((n^(n>>13))*1274126177)&0xffffffff
    return ((n^(n>>16))&0xffffffff)/4294967295

def original(x,y):
    i=min(319,max(0,math.floor((x+800)/5)));j=min(319,max(0,math.floor((y+800)/5)))
    x0=-800+i*5;y0=-800+j*5;fx=(x-x0)/5;fy=(y-y0)/5
    a,b,c,d=[HEIGHTS[(xx,yy)] for xx,yy in [(x0,y0),(x0+5,y0),(x0,y0+5),(x0+5,y0+5)]]
    if (i+j)%2:return a+(b-a)*(fx-fy)+(d-a)*fy if fy<=fx else a+(d-a)*fx+(c-a)*(fy-fx)
    return a+(b-a)*fx+(c-a)*fy if fx+fy<=1 else d+(c-d)*(1-fx)+(b-d)*(1-fy)

def preservation(x,y):
    # Radius includes a complete mesh cell beyond all usable road shoulders.
    rd,rz,rw,_=previous.road_info(x,y)
    keep=1-smooth(rw/2+13,rw/2+28,rd)
    for p in previous.PADS:
        d=math.hypot(x-p['center'][0],y-p['center'][1])
        keep=max(keep,1-smooth(p['radius']+10,p['radius']+28,d))
    river=abs(x-previous.river_center_x(y))-previous.river_halfwidth(y)
    keep=max(keep,1-smooth(13,27,river))
    keep=max(keep,1-smooth(75,92,max(abs(x),abs(y))))
    keep=max(keep,1-smooth(5,18,800-max(abs(x),abs(y))))
    return keep

CELLS={}
def cell(i,j):
    if (i,j) in CELLS:return CELLS[(i,j)]
    if not (0<=i<N and 0<=j<N):return None
    x=-800+i*5;y=-800+j*5
    if -65<x+2.5<65 and -65<y+2.5<65:return None
    corners=[HEIGHTS[(xx,yy)] for xx,yy in [(x,y),(x+5,y),(x+5,y+5),(x,y+5)]]
    base=original(x+2.5,y+2.5)
    slope=math.hypot((corners[1]+corners[2]-corners[0]-corners[3])/10,(corners[2]+corners[3]-corners[0]-corners[1])/10)
    keep=preservation(x+2.5,y+2.5)
    steep=smooth(.12,.62,slope)
    # Different local lithological packets interrupt broad contour bands.
    packet=noise(i//9,j//9,11)
    step=.45+steep*(2.0+1.55*packet)
    offset=(math.sin(x/43)+math.cos(y/59))*.65+packet*.9
    shelf=math.floor((base+offset)/step)*step-offset
    heights=[round(z*keep+shelf*(1-keep),4) for z in corners]
    stone=(slope>.43 or base>112) and keep<.98
    role='rock' if stone and noise(i//2,j//2,24)>.14 else 'ground'
    record={'i':i,'j':j,'x':x,'y':y,'z':heights,'base':base,'slope':slope,'keep':keep,'role':role,'step':step}
    CELLS[(i,j)]=record
    return record

class Geometry:
    def __init__(self,name,role):self.name=name;self.role=role;self.v=[];self.t=[];self.uv=[];self.colors=[];self.parts=0
    def face(self,points,tint=1,uv_axis=None):
        if len(points)<3:return
        a,b,c=points[:3];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
        n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        if sum(q*q for q in n)<1e-12:return
        axis=uv_axis if uv_axis is not None else max(range(3),key=lambda k:abs(n[k]))
        axes=[k for k in range(3) if k!=axis]
        start=len(self.v)
        self.v.extend([[round(v,4) for v in p] for p in points])
        self.uv.extend([[round(p[axes[0]]/2,5),round(p[axes[1]]/2,5)] for p in points])
        self.colors.extend([[round(tint,4)]*3 for p in points])
        self.t.extend([[start,start+k,start+k+1] for k in range(1,len(points)-1)])
        self.parts+=1
    def box(self,center,size,tint=1):
        x,y,z=center;hx,hy,hz=[s/2 for s in size]
        vs=[[x+dx*hx,y+dy*hy,z+dz*hz] for dz in [-1,1] for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        for f in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:self.face([vs[k] for k in f],tint)
    def save(self):
        path=OUT/(self.name+'.json')
        data={'name':self.name,'role':self.role,'units':'meters','vertices':self.v,'triangles':self.t,'uv0':self.uv,'colors':self.colors}
        path.write_text(json.dumps(data,separators=(',',':')))
        return {'name':self.name,'role':self.role,'source':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'vertices':len(self.v),'triangles':len(self.t),'bounds_m':[[min(p[k] for p in self.v) for k in range(3)],[max(p[k] for p in self.v) for k in range(3)]]}

def riser(geo,a,b,za,zb,na,nb,seed,detail):
    # Two independently supported neighboring shelves meet at this wall.
    da=za-na;db=zb-nb
    if abs(da)<.0001 and abs(db)<.0001:return
    if da*db<0:
        t=da/(da-db);p=[a[k]+(b[k]-a[k])*t for k in range(2)];z=za+(zb-za)*t
        riser(geo,a,p,za,z,na,z,seed,False);riser(geo,p,b,z,zb,z,nb,seed+1,False);return
    upper_a,lower_a=max(za,na),min(za,na);upper_b,lower_b=max(zb,nb),min(zb,nb)
    pts=[[*a,lower_a],[*b,lower_b],[*b,upper_b],[*a,upper_a]]
    if da+db<0:pts.reverse()
    # Remove coincident endpoint vertices on tapering risers.
    unique=[]
    for p in pts:
        if not unique or any(abs(p[k]-unique[-1][k])>1e-6 for k in range(3)):unique.append(p)
    if len(unique)>1 and all(abs(unique[0][k]-unique[-1][k])<1e-6 for k in range(3)):unique.pop()
    geo.face(unique,.88+noise(seed,17)*.15)
    height=(upper_a+upper_b-lower_a-lower_b)/2
    if not detail or height<1.25:return
    length=math.hypot(b[0]-a[0],b[1]-a[1])
    if length<4.9:return
    # Broken ledgers: true shallow box relief in offset stone courses. Far from
    # protected walking surfaces, these produce smaller geometry than the ridge.
    dx=(b[0]-a[0])/length;dy=(b[1]-a[1])/length
    nx=dy;ny=-dx
    if da+db<0:nx=-nx;ny=-ny
    bands=min(4,max(1,math.floor(height/1.1)))
    for band in range(bands):
        if noise(seed,band,6)<.32:continue
        fraction=(band+.5)/bands
        bottom=(lower_a+lower_b)/2
        z=bottom+fraction*height
        width=1.0+noise(seed,band,3)*2.6
        along=.8+noise(seed,band,12)*(length-1.6)
        projection=.10+noise(seed,band,4)*.26
        cx=a[0]+dx*along+nx*projection*.33;cy=a[1]+dy*along+ny*projection*.33
        sx=width if abs(dx)>.5 else projection;sy=width if abs(dy)>.5 else projection
        geo.box([cx,cy,z],[sx,sy,min(.68,height/bands*.65)],.82+noise(seed,band,44)*.22)

def generate():
    OUT.mkdir(parents=True,exist_ok=True);assets=[];chunks=[];protected=0;stepped=0
    for tx in range(8):
        for ty in range(8):
            ground=Geometry(f'VoxelGround_{tx}_{ty}','ground');rock=Geometry(f'VoxelRock_{tx}_{ty}','rock')
            for i in range(tx*40,(tx+1)*40):
                for j in range(ty*40,(ty+1)*40):
                    c=cell(i,j)
                    if c is None:continue
                    x,y,z=c['x'],c['y'],c['z'];pts=[[x,y,z[0]],[x+5,y,z[1]],[x+5,y+5,z[2]],[x,y+5,z[3]]]
                    geo=ground if c['role']=='ground' else rock
                    shade=.9+.13*noise(i,j,8)
                    # Preserve the exact diagonal of the previous 5 m mesh.
                    tris=[[0,1,2],[0,2,3]] if (i+j)%2 else [[0,1,3],[1,2,3]]
                    for t in tris:geo.face([pts[k] for k in t],shade,2)
                    if c['keep']==1:protected+=1
                    else:stepped+=1
                    east=cell(i+1,j);north=cell(i,j+1)
                    if east:riser(rock,[x+5,y],[x+5,y+5],z[1],z[2],east['z'][0],east['z'][3],i*409+j,c['keep']<.05 and east['keep']<.05 and max(c['base'],east['base'])>22)
                    if north:riser(rock,[x+5,y+5],[x,y+5],z[2],z[3],north['z'][1],north['z'][0],i*911+j,c['keep']<.05 and north['keep']<.05 and max(c['base'],north['base'])>22)
            rows=[g.save() for g in (ground,rock) if g.t];assets+=rows
            chunks.append({'tile':[tx,ty],'old_actor':f'WX_Terrain_{tx}_{ty}','assets':[r['name'] for r in rows]})
    forest=[]
    for tree in BASE_MANIFEST['forest_instances']:
        x,y,z=tree['location_m'];i=min(319,max(0,math.floor((x+800)/5)));j=min(319,max(0,math.floor((y+800)/5)));c=cell(i,j)
        if c:
            fx=(x-c['x'])/5;fy=(y-c['y'])/5;a,b,d,cc=c['z']
            if (i+j)%2:hz=a+(b-a)*(fx-fy)+(d-a)*fy if fy<=fx else a+(d-a)*fx+(cc-a)*(fy-fx)
            else:hz=a+(b-a)*fx+(cc-a)*fy if fx+fy<=1 else d+(cc-d)*(1-fx)+(b-d)*(1-fy)
            row=dict(tree);row['location_m']=[x,y,round(hz-.08,3)];forest.append(row)
        else:forest.append(tree)
    apron_assets,apron_chunk=generate_apron();assets+=apron_assets;chunks.append(apron_chunk)
    manifest={'version':5,'bounds_m':[-800,-800,800,800],'cell_size_m':5,'home_apron_cell_size_m':1,'uv_repeat_m':2,'assets':assets,'chunks':chunks,
              'protected_cells':protected,'stepped_cells':stepped,'total_triangles':sum(r['triangles'] for r in assets),
              'pads':BASE_MANIFEST['pads'],'roads':BASE_MANIFEST['roads'],'route_samples':BASE_MANIFEST['route_samples'],
              'forest_instances':forest,'forest_xy_order_and_scale_preserved':True,
              'preserved_actors':['WX_AlderRiver','WX_HomeTributary','WX_RiverStoneBridges'],
              'materials':{'ground':'/Game/Terrarium/WorldExpansion/TerrainV5/Materials/M_VoxelGrass','rock':'/Game/Terrarium/WorldExpansion/TerrainV5/Materials/M_VoxelStone'},
              'geometry':'Horizontal variable-height shelves, vertical connecting risers, projecting broken stone courses; exact previous triangles in protected corridors.',
              'source_baseline_manifest_sha256':hashlib.sha256((BASE/'manifest.json').read_bytes()).hexdigest()}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));preview()
    print(json.dumps({'assets':len(assets),'triangles':manifest['total_triangles'],'protected_cells':protected,'stepped_cells':stepped,'forest':len(forest)}))

def generate_apron():
    source=json.loads((BASE/'HomeApron.json').read_text())
    hull=json.loads((BASE/'apron-profile.json').read_text())['hull_m']
    wetdata=json.loads((ROOT/'Docs/HomesteadPilot/RemainingEnvironment/unreal-validation.json').read_text())
    water=[(t['translation'][0]/100,t['translation'][1]/100) for g in wetdata['groups'] for t in g['before']]
    heights={(p[0],p[1]):p[2] for p in source['vertices']}
    ground=Geometry('VoxelHomeGround','ground');rock=Geometry('VoxelHomeRock','rock');cells={};protected=0;stepped=0
    def cross(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    for i in range(130):
        for j in range(130):
            x=-65+i;y=-65+j;cx=x+.5;cy=y+.5
            z=[heights[p] for p in [(x,y),(x+1,y),(x+1,y+1),(x,y+1)]]
            inside=all(cross(a,b,(cx,cy))>=0 for a,b in zip(hull,hull[1:]+hull[:1]))
            distance=min(previous.segment_info(cx,cy,[*a,0],[*b,0])[0] for a,b in zip(hull,hull[1:]+hull[:1]))
            keep=1 if inside else 1-smooth(1.5,6,distance)
            rd,rz,rw,_=previous.road_info(cx,cy);keep=max(keep,1-smooth(rw/2+2.5,rw/2+6,rd))
            wd=min(math.hypot(cx-wx,cy-wy) for wx,wy in water)
            keep=max(keep,1-smooth(3,6,wd))
            td,_,_=previous.segment_info(cx,cy,[35.5,-9,0],[previous.river_center_x(-12),-12,0])
            keep=max(keep,1-smooth(9.5,13,td))
            keep=max(keep,1-smooth(1,4,65-max(abs(cx),abs(cy))))
            slope=math.hypot((z[1]+z[2]-z[0]-z[3])/2,(z[2]+z[3]-z[0]-z[1])/2)
            step=.22+smooth(.12,.7,slope)*(.5+noise(i//5,j//5,47)*.15)
            offset=.12*math.sin(cx/4)+.1*math.cos(cy/7)
            base=(z[0]+z[2])/2;shelf=math.floor((base+offset)/step)*step-offset
            modified=[round(h*keep+shelf*(1-keep),4) for h in z]
            role='rock' if slope>.42 and keep<.98 and noise(i//2,j//2,34)>.18 else 'ground'
            cells[(i,j)]={'z':modified,'role':role,'keep':keep,'original':z}
            if keep==1:protected+=1
            else:stepped+=1
    for (i,j),c in cells.items():
        x=-65+i;y=-65+j;z=c['z'];pts=[[x,y,z[0]],[x+1,y,z[1]],[x+1,y+1,z[2]],[x,y+1,z[3]]]
        geo=ground if c['role']=='ground' else rock
        shade=.91+noise(i,j,31)*.11
        for tri in [[0,1,2],[0,2,3]]:geo.face([pts[k] for k in tri],shade,2)
        east=cells.get((i+1,j));north=cells.get((i,j+1))
        if east:riser(rock,[x+1,y],[x+1,y+1],z[1],z[2],east['z'][0],east['z'][3],i*331+j,False)
        if north:riser(rock,[x+1,y+1],[x,y+1],z[2],z[3],north['z'][1],north['z'][0],i*499+j,False)
    assets=[g.save() for g in (ground,rock)]
    receipt={'source':'SourceAssets/WorldExpansion/Terrain/HomeApron.json','source_sha256':hashlib.sha256((BASE/'HomeApron.json').read_bytes()).hexdigest(),
             'cell_m':1,'step_range_m':[.22,.87],'protected_cells':protected,'stepped_outer_cells':stepped,
             'source_hull_m':hull,'original_hull_interior_exact':True,'road_river_and_seam_guards_exact':True,
             'protected_exact_corner_checks':sum(1 for c in cells.values() if c['keep']==1 and c['z']==c['original']),
             'triangles':sum(r['triangles'] for r in assets)}
    assert receipt['protected_exact_corner_checks']==protected
    (OUT/'home-apron-source-validation.json').write_text(json.dumps(receipt,indent=2))
    return assets,{'tile':['HomeApron'],'old_actor':'WX_HomeApron','assets':[r['name'] for r in assets]}

def preview():
    # Geometry-based technical preview, not a substitute for actual editor QA.
    polygons=[]
    for i in range(139,173):
        for j in range(283,317):
            c=cell(i,j)
            if not c:continue
            x,y,z=c['x'],c['y'],c['z']
            pts=[[x,y,z[0]],[x+5,y,z[1]],[x+5,y+5,z[2]],[x,y+5,z[3]]]
            polygons.append((x+y,pts,'#727958' if c['role']=='ground' else '#929078'))
            for ni,nj,ia,ib,ja,jb in [(i+1,j,1,2,0,3),(i,j+1,2,3,1,0)]:
                n=cell(ni,nj)
                if n:polygons.append((x+y,[[*pts[ia][:2],z[ia]],[*pts[ib][:2],z[ib]],[*pts[ib][:2],n['z'][jb]],[*pts[ia][:2],n['z'][ja]]],'#5f6351'))
    def proj(p):return ((p[0]-p[1]+690)*3.5+560,(p[0]+p[1]-640)*1.6-p[2]*3.1+610)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850"><rect width="1200" height="850" fill="#222b28"/><text x="28" y="38" fill="#ede6c9" font-size="22">Terrarium V5 — actual stepped mountain geometry preview</text>']
    for _,pts,col in sorted(polygons,key=lambda p:p[0]):svg.append('<polygon points="'+' '.join('%.1f,%.1f'%proj(p) for p in pts)+'" fill="'+col+'" stroke="#414c40" stroke-width=".3"/>')
    svg.append('</svg>');(OUT/'mountain-geometry-preview.svg').write_text(''.join(svg))

if __name__=='__main__':generate()
