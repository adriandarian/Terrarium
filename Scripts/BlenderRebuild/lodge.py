"""Raised-dormer lodge built from lodge.png in a verified Blender scene."""
import bpy,math,random,sys
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
P=[('a7a591','stone'),('999b87','stone'),('b9b39b','stone'),('888d79','stone'),
   ('664525','timber'),('52391d','timber'),('785027','timber'),('a45423','timber'),
   ('e9debe','plaster'),('dfd3b2','plaster'),('ad5231','clay'),('b65832','clay'),('a84e2e','clay'),('bd6035','clay'),
   ('70872b','moss'),('899c31','moss'),('5d7424','moss'),('9aaa3b','moss'),
   ('08766d','glass'),('07584f','glass'),('118e82','glass'),('e4a42f','metal'),
   ('eee2aa','flower'),('dd7827','flower'),('302b20','shadow')]
a=Asset('Lodge','lodge.png',P);b=a.box;rng=random.Random(906)

def masonry(label,x,y,z,w,d,h,cell=.28):
    n=max(1,round(w/cell));rows=max(1,round(h/.20))
    for row in range(rows):
        edges=[-w/2]+[v for i in range(n+1) if -w/2<(v:=-w/2+(i+(.5 if row%2 else 0))*w/n)<w/2]+[w/2]
        for x0,x1 in zip(edges,edges[1:]):
            b(label,(x+(x0+x1)/2,y,z-h/2+(row+.5)*h/rows),(x1-x0-.006,d,h/rows-.006),rng.choice([0,0,1,2,3]),.009)

def window(x,y,z,w,h):
    # Opaque teal glazing behind actual timber reveals and a cruciform mullion.
    b('Window recess',(x,y+.075,z),(w,.055,h),24,.002)
    for sx in [-1,1]:
        for sz in [-1,1]:
            b('Inset teal pane',(x+sx*w*.225,y+.025,z+sz*h*.23),(w*.41,.045,h*.43),19,.005)
            b('Teal pane inner sill',(x+sx*w*.225,y-.005,z+sz*h*.23-h*.185),(w*.40,.085,.04),18,.004)
    b('Teal vertical mullion',(x,y-.045,z),(.070,.12,h),18,.006)
    b('Teal horizontal mullion',(x,y-.048,z),(w,.12,.065),20,.006)
    for sx in [-1,1]:b('Window timber jamb',(x+sx*(w/2+.045),y-.055,z),(.105,.19,h+.08),4,.013)
    b('Window lintel',(x,y-.055,z+h/2+.07),(w+.25,.21,.15),4,.013)
    b('Projecting window sill',(x,y-.14,z-h/2-.085),(w+.32,.35,.15),6,.014)

# Four masonry courses with locally stepped corner footing.
b('Foundation core',(0,0,.34),(4.38,3.20,.68),1,.008)
for y in [-1.64,1.64]:masonry('Foundation courses',0,y,.36,4.50,.24,.72)
for side in [-1,1]:
    for row in range(4):
        for j in range(12):b('Side foundation block',(side*2.20,-1.48+j*.27,.09+row*.18),(.23,.264,.174),rng.choice([0,1,2,3]),.009)

# Ground-floor infill stops behind the recessed openings.
b('Plaster body',(0,.09,1.61),(4.10,2.82,1.78),8,.004)
for side in [-1,1]:
    for x,w in [(1.94,.29),(.74,.32)]:b('Facade plaster',(side*x,-1.51,1.65),(w,.24,1.84),8,.004)
    b('Below window plaster',(side*1.32,-1.51,.94),(.94,.24,.44),9,.004)
    b('Above window plaster',(side*1.32,-1.51,2.35),(.94,.24,.34),8,.004)
    for y in [-1.52,1.47]:b('Corner timber',(side*2.08,y,1.72),(.26,.29,1.96),4,.018)
    window(side*1.32,-1.69,1.65,.70,.94)
    for row in range(5):
        # Restrained block joints on the exposed side plaster.
        for j in range(7):b('Side plaster blocks',(side*2.062,-1.30+j*.42,.92+row*.32),(.038,.416,.315),8 if row%2 else 9,.003)
