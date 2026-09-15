"""Seven-stripe market stall from market_stall.png; open structure and counters."""
import sys,random
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
P=[('795125','wood'),('66451f','wood'),('97672e','wood'),('a77a36','endgrain'),
   ('a2a28b','stone'),('858c76','stone'),('b7b49a','stone'),
   ('037e6c','cloth'),('efd298','cloth'),('066753','cloth'),
   ('6d8430','moss'),('879a39','moss'),('a4b44c','moss'),
   ('d3641d','produce'),('ed9230','produce'),('b7831e','produce'),('e9b647','produce'),
   ('bfc987','produce'),('737fa2','bottle'),('556687','bottle'),('438f84','bottle'),
   ('ecdca5','flower'),('523a1f','wood')]
a=Asset('MarketStall','market_stall.png',P);b=a.box;rng=random.Random(86)

def course(label,x,y,z,width,depth,height,cell=.22):
    n=max(1,round(width/cell))
    for i in range(n):b(label,(x-width/2+(i+.5)*width/n,y,z),(width/n-.005,depth,height),rng.choice([4,5,6]),.006)

# Small dressed-stone footing and plank deck, fitted to the stand.
b('Foundation interior',(0,0,.17),(3.42,1.91,.32),5,.006)
for z in [.105,.285]:
    for y in [-.97,.97]:course('Foundation courses',0,y,z,3.55,.19,.174)
    for x in [-1.69,1.69]:
        for j in range(9):b('Side stone courses',(x,-.85+j*.2125,z),(.22,.206,.174),rng.choice([4,5,6]),.006)
for x in range(15):
    for y in range(8):b('Wood deck',(-1.57+x*.224,-.785+y*.224,.36),(.22,.22,.10),rng.choice([0,2]),.003)
course('Central doorstep',0,-1.20,.095,.76,.35,.18,cell=.25)
for x in [-.50,.50]:b('Step timber end',(x,-1.20,.10),(.22,.35,.21),1,.007)
# Four load-bearing uprights, with raised square feet and caps.
for x in [-1.52,1.52]:
    for y,top in [(-.79,2.58),(.78,2.92)]:
        b('Timber upright',(x,y,(.40+top)/2),(.235,.235,top-.40),0,.010)
        b('Square post shoe',(x,y,.54),(.35,.35,.36),0,.010)
        for dx in [-.075,.075]:
            for dy in [-.075,.075]:b('Projecting post head',(x+dx,y+dy,top),(.147,.147,.22),0,.008)
for y,z in [(-.79,2.38),(.78,2.63)]:b('Cross beam',(0,y,z),(3.35,.22,.22),1,.008)
for x in [-1.52,1.52]:
    b('Side beam',(x,0,2.55),(.22,1.65,.20),1,.007,rotation=(12,0,0))
    for side in [-1,1]:
        for j in range(3):b('Stepped corner brace',(x-side*(.09+j*.07),-.79,2.22+j*.055),(.20,.19,.19),1,.005)
# Seven alternating stripes; small solids create the concept's shallow seams.
stripe=.46
for k in range(7):
    color=7 if k%2==0 else 8
    x=(k-3)*stripe
    for ix in [-1,1]:
        for row in range(8):
            y=-.955+row*.25;z=2.50+row*.043
            b('Striped awning tile',(x+ix*.115,y,z),(.228,.252,.09),color,.004,rotation=(9.76,0,0))
        b('Awning front valance',(x+ix*.115,-1.092,2.411),(.228,.088,.17),color,.004)
    b('Stepped valance tab',(x,-1.095,2.30),(.235,.087,.08),color,.003)
# Two separate stalls leave an open central entrance under the canopy.
for side in [-1,1]:
    cx=side*.96
    for row in range(3):b('Counter front plank',(cx,-.865,.52+row*.165),(1.35,.14,.16),0 if row%2 else 1,.006)
    for edge in [-1,1]:
        b('Counter corner leg',(cx+edge*.60,-.86,.72),(.145,.19,.73),1,.007)
        for row in range(3):b('Counter side plank',(cx+edge*.605,-.50,.55+row*.16),(.12,.77,.155),0,.006)
    for ix in range(6):
        for iy in range(4):b('Countertop block',(cx-.575+ix*.23,-.86+iy*.23,1.025),(.226,.226,.13),2,.004)

