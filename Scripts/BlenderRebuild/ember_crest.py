"""Physical shield and flame relief traced from the Ember Crest's front design."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset
P=[('bd8b29',.34,0),('c79b39',.32,0),('a97d2b',.38,0),('d3a740',.29,0),
   ('111a1c',.67,0),('1b211f',.72,0),('28271f',.65,0),('142023',.68,0),
   ('e82d13',.27,0),('cc1b0c',.29,0),('f33914',.26,0),('ed5c05',.26,0),
   ('fa8606',.24,0),('ffb70a',.22,0),('ffd42a',.21,0),('ffe867',.20,0),
   ('125e70',.46,0),('164a55',.50,0),('8a6429',.43,0),('ad1010',.16,0)]
class CrestAsset(PaletteAsset):
    def make_material(self):
        super().make_material()
        import numpy as np
        rng=np.random.default_rng(614)
        for image in [self.images[0],self.images[2]]:
            px=np.empty(512*512*4,dtype=np.float32);image.pixels.foreach_get(px);px=px.reshape(512,512,4)
            for index in [0,1,2,3,18]:
                y=index//8*64;x=index%8*64
                grain=rng.uniform(-1,1,(64,64,1))
                if image==self.images[0]:px[y:y+64,x:x+64,:3]*=1+grain*.11
                else:px[y:y+64,x:x+64,:3]=np.clip(px[y:y+64,x:x+64,:3]+grain*.045,0,1)
            image.pixels.foreach_set(px.ravel());image.save();image.pack()
a=CrestAsset('EmberCrest','ember_crest.png',P)
metal=a.material;metal.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.72
enamel=a.shader('Enamel',metallic=.12);field=a.shader('Field',metallic=.12)
# The reference reveals the lower faces of raised blocks. A low orthographic
# camera matches that projection; front coordinates are measured in the PNG.
theta=math.radians(20);unit=.001;origin_v=1170
def xyz(u,v,y):return ((u-627)*unit,y,((origin_v-v)*unit+y*math.sin(theta))/math.cos(theta))
def rect(label,box,y,depth,index,material=None,bevel=.0012):
    u0,v0,u1,v1=box
    pos=xyz((u0+u1)/2,(v0+v1)/2,y);pos=(pos[0],y+depth/2,pos[2])
    ob=a.box(label,pos,((u1-u0)*unit,depth,(v1-v0)*unit/math.cos(theta)),index,bevel)
    ob.data.materials[0]=material or metal;return ob
def polygon(label,points,y,depth,index,material=None,bevel=.001):
    front=[xyz(u,v,y) for u,v in points];back=[(x,y+depth,z) for x,_,z in front];n=len(front)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    return a.solid(label,front+back,faces,index,material,bevel)
half=[(627,1168),(591,1147),(591,1123),(550,1123),(550,1065),(488,1065),(488,1011),(429,1011),(429,956),(369,956),(369,903),(312,903),(312,850),(253,850),(253,778),(212,778),(212,222),(345,222),(345,168),(467,168),(467,103),(627,103)]
outline=half+[(1254-u,v) for u,v in reversed(half[1:-1])]
polygon('Continuous bronze shield backing',outline,.025,.105,17,field,.0016)
def inside(x,y,poly):
    hit=False
    for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
    return hit
for row in range(26):
    for col in range(22):
        x=217+col*38.5;v=160+row*38.5
        if all(inside(xx,vv,outline) for xx in [x+1,x+37.5] for vv in [v+1,v+37.5]):
            warm=abs(x+19-627)<210 and 370<v<850
            color=(6 if (row*3+col*7)%5==0 else 5) if warm else (7 if (row+col)%4==0 else 4)
            rect('Recessed charcoal face tile',(x+.7,v+.7,x+37.8,v+37.8),.0,.037,color,field,.0006)
# Rim courses follow the traced stepped edge. Mirrors share geometry dimensions,
# while small color changes preserve the source's individual gold blocks.
rim=[(467,103,568,164),(467,164,515,224),(345,168,406,222),(406,168,467,222),(345,222,402,278),
     (212,222,275,278),(275,222,345,278),(212,278,271,318),(212,318,271,418),(212,418,271,474),(212,474,271,529),
     (212,648,271,710),(212,710,271,778),(253,774,310,850),(253,850,310,883),(310,849,369,939),
     (367,900,426,959),(367,959,426,991),(426,955,488,1015),(426,1015,488,1042),
     (486,1010,548,1067),(486,1067,548,1091),(548,1057,591,1131)]
for side in [-1,1]:
    for i,box in enumerate(rim):
        u0,v0,u1,v1=box
        if side==1:u0,u1=1254-u1,1254-u0
        rect('Stepped gold rim',(u0,v0,u1,v1),-.045,.086,i%4,bevel=.0014)
# Four structural gem sockets; rear bands continue below the front gold.
for box in [(171,525,313,655),(941,525,1083,655),(568,58,684,187)]:
    rect('Patinated socket body',box,-.047,.153,16,field,.002)
    rect('Gold socket face',box,-.063,.028,1,metal,.003)
polygon('Lower pointed gem mount',[(591,1027),(627,1003),(662,1027),(662,1051),(701,1051),(701,1130),(662,1130),(662,1152),(627,1174),(591,1152),(591,1130),(550,1130),(550,1051),(591,1051)],-.063,.16,1,metal,.002)
# Flame relief measured in the front design, including separated side tongues.
Y=14;O=12;R=8
central={0:[(0,Y)],1:[(0,Y)],2:[(0,Y),(1,Y)],3:[(-1,Y),(0,O),(1,R)],
         4:[(-1,Y),(0,Y),(1,R),(2,R)],5:[(-2,Y),(-1,O),(0,Y),(1,O),(2,Y)],
         6:[(-2,Y),(-1,O),(0,O),(1,R),(2,Y)],7:[(-3,Y),(-2,O),(-1,R),(0,O),(1,O),(2,O),(3,Y)],
         8:[(-3,Y),(-2,O),(-1,Y),(0,Y),(1,Y),(2,O),(3,Y)],
         9:[(-3,Y),(-2,Y),(-1,O),(0,Y),(1,O),(2,Y),(3,O)],
         10:[(-2,Y),(-1,Y),(0,O),(1,Y),(2,Y)],11:[(-2,O),(-1,O),(0,Y),(1,Y),(2,O)],12:[(-1,O),(0,Y),(1,O)],13:[(0,O)]}
for row,entries in central.items():
    for col,color in entries:
        v0=250+40*row+(18 if row>=3 else 0)
        box=(606+39*col,v0,645+39*col,v0+(58 if row==2 else 40))
        front={Y:-.114,O:-.108,R:-.102}[color]
        rect('Raised central flame block',box,front,.031-front,color,enamel,.0014)
outer=[(459,351,501,391,R),(459,391,501,431,R),(420,429,460,470,R),(420,470,460,511,O),
       (382,509,422,551,O),(422,511,460,551,O),(382,551,422,591,O),
       (353,590,383,630,R),(383,590,423,630,O),(353,630,383,669,R),(383,630,423,669,R),
       (353,669,383,713,R),(383,669,423,709,R),(423,655,459,697,R),(383,709,423,748,R),
       (423,697,459,744,R),(423,744,459,784,R),(459,744,499,784,O),(499,744,527,784,O),
       (459,784,499,824,R),(499,784,538,824,R),(499,824,538,863,R),(538,824,577,863,R),
       (538,863,577,901,R),(577,863,608,901,R),(577,901,608,940,R)]
for side in [-1,1]:
    for n,(x0,v0,x1,v1,color) in enumerate(outer):
        if side==1:x0,x1=1254-x1,1254-x0
        rect('Outer curling flame block',(x0,v0,x1,v1),-.080,.111,color+(n%3 if color==R else 0),enamel,.0013)
for box,color in [((608,863,647,902),12),((608,902,647,941),11),((608,941,647,979),8)]:rect('Flame lower tip',box,-.084,.115,color,enamel,.0013)
# Bright central ember, shaped as a small stepped cross with pointed ends.
polygon('Central ember point',[(606,555),(627,537),(647,555),(647,590),(686,590),(686,630),(647,630),(647,666),(627,689),(607,666),(607,630),(568,630),(568,590),(607,590)],-.157,.073,14,enamel,.001)
for box in [(607,555,646,590),(568,591,606,629),(607,591,646,629),(647,591,685,629),(607,630,646,666)]:rect('Pale ember face',box,-.16,.02,15,enamel,.001)
def jewel(u,v,w,h):
    # Broad red front table, four sloped polished facets and a closed back.
    outer=[(u-w/2,v-h/2),(u+w/2,v-h/2),(u+w/2,v+h/2),(u-w/2,v+h/2)]
    inner=[(u-w*.32,v-h*.32),(u+w*.32,v-h*.32),(u+w*.32,v+h*.32),(u-w*.32,v+h*.32)]
    vs=[xyz(x,z,y) for points,y in [(outer,-.072),(outer,-.083),(inner,-.108)] for x,z in points]
    fs=[(3,2,1,0),(8,9,10,11)];inds=[19,8]
    for start in [0,4]:
        for j in range(4):fs.append((start+j,start+(j+1)%4,start+(j+1)%4+4,start+j+4));inds.append([10,8,19,9][j])
    a.solid('Faceted red socket gem',vs,fs,8,enamel,.0007,inds)
for args in [(627,125,54,65),(243,588,64,68),(1008,588,64,68),(627,1087,64,72)]:jewel(*args)
# Plain minted reverse is inferred: a continuous metal plate, not an image.
polygon('Solid rear face',[(627+(u-627)*.965,635+(v-635)*.965) for u,v in outline],.132,.008,18,metal,.001)
a.studio((0,0,.58),(0,-7,.58-7*math.tan(theta)),1.27)
a.scene.render.resolution_x=1254;a.scene.render.resolution_y=1254;a.scene.cycles.samples=96
a.scene.view_settings.view_transform='Standard';a.scene.view_settings.look='Medium High Contrast';a.scene.view_settings.exposure=-.35
for ob in a.scene.objects:
    if ob.type=='LIGHT':
        if ob.name.startswith('Key'):ob.data.energy=900;ob.location=(-3,-4,5)
        elif ob.name.startswith('Fill'):ob.data.energy=180
        ob.rotation_euler=(Vector((0,0,.58))-ob.location).to_track_quat('-Z','Y').to_euler()
a.scene['fidelity_status']='traced_front_relief_pending_visual_review';a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'source':'SourceAssets/Voxel/ember_crest.png','method':'Measured front outlines, rim rectangles and flame block regions rebuilt as beveled solid geometry. Depth is inferred from exposed lower faces. Front texture coordinates sample palette cells, not the full concept image.','unseen_rear':'Plain continuous minted metal face inferred.','status':'pending_render_and_engine_review'},indent=2))
result={'asset':a.key,'parts':len(a.parts),'scene':a.scene.name}
