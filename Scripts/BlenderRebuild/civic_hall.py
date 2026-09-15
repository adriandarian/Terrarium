"""Two-storey civic hall with open belfry, physical bell, clock and arched portal."""
import bpy,math,random,sys
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
from mathutils import Vector
P=[('a19f89','stone'),('8e947d','stone'),('b2aa91','stone'),('7f8871','stone'),
   ('71502b','timber'),('573d20','timber'),('815629','timber'),('cfbd8e','stone'),
   ('e9dab3','plaster'),('dfcfa7','plaster'),('ad5231','clay'),('b65c34','clay'),('a74c2b','clay'),('c36639','clay'),
   ('71882b','moss'),('889b32','moss'),('5f7526','moss'),('9da939','moss'),
   ('087c71','glass'),('075f55','glass'),('119589','glass'),('d89722','metal'),
   ('eee0a5','flower'),('dc7825','flower'),('302a1d','shadow'),('edae3d','pane'),('795022','metal'),('ecdbaf','stone')]
a=Asset('CivicHall','civic_hall.png',P);b=a.box;rng=random.Random(926)

def course(label,x,y,z,w,d,h,cell=.25,color=None):
    rows=max(1,round(h/.17));cols=max(1,round(w/cell))
    for j in range(rows):
        edges=[-w/2]+[q for i in range(cols+1) if -w/2<(q:=-w/2+(i+(.5 if j%2 else 0))*w/cols)<w/2]+[w/2]
        for u,v in zip(edges,edges[1:]):
            b(label,(x+(u+v)/2,y,z-h/2+(j+.5)*h/rows),(v-u-.005,d,h/rows-.005),color if color is not None else rng.choice([0,0,1,2,3]),.008)

def window(x,y,z,w=.43,h=.66):
    b('Window recess',(x,y+.05,z),(w,.07,h),24,.003)
    for sx in [-1,1]:
        for sz in [-1,1]:
            b('Teal glazing',(x+sx*w*.23,y+.005,z+sz*h*.23),(w*.43,.04,h*.43),19,.004)
            b('Glazing inner sill',(x+sx*w*.23,y-.015,z+sz*h*.23-h*.18),(w*.42,.065,.032),18,.003)
    b('Window teal mullion',(x,y-.045,z),(.052,.095,h),18,.005)
    b('Window teal cross',(x,y-.045,z),(w,.095,.047),20,.004)
    for sx in [-1,1]:b('Window timber jamb',(x+sx*(w/2+.034),y-.058,z),(.077,.14,h+.09),4,.01)
    b('Window timber lintel',(x,y-.058,z+h/2+.055),(w+.17,.16,.12),4,.01)
    b('Window projecting sill',(x,y-.115,z-h/2-.065),(w+.22,.28,.12),6,.012)

def tile(x,y,z,color,w=.24,d=.24,h=.22):
    for sx in [-1,1]:
        for sy in [-1,1]:
            for sz in [-1,1]:b('Clay roof subtile',(x+sx*w/4,y+sy*d/4,z+sz*h/4),(w/2-.002,d/2-.002,h/2-.002),color,.004)

# Deep footing and five courses, with patches of moss between the stones.
b('Foundation core',(0,0,.40),(7.36,3.12,.80),1,.008)
for y in [-1.62,1.62]:course('Foundation courses',0,y,.41,7.46,.24,.82)
for side in [-1,1]:
    for j in range(5):
        for k in range(13):b('Side foundation stone',(side*3.67,-1.46+k*.24,.082+j*.164),(.24,.235,.159),rng.choice([0,1,2,3,14] if j in [2,4] else [0,1,2]),.006)
    for j in range(18):
        if rng.random()<.58:b('Foundation moss joint',(side*(.90+j*.15),-1.755,rng.choice([.26,.43,.59,.76])),(.145,.035,.09),rng.choice([14,15,16]),.004)

