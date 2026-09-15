"""Solid hexagonal mining badge with inset cavern and raised crystal glyph."""
import bpy,sys,math,json,random
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset
P=[('c5a443',.32,0),('d3b451',.29,0),('a28432',.39,0),('e4c768',.28,0),
   ('263334',.70,0),('314344',.69,0),('172c2e',.75,0),('092c30',.71,0),
   ('07464c',.60,0),('0b555a',.58,0),('136970',.54,0),('2a8288',.48,0),
   ('39767a',.47,0),('65a7aa',.38,0),('a5d3cc',.32,0),('b6d6d0',.30,0),
   ('399894',.29,0),('73bcb4',.25,0),('a6ded0',.24,0),('1e6869',.36,0)]
a=PaletteAsset('DeepDelverMark','deep_delver_mark.png',P)
metal=a.material;metal.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.65
stone=a.shader('Cavern',metallic=.03);crystal=a.shader('Crystal',metallic=.10)
theta=math.radians(30);unit=.001;origin_v=1150
def xyz(u,v,y):return ((u-627)*unit,y,((origin_v-v)*unit-y*math.sin(theta))/math.cos(theta))
def polygon(label,points,y,depth,index,material=None,bevel=.001):
    front=[xyz(u,v,y) for u,v in points];n=len(front)
    vs=front+[(x,yy+depth,z) for x,yy,z in front]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    return a.solid(label,vs,fs,index,material,bevel)
def rect(label,box,y,depth,index,material=None,bevel=.0008):
    x0,v0,x1,v1=box;pos=xyz((x0+x1)/2,(v0+v1)/2,y)
    ob=a.box(label,(pos[0],y+depth/2,pos[2]),((x1-x0)*unit,depth,(v1-v0)*unit/math.cos(theta)),index,bevel)
    ob.data.materials[0]=material or stone;return ob
def ring(label,outer,inner,y,depth,index,material,sloped_back=False):
    n=len(outer);vs=[xyz(u,v,yy) for yy in [y,y+depth] for loop in [outer,inner] for u,v in loop]
    # Back loops use identical Z to their front counterparts so thickness is along Y.
    for j in range(2*n):vs[2*n+j]=(vs[j][0],y+depth,vs[j][2]-(depth*math.tan(theta) if sloped_back else 0))
    fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return a.solid(label,vs,fs,index,material,.0012)
outer=[(627,78),(1070,330),(1070,864),(627,1120),(184,864),(184,330)]
inner=[(627,149),(1012,368),(1012,831),(627,1053),(242,831),(242,368)]
field=[(627,220),(976,419),(976,806),(627,1008),(278,806),(278,419)]
polygon('Continuous cast badge back',outer,.073,.065,2,metal,.002)
polygon('Deep teal cavern backing',field,.035,.043,7,stone,.001)
ring('Six sided thick gold frame',outer,inner,-.038,.045,0,metal)
ring('Continuous frame to backing wall',outer,inner,.002,.078,2,metal,True)
ring('Inner charcoal bevel surround',inner,field,-.011,.069,4,stone)
# Narrow inset highlight along the exterior of the forged frame.
highlight=[(627+(x-627)*.978,601+(v-601)*.978) for x,v in outer]
ring('Thin perimeter gold edge',outer,highlight,-.041,.012,3,metal)
def inside(x,y,poly):
    hit=False
    for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
    return hit
def rear_key(label,x,y,z,width,height):
    # A closed sloping web joins raised relief to the cast backing. The unseen
    # mounting is inferred; the web stays behind the front-facing relief.
    depth=.061-y
    if depth<=0:return
    front=[(x-width/2,y,z-height/2),(x+width/2,y,z-height/2),(x+width/2,y,z+height/2),(x-width/2,y,z+height/2)]
    back=[(xx,yy+depth,zz-depth*math.tan(theta)) for xx,yy,zz in front]
    fs=[(3,2,1,0),(4,5,6,7)]+[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)]
    a.solid(label,front+back,fs,7,stone,.0003)
rng=random.Random(214)
for row in range(22):
    for col in range(19):
        x=280+col*37;v=224+row*36
        if all(inside(xx,vv,field) for xx in [x,x+36] for vv in [v,v+35]):
            rect('Inset square cavern tile',(x+.4,v+.4,x+36.4,v+35.4),.019+rng.random()*.003,.025,8 if (row*5+col*3)%11==0 else 7,stone)
# Distinct angular shoulder rock courses flank the upper cavern.
shoulders=[[(283,416),(476,305),(476,380),(397,425),(397,451),(318,449),(318,486),(283,505)],
           [(318,451),(356,451),(356,497),(318,517)],
           [(397,379),(443,352),(443,391),(397,418)]]
for side in [-1,1]:
    for i,p in enumerate(shoulders):
        points=[(1254-x if side==1 else x,v) for x,v in p]
        polygon('Angular dark cavern shoulder',points,-.022,.069,4+i%2,stone,.0008)
def block(label,u,top,width,total_height,y,index,material=stone):
    # A square column turned 45 degrees shows two vertical faces and a diamond top.
    top_depth=width*math.sin(theta);h=(total_height-top_depth)*unit/math.cos(theta)
    assert h>0
    center_y=y+width*unit/2;xt,_,zt=xyz(u,top+top_depth/2,center_y)
    ob=a.box(label,(xt,center_y,zt-h/2),(width*unit/math.sqrt(2),width*unit/math.sqrt(2),h),index,.0006,rotation=(0,0,45))
    ob.data.materials[0]=material
    rear_key('Cast backing web for '+label,xt,center_y+width*unit*.13,zt-h/2,width*unit*.36,h*.45)
    return ob