b('Front floor beam',(0,-1.85,2.62),(4.47,.28,.26),5,.016)
b('Rear floor beam',(0,1.59,2.62),(4.47,.26,.26),5,.016)
for side in [-1,1]:b('Side eave beam',(side*2.19,0,2.64),(.25,3.69,.26),4,.016)

# Four warm planks form the inset door, with a square brass latch.
b('Door shadow',(0,-1.62,1.46),(1.02,.12,1.54),24,.003)
for j in range(4):b('Door plank',(-.378+j*.252,-1.735,1.48),(.246,.10,1.52),7 if j%2 else 11,.008)
for side in [-1,1]:b('Door jamb',(side*.57,-1.80,1.4275),(.18,.25,1.575),4,.016)
b('Door header',(0,-1.80,2.30),(1.35,.25,.17),6,.014)
b('Brass latch',(.33,-1.895,1.48),(.16,.13,.17),21,.012)
for j in range(3):
    h=.22*(3-j);y=-1.89-j*.29
    masonry('Entry stair',0,y,h/2,1.25,.34,h,cell=.42)
    for side in [-1,1]:b('Entry stair cheek',(side*.76,y,h/2+.08),(.28,.34,h+.16),5,.012)

# Dormer panel: this upper window and tall rectangular bay distinguish the lodge.
for side in [-1,1]:
    b('Dormer cheek plaster',(side*.65,-1.79,3.12),(.40,.20,.93),8,.005)
    b('Dormer side upright',(side*.91,-1.91,3.12),(.23,.27,1.02),4,.016)
    b('Dormer projecting beam end',(side*.91,-1.99,2.64),(.32,.36,.26),5,.016)
    b('Dormer beam corbel',(side*.91,-1.86,2.41),(.25,.26,.23),5,.013)
b('Dormer below-window plaster',(0,-1.78,2.80),(.95,.20,.29),8,.003)
b('Dormer over-window plaster',(0,-1.78,3.54),(.95,.20,.18),8,.003)
window(0,-1.94,3.21,.47,.57)
for ix in range(-4,5):
    x=ix*.235;top=4.10-math.floor(abs(x)/.27)*.27;bottom=3.57
    if top>bottom:b('Dormer gable infill',(x,-1.80,(top+bottom)/2),(.234,.19,top-bottom),8,.003)
b('Dormer gable upright',(0,-1.93,3.84),(.17,.13,.55),5,.01)

# Roof: seven large courses; finer subdivided clay blocks give shallow seams.
def tile(x,y,z,color,w=.27,d=.27,h=.255):
    for dx in [-1,1]:
        for dy in [-1,1]:
            for dz in [-1,1]:b('Clay roof subtile',(x+dx*w/4,y+dy*d/4,z+dz*h/4),(w/2-.002,d/2-.002,h/2-.002),color,.004)

for iy in range(15):
    y=(iy-7)*.27;main=2.92+(7-abs(iy-7))*.255
    for ix in range(19):
        x=(ix-9)*.27
        cross=4.45-math.floor(abs(x)/.27+.001)*.27 if y<.10 and abs(x)<1.35 else 0
        top=max(main,cross)
        tile(x,y,top,rng.choice([10,10,11,12,13]))
        if cross>main+.10 and iy>0:b('Cross-roof riser',(x,y,(cross+main)/2-.08),(.266,.266,cross-main+.09),10,.006)
        if iy==0:b('Front stepped roof fascia',(x,y-.025,top-.255),(.269,.31,.25),5,.012)
        if ix in [0,18]:b('Side roof fascia',(x,y,top-.255),(.27,.269,.25),4,.012)
    if main>3.2:b('Enclosed roof core',(0,y,(main-.22+2.62)/2),(4.35,.27,main-.22-2.62),9,.003)