# Solid rear body; separate front infill gives each opening an actual reveal.
b('Plaster building body',(0,.08,2.55),(7.04,2.85,3.46),8,.004)
window_x=[-2.94,-2.02,2.02,2.94]
for side in [-1,1]:
    for level,z in enumerate([1.63,3.29]):
        for cx in [2.48,3.45,1.50]:b('Facade plaster strip',(side*cx,-1.49,z),(.38,.26,1.49),8,.003)
        for cx in [2.94,2.02]:
            b('Below window plaster',(side*cx,-1.49,z-.56),(.66,.26,.38),9,.003)
            b('Above window plaster',(side*cx,-1.49,z+.59),(.66,.26,.31),8,.003)
            window(side*cx,-1.67,z,.43,.70)
    for x in [1.34,2.49,3.56]:b('Facade timber upright',(side*x,-1.64,2.52),(.18,.26,3.49),4,.016)
    for y in [-1.5,1.46]:b('Rear corner timber',(side*3.56,y,2.54),(.24,.27,3.50),4,.016)
    for y in [-.65,.48]:
        b('Side timber upright',(side*3.57,y,2.54),(.22,.16,3.50),4,.014)
        # Two narrow side windows on each floor, facing outward.
        before=len(a.parts);window(0,0,1.63,.42,.68);window(0,0,3.29,.42,.68)
        angle=side*math.pi/2
        for o in a.parts[before:]:
            p=o.location.copy();o.location=(side*3.58+math.cos(angle)*p.x-math.sin(angle)*p.y,y+math.sin(angle)*p.x+math.cos(angle)*p.y,p.z)
            o.rotation_euler.z+=angle
for z in [2.46,4.16]:
    b('Front floor beam',(0,-1.71,z),(7.43,.25,.21),5,.014)
    b('Rear floor beam',(0,1.57,z),(7.43,.25,.21),5,.014)
    for side in [-1,1]:b('Side floor beam',(side*3.63,0,z),(.24,3.43,.21),4,.014)
    for x in [-3.56,-2.49,-1.34,1.34,2.49,3.56]:
        b('Projecting beam joint',(x,-1.80,z),(.26,.32,.25),5,.014)
        b('Timber joint corbel',(x,-1.65,z-.20),(.18,.23,.19),5,.012)

# Central projecting bay and the small upper window under its own gable.
for side in [-1,1]:
    b('Portal flank plaster',(side*.99,-1.66,1.62),(.48,.35,1.64),8,.004)
    b('Upper central bay plaster',(side*.73,-1.69,3.03),(.93,.38,1.05),8,.004)
    b('Central bay upright',(side*1.29,-1.83,2.02),(.20,.32,2.41),4,.014)
    b('Central upper upright',(side*.43,-1.93,3.15),(.10,.16,1.15),5,.008)
b('Upper window lower infill',(0,-1.70,2.71),(.79,.35,.27),8,.003)
b('Upper window high infill',(0,-1.70,3.53),(.79,.35,.27),8,.003)
window(0,-1.94,3.18,.43,.57)
b('Central front floor beam',(0,-1.86,2.46),(2.80,.28,.20),5,.014)
for ix in range(-6,7):
    x=ix*.22;top=4.42-abs(ix)*.17
    if top>3.56:b('Portico gable plaster',(x,-1.73,(top+3.56)/2),(.218,.35,top-3.56),8,.003)
# A separate forward-running roof forms the portal's pointed silhouette.
for ix in range(-7,8):
    x=ix*.21;top=4.55-abs(ix)*.165
    for iy in range(4):tile(x,-2.10+iy*.21,top,rng.choice([10,11,12,13]),.21,.21,.18)
    b('Portico stepped fascia',(x,-2.13,top-.175),(.208,.24,.18),5,.012)
b('Portico ridge timber',(0,-2.20,4.43),(.25,.27,.28),5,.012)

# Double teal door and a stepped, ivory stone arch surround.
for side in [-1,1]:
    for j in range(4):
        z=.94+j*.24;b('Door leaf inset',(side*.23,-1.80,z),(.42,.10,.234),19,.006)
    b('Door stile',(side*.445,-1.885,1.51),(.065,.09,1.40),18,.005)
    b('Door center stile',(side*.035,-1.885,1.51),(.057,.09,1.40),18,.005)
    for z in [1.20,1.63]:b('Door rail',(side*.24,-1.89,z),(.44,.095,.062),18,.005)
    b('Door brass knob',(side*.066,-1.963,1.43),(.042,.04,.048),21,.005)
    for row in range(7):b('Portal stone jamb',(side*.63,-1.94,.90+row*.17),(.18,.31,.164),27,.009)
    b('Door timber reveal',(side*.51,-1.85,1.45),(.10,.15,1.34),5,.008)