# The cavern descends in repeated V-shaped, square-cut ledges. Their depths are
# modeled independently of the background tile layer; this is not a height map.
courses=[[(314,597,61,84),(366,646,66,88),(402,755,68,84),(441,811,68,82),(486,850,61,78),(538,869,66,76),(591,900,70,72)],
         [(333,509,40,64),(368,552,49,69),(400,605,55,70),(429,673,51,72),(451,725,58,73),(486,773,66,90)],
         [(443,546,53,67),(477,595,45,62),(502,618,43,70),(501,672,42,68),(534,707,46,71),(534,761,48,71),(573,815,52,73)],
         [(557,520,59,74),(577,574,45,76),(577,645,48,66),(595,692,42,64),(600,753,43,66),(607,814,38,70)]]
for side in [-1,1]:
    for course,chain in enumerate(courses):
        for j,(u,v,w,h) in enumerate(chain):
            index=([5,5,12,12,11,10,10][j%7] if course==0 else [8,9,10,8,10,9,11][j%7])
            block('Square cut descending cavern ledge',u if side==-1 else 1254-u,v,w,max(h,100 if course==0 else 89),-.044+course*.013,index)
block('Bottom cavern keystone',627,917,70,66,-.044,11)
for side in [-1,1]:
    for j,(u,v) in enumerate([(349,620),(390,672),(407,710),(439,755),(474,805),(520,835),(561,874),(604,907)]):
        block('Intermediate connecting cavern step',u if side==-1 else 1254-u,v,60,86,-.020,5 if j<3 else 9+j%3)
# Pale crystal glyph: central tall tip, paired shoulders, center and satellites.
for u,v,w,h,color in [(627,258,70,123,15),(588,338,72,107,14),(666,338,72,107,14),
                       (588,408,72,72,13),(666,408,72,72,13),(627,428,70,77,15),
                       (627,486,66,62,11),(522,454,59,78,14),(732,454,59,78,14),
                       (575,524,40,63,14),(679,524,40,63,14),
                       (627,605,63,74,14),(627,694,50,58,11),(627,755,50,58,10),(627,816,40,56,10)]:
    block('Raised crystal glyph column',u,v,w,h,-.178 if u==627 and v==428 else -.124,color,crystal)
# Chunky gold corner clips and top/bottom gemstone mounts.
clip=[(203,375),(275,334),(275,403),(239,407),(239,456),(203,456)]
lower=[(203,756),(240,756),(240,808),(276,819),(276,876),(203,836)]
for side in [-1,1]:
    for shape in [clip,lower]:
        front=[xyz(1254-x if side==1 else x,v,-.087) for x,v in shape];n=len(front)
        back=[(x+side*.052,y+.065,z) for x,y,z in front]
        fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
        a.solid('Stepped outer corner clasp',front+back,fs,0,metal,.0016)
for points in [[(562,92),(627,76),(693,92),(693,228),(562,228)],[(562,990),(693,990),(693,1126),(627,1161),(562,1125)]]:
    polygon('Thick central gemstone socket',points,-.096,.05,0,metal,.002)
    v=sum(p[1] for p in points)/len(points);x,y,z=xyz(627,v,-.055)
    rear_key('Hidden gemstone socket key',x,y,z,.065,.06)
def gem(u,v):
    w=64;h=64
    outer=[(u-w/2,v-h/2),(u+w/2,v-h/2),(u+w/2,v+h/2),(u,v+h/2+11),(u-w/2,v+h/2)]
    inner=[(u-13,v-10),(u+13,v-10),(u+13,v+13),(u,v+17),(u-13,v+13)]
    n=len(outer);vs=[xyz(x,z,y) for points,y in [(outer,-.099),(outer,-.107),(inner,-.144)] for x,z in points]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(2*n,3*n))];colors=[19,17]
    for start in [0,n]:
        for j in range(n):fs.append((start+j,start+(j+1)%n,start+(j+1)%n+n,start+j+n));colors.append([18,17,19,19,16][j])
    a.solid('Faceted turquoise socket gemstone',vs,fs,17,crystal,.0006,colors)
gem(627,157);gem(627,1055)
a.studio((0,0,.603908),(0,-7,.603908+7*math.tan(theta)),1.254)
a.scene.render.resolution_x=1254;a.scene.render.resolution_y=1254;a.scene.cycles.samples=80
a.scene.view_settings.view_transform='Standard';a.scene.view_settings.look='Medium High Contrast';a.scene.view_settings.exposure=-.35
for ob in a.scene.objects:
    if ob.type=='LIGHT':
        if ob.name.startswith('Key'):ob.data.energy=800;ob.location=(-3,-4,5)
        elif ob.name.startswith('Fill'):ob.data.energy=220
        ob.rotation_euler=(Vector((0,0,.635))-ob.location).to_track_quat('-Z','Y').to_euler()
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'source':a.scene['concept'],'method':'Measured hexagonal rim and physical cast clips; individually modeled recessed tiles and square-cut cavern ledges; raised turned-square crystal columns and faceted gems. Packed material palettes are not projected concept images.','inferred':'Depths and plain cast rear inferred from single front concept. Crystal is an opaque mineral material at this stage.','status':'pending_studio_and_engine_review'},indent=2))
result={'asset':a.key,'scene':a.scene.name,'parts':len(a.parts)}