def crate(x,y,z,w=.46,d=.42,h=.36):
    b('Crate bottom',(x,y,z-h/2+.04),(w,d,.07),1,.004)
    for side in [-1,1]:
        for j in range(3):
            b('Open crate slat',(x,y+side*d/2,z-h/2+(j+.5)*h/3),(w,.066,h/3-.009),0,.004)
            b('Open crate end',(x+side*w/2,y,z-h/2+(j+.5)*h/3),(.066,d,h/3-.009),1,.004)
        for sy in [-1,1]:b('Crate corner',(x+side*(w/2-.02),y+sy*(d/2-.02),z),(.074,.074,h+.03),0,.005)

crate(-1.00,-.22,1.32,.49,.44,.46)
crate(.77,-.26,1.30,.47,.43,.40)
crate(1.22,.34,1.45,.43,.38,.39)
# Low front trays and identifiable cube produce, placed like the reference.
for x,y in [(-.58,-.65),(.55,-.65),(1.27,-.58)]:
    crate(x,y,1.20,.38,.34,.25)
for x,y,color in [(-.58,-.65,13),(.55,-.65,16),(1.27,-.58,13)]:
    for dx,dy,dz in [(-.076,-.035,0),(.076,-.035,0),(0,.07,.12)]:b('Stacked produce',(x+dx,y+dy,1.42+dz),(.14,.14,.14),color,.008)
for dx,dy,dz in [(0,0,0),(-.05,.04,.12),(.06,.05,.20)]:b('Leafy vegetables',(-.94+dx,-.65+dy,1.20+dz),(.17,.16,.17),11 if dz else 10,.006)
for x,y,index in [(-1.27,-.76,18)]:
    b('Square bottle body',(x,y,1.235),(.18,.18,.29),index,.006)
    b('Bottle shoulder',(x,y,1.395),(.135,.135,.07),index,.005)
    b('Bottle neck',(x,y,1.46),(.078,.078,.065),19 if index==18 else 20,.004)
    b('Bottle stopper',(x,y,1.50),(.090,.090,.027),17,.003)
for dx in [-.059,.059]:
    for dy in [-.059,.059]:
        for dz in [-.059,.059]:b('Teal wrapped goods',(.89+dx,-.70+dy,1.216+dz),(.116,.116,.116),20,.007)
# A folded turquoise runner hangs down the left counter's front.
b('Cloth runner top',(-.68,-.88,1.106),(.27,.33,.038),7,.003)
for row in range(2):b('Cloth runner drop',(-.68,-1.046,.994-row*.13),(.27,.041,.13),7 if row else 9,.003)
# Hanging merchant token: arm, two square loops, wooden medallion and teal inset.
b('Token support arm',(1.86,-.79,2.37),(.69,.12,.13),0,.006)
for x in [1.94,2.10]:b('Token strap',(x,-.79,2.37),(.066,.18,.21),2,.004)
b('Token stem',(2.02,-.79,2.15),(.074,.074,.30),1,.004)
b('Token center',(2.02,-.80,1.96),(.33,.12,.34),2,.006)
for x,z in [(1.825,1.96),(2.215,1.96),(2.02,1.755),(2.02,2.165)]:b('Token stepped edge',(x,-.80,z),(.13,.12,.13),0,.005)
b('Teal merchant inset',(2.02,-.88,1.96),(.16,.055,.17),7,.005)
# Small plants wrap each visible foundation corner; no freestanding pedestal.
for side in [-1,1]:
    for x,y,z in [(1.67,-.98,.27),(1.52,-1.05,.13),(1.78,-.89,.13),(1.59,-.98,.43),(1.80,-.66,.22)]:
        b('Corner moss',(side*x,y,z),(.17,.19,.16),rng.choice([10,11,12]),.005)
    for dx,dz in [(-.045,0),(.045,0),(0,.09)]:b('Corner flower',(side*1.62+dx,-1.05,.48+dz),(.085,.085,.09),21 if side<0 else 14,.004)
    for x,y,z in [(1.80,-1.08,.10),(1.62,-1.23,.09),(1.42,-1.20,.08),(1.94,-.80,.08),(1.90,-.58,.15)]:
        b('Spreading foundation moss',(side*x,y,z),(.20,.22,.16),rng.choice([10,11,12]),.008)
# The concept is broad and low; compress the authored vertical grid consistently.
for ob in a.parts:
    ob.location.z *= .86
    for vertex in ob.data.vertices:vertex.co.z *= .86
a.studio(focus=(.17,0,1.30),location=(-3.7,-10,5.0),scale=5.15)
a.scene.render.resolution_x=1100;a.scene.render.resolution_y=1100
result=a.save()