for ix in range(-4,5):
    x=ix*.14;top=2.29-math.floor(abs(ix)/1.45)*.12
    b('Arched door infill',(x,-1.80,(1.78+top)/2),(.137,.10,top-1.78),19,.005)
    b('Arch inner timber',(x,-1.91,top+.025),(.138,.14,.13),5,.008)
    b('Arch ivory voussoir',(x,-2.00,top+.16),(.165,.31,.17),27,.01)
    b('Arch second stone course',(x,-1.94,top+.30),(.165,.22,.13),7,.008)
for j in range(5):
    height=.16*(5-j);y=-1.96-j*.20
    course('Wide entry stair',0,y,height/2,1.85,.25,height,cell=.24)
    for side in [-1,1]:b('Stair timber cheek',(side*1.05,y,height/2+.08),(.30,.25,height+.16),5,.012)

# Main roof, interrupted by the front clock tower but continuous at the rear.
for iy in range(15):
    y=(iy-7)*.24;top=4.38+(7-abs(iy-7))*.20
    for ix in range(33):
        x=(ix-16)*.24
        if abs(x)<.83 and -.99<y<.45:continue
        tile(x,y,top,rng.choice([10,10,11,12,13]))
        if iy==0:b('Main front eave fascia',(x,y-.025,top-.22),(.239,.28,.22),5,.01)
        if ix in [0,32]:b('Main roof side fascia',(x,y,top-.22),(.24,.238,.22),5,.01)
    if top>4.6:b('Roof enclosure',(0,y,(4.23+top-.22)/2),(7.14,.24,top-.22-4.23),9,.002)
for side in [-1,1]:
    for j in range(5):b('Main ridge timber end',(side*3.84,-j*.24,5.88-j*.20),(.30,.26,.35),5,.012)
    b('Main eave corner cap',(side*3.84,-1.69,4.35),(.30,.32,.32),5,.012)
for x in [-3.2,-2.7,-2.2,-1.7,1.7,2.2,2.7,3.2]:b('Eave clay tooth',(x,-1.77,4.20),(.14,.12,.13),10,.006)

# Clock tower forward of the ridge. Belfry above is open on all four sides.
cy=-.74
b('Clock tower body',(0,cy,5.40),(1.74,1.59,1.78),8,.003)
for side in [-1,1]:
    b('Clock tower front post',(side*.85,-1.60,5.39),(.16,.21,1.84),5,.012)
    b('Clock tower rear post',(side*.85,.11,5.39),(.16,.19,1.84),5,.012)
    for row in range(9):
        for j in range(7):b('Tower side block',(side*.878,-1.48+j*.24,4.57+row*.19),(.035,.235,.184),8 if row%2 else 9,.004)
b('Clock tower upper beam',(0,cy,6.31),(1.95,1.86,.18),5,.012)
for ix in range(-5,6):
    for iz in range(-5,6):
        if .395<math.hypot(ix*.10,iz*.10)<.56:b('Continuous stepped clock rim',(ix*.10,-1.592,5.40+iz*.10),(.104,.055,.104),5,.006)
for j in range(16):
    angle=math.tau*j/16;x=round(math.sin(angle)*.48/.10)*.10;z=5.40+round(math.cos(angle)*.48/.10)*.10
    size=.17 if j%4==0 else .135
    b('Stepped clock rim',(x,-1.627,z),(size,.09,size),18 if j%2==0 else 5,.009)
b('Clock upper hand',(0,-1.672,5.47),(.070,.08,.32),5,.006)
b('Clock lower hand',(0,-1.682,5.27),(.068,.09,.18),5,.006)
b('Clock hub',(0,-1.72,5.39),(.10,.07,.11),5,.008)
course('Belfry stone floor',0,cy,6.44,1.94,1.87,.18,cell=.20)
for sx in [-1,1]:
    for sy in [-1,1]:
        for row in range(4):b('Belfry open corner pier',(sx*.74,cy+sy*.69,6.65+row*.20),(.31,.33,.194),7 if row%2 else 2,.008)
        b('Belfry corner corbel',(sx*.68,cy+sy*.63,7.34),(.47,.49,.18),2,.009)
course('Belfry projecting cornice',0,cy,7.47,2.22,2.10,.20,cell=.18)