# Wood ridge end caps and lower eave corbels.
for side in [-1,1]:
    for row in range(2):b('Ridge timber cap',(side*2.43,row*.27,4.69-row*.255),(.33,.29,.31),5,.014)
    for y in [-1.62,1.61]:
        b('Eave corner cap',(side*2.43,y,2.91),(.34,.38,.42),5,.017)
        for j in range(2):b('Eave bracket',(side*(2.15-j*.08),y,2.38-j*.13),(.28-j*.05,.25,.16),5,.010)
for x in [-1.73,-1.35,1.35,1.73]:b('Front eave tile tooth',(x,-1.965,2.765),(.16,.15,.15),10,.007)

# Left masonry chimney emerges through the slope and ends in a pale slab/crown.
cx=-1.68;cy=-.50
b('Chimney solid',(cx,cy,4.41),(.61,.58,1.74),1,.005)
for row in range(8):
    z=3.68+row*.19
    for side in [-1,1]:
        for j in range(2):
            b('Chimney front masonry',(cx+(j-.5)*.32,cy+side*.32,z),(.313,.10,.184),[0,2,1][row%3],.008)
            b('Chimney side masonry',(cx+side*.32,cy+(j-.5)*.32,z),(.10,.313,.184),[2,0,1][row%3],.008)
for dx in [-1,1]:
    for dy in [-1,1]:
        b('Chimney capstone',(cx+dx*.21,cy+dy*.21,5.21),(.414,.414,.22),2,.014)
        b('Chimney clay crown',(cx+dx*.12,cy+dy*.12,5.46),(.234,.234,.28),11,.011)

# Clustered, irregular moss wraps the foundation, with physical tiny flowers.
for side in [-1,1]:
    for layer,coords in enumerate([[(0,0),(1,0),(2,0),(3,1),(0,1),(1,1),(2,1),(3,2),(0,2),(1,2),(2,2)],
                                  [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(1,2),(2,2)],
                                  [(0,1),(1,0),(1,1),(2,1),(1,2)],[(0,1),(1,1)]]):
        for ix,iy in coords:
            x=side*(1.65+ix*.20);y=-1.96+iy*.19
            b('Moss corner cushion',(x,y,.78+layer*.17),(.21,.20,.185),rng.choice([14,15,16,17]),.01)
    for x,y,z in [(1.55,-2.04,.58),(1.87,-2.08,.39),(2.26,-1.95,.28),(2.40,-1.70,.48),(2.34,-1.42,.75),(1.04,-2.03,.15),(1.11,-1.84,.33)]:
        b('Creeping moss spill',(side*x,y,z),(.24,.24,.25),rng.choice([14,15,16]),.014)
    for x in range(4):
        for y in range(3):
            if x+y>4:continue
            for row in range(3):b('Corner stepped stone',(side*(1.58+x*.23),-1.93+y*.20,.12+row*.21),(.225,.22,.204),rng.choice([0,1,2]),.009)
    for j in range(10):
        if rng.random()<.85:b('Side moss',(side*2.25,-1.30+j*.29,.70+rng.choice([0,.17])),(.24,.27,.24),rng.choice([14,15,16]),.012)
    for dx,dy,dz in [(0,0,.09),(-.10,0,0),(.09,0,0),(0,-.07,0)]:b('Corner flower',(side*1.86+dx,-2.08+dy,1.02+dz),(.11,.11,.12),22 if side<0 else 23,.006)
    for dx,dz in [(-.04,0),(.04,0),(0,.075)]:b('Small ivory flower',(side*1.50+dx,-2.03,.90+dz),(.085,.085,.095),22,.005)

a.studio(focus=(0,-.1,2.67),location=(-4.8,-14,8.5),scale=8.1)
a.scene.render.resolution_x=1100;a.scene.render.resolution_y=1100
from mathutils import Vector
for label,pos,power in [('Key',(-4,-6,10),1100),('Fill',(5,-3,7),700),('Rim',(1,5,9),850)]:
    light=next(o for o in a.scene.objects if o.type=='LIGHT' and o.name.startswith(label))
    light.location=pos;light.data.energy=power
    light.rotation_euler=(Vector((0,0,2.7))-light.location).to_track_quat('-Z','Y').to_euler()
a.scene.view_settings.exposure=-.25
result=a.save()