# Low-poly hollow bronze bell: turned profile, actual interior lip and clapper.
profile=[(.095,7.22),(.105,7.10),(.16,7.08),(.19,6.83),(.25,6.79),(.25,6.71),(.19,6.71),(.13,6.84),(.075,7.10)]
n=12;verts=[];faces=[]
for r,z in profile:
    for j in range(n):verts.append((r*math.cos(math.tau*j/n),cy+r*math.sin(math.tau*j/n),z))
for i in range(len(profile)):
    for j in range(n):faces.append((i*n+j,((i+1)%len(profile))*n+j,((i+1)%len(profile))*n+(j+1)%n,i*n+(j+1)%n))
mesh=bpy.data.meshes.new('Bell shell');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(a.material);uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
    for li,(u,v) in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=(21%8/8+.006+u*.113,21//8/8+.006+v*.113)
bell=bpy.data.objects.new('Hollow cast bell',mesh);a.scene.collection.objects.link(bell);bell['part']='Hollow cast bell';a.parts.append(bell)
bell.location=(0,-.40,-.06)
b('Bell hanging stem',(0,cy-.40,7.25),(.07,.07,.25),26,.006)
b('Bell clapper',(0,cy-.40,6.72),(.075,.075,.30),21,.009)
for layer in range(4):
    width=1.83-layer*.35;z=7.67+layer*.20;count=max(1,round(width/.20));step=width/count
    for ix in range(count):
        for iy in range(count):b('Tower hip roof tile',(-width/2+(ix+.5)*step,cy-width/2+(iy+.5)*step,z),(step-.003,step-.003,.194),rng.choice([10,10,11,13]),.006)
for dx in [-1,1]:
    for dy in [-1,1]:b('Tower timber finial',(dx*.105,cy+dy*.105,8.53),(.205,.205,.32),5,.009)

# Two actual framed lanterns flank the front arch.
for side in [-1,1]:
    x=side*.93;y=-1.98;z=1.83
    b('Lantern wall peg',(x,-1.83,z+.22),(.08,.31,.09),5,.005)
    b('Lantern hanger',(x,y,z+.22),(.055,.055,.17),26,.004)
    b('Lantern amber body',(x,y,z),(.15,.14,.23),25,.004)
    for dx in [-1,1]:
        for dy in [-1,1]:b('Lantern cage upright',(x+dx*.085,y+dy*.078,z),(.027,.027,.27),26,.003)
    for dz in [-1,1]:b('Lantern cage cap',(x,y,z+dz*.14),(.22,.20,.055),26,.005)

# Front planting pockets, stone pedestals and ivy tucked into foundation joints.
for side in [-1,1]:
    for layer in range(2):
        for ix in range(4):
            for iy in range(3):b('Flower pocket stone',(side*(1.88+ix*.16),-1.86+iy*.16,.09+layer*.18),(.157,.157,.174),rng.choice([0,1,2]),.006)
    for ix in range(4):
        for iy in range(3):
            b('Flower pocket moss',(side*(1.88+ix*.16),-1.86+iy*.16,.41+(.10 if ix in [1,2] and iy==1 else 0)),(.16,.16,.16),rng.choice([14,15,17]),.008)
    for dx,dy,dz in [(0,0,.09),(-.09,0,0),(.09,0,0),(0,-.07,0)]:b('Front pocket flower',(side*2.15+dx,-1.86+dy,.59+dz),(.10,.10,.11),23 if dz else 22,.005)
    for j in range(9):
        b('Climbing foundation moss',(side*(1.35+j*.25),-1.70,.76+rng.choice([0,.08])),(.21,.21,.15),rng.choice([14,15,16]),.007)

a.studio(focus=(0,-.2,4.30),location=(-6,-22,13.9),scale=11.3)
a.scene.render.resolution_x=1200;a.scene.render.resolution_y=1200
for label,pos,power in [('Key',(-6,-9,15),2100),('Fill',(7,-6,11),1700),('Rim',(2,7,13),1800)]:
    light=next(o for o in a.scene.objects if o.type=='LIGHT' and o.name.startswith(label));light.location=pos;light.data.energy=power;light.data.size=6
    light.rotation_euler=(Vector((0,0,4))-light.location).to_track_quat('-Z','Y').to_euler()
result=a.save()
