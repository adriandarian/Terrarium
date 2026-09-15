"""Three asymmetric leaf clusters, grass stems and four flowers from meadow_shrub.png."""
import sys,random
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
P=[('647813','foliage'),('778a18','foliage'),('506318','foliage'),('8b991c','foliage'),('3b4f14','foliage'),
   ('718312','foliage'),('a29d14','foliage'),('d9cf95','flower'),('f0e8c5','flower'),('aa5918','flower'),('d66b13','flower')]
a=Asset('MeadowShrub','meadow_shrub.png',P);b=a.box;rng=random.Random(715)

def leaf(label,p,size,color=None):
    return b(label,p,size,rng.choice([0,0,1,2,3]) if color is None else color,.003)

# A low, connected cluster; independent cuboids retain the negative spaces between lobes.
leaf('Central dark leaf core',(-.04,.16,.46),(.38,.34,.48),4)
for x,y,z,w,d,h in [(0,.15,1.00,.24,.24,.30),(.13,.27,.87,.25,.26,.23),(.30,.25,.73,.25,.24,.25),
    (-.30,.10,.74,.24,.24,.24),(-.13,-.06,.69,.25,.26,.25),(.10,-.04,.70,.25,.23,.22),
    (.28,.17,.56,.18,.20,.23),(.03,-.22,.49,.22,.21,.25),(-.18,-.16,.43,.18,.18,.21),
    (-.10,.40,.75,.23,.22,.22),(.14,.43,.65,.23,.22,.24),(-.34,.31,.54,.22,.24,.23)]:
    leaf('Central leafy block',(x,y,z),(w,d,h))
    # A few shoulder cubes give each large block a broken, branching edge.
    if rng.random()<.6:leaf('Leaf shoulder',(x+w*.44,y-d*.27,z-h*.27),(.11,.12,.12))

# Shorter left-hand shrub, with its own square terminal leaf column.
leaf('Left dark core',(-.57,-.06,.28),(.41,.34,.43),4)
for x,y,z,w,d,h in [(-.59,.05,.59,.22,.22,.28),(-.50,-.16,.44,.25,.24,.24),(-.71,-.09,.35,.24,.23,.22),
    (-.39,-.09,.29,.25,.24,.23),(-.38,-.29,.22,.22,.22,.25),(-.68,-.29,.19,.22,.23,.26),
    (-.79,-.19,.10,.15,.18,.18),(-.49,.14,.30,.23,.23,.24),(-.27,-.19,.19,.18,.20,.18)]:
    leaf('Left leafy block',(x,y,z),(w,d,h))

# The right lobe is taller at the rear and opens around the orange flower.
leaf('Right dark core',(.48,.12,.31),(.39,.35,.46),4)
for x,y,z,w,d,h in [(.49,.21,.65,.24,.25,.26),(.65,.15,.48,.22,.24,.25),(.32,.09,.46,.22,.22,.27),
    (.47,-.10,.35,.26,.25,.23),(.69,-.06,.24,.21,.22,.23),(.70,-.27,.10,.22,.21,.17),
    (.27,-.36,.10,.24,.23,.17),(.44,-.35,.11,.24,.24,.18),(.59,.34,.38,.22,.21,.23),
    (.19,.08,.26,.18,.18,.21),(.57,-.29,.19,.17,.18,.18)]:
    leaf('Right leafy block',(x,y,z),(w,d,h))

# Uneven small ground leaves link the three lobes without a rectangular base.
# Physical stems also support the crowns from the unpictured rear side.
for label,x,y,h in [('Central supporting stem',-.04,.16,.30),('Left supporting stem',-.57,-.06,.15),('Right supporting stem',.48,.12,.17)]:
    b(label,(x,y,h/2),(.07,.07,h),4,.002)
for x,y,z in [(-.08,.37,.24),(.08,.37,.35),(-.28,.35,.27),(.46,.32,.19),(.62,.33,.16),(-.57,.17,.17)]:
    leaf('Rear leaf',(x,y,z),(.14,.14,.19),2)
for x,y,z in [(-.23,-.34,.08),(-.11,-.38,.07),(.02,-.36,.09),(.13,-.29,.09),(.25,-.48,.07),(.44,-.48,.065),
              (-.57,-.38,.07),(-.38,-.43,.07),(.72,.04,.08),(.03,.46,.10),(-.33,.32,.10)]:
    leaf('Ground leaf',(x,y,z),(.115,.115,.12))
for i,(x,y,h,tilt) in enumerate([(-.50,-.38,.37,0),(-.41,-.45,.18,14),(-.31,-.34,.31,-7),
    (.07,-.16,.55,0),(.19,-.14,.29,8),(.75,.06,.44,0),(.85,-.01,.32,13),(.90,-.13,.25,6),
    (-.06,-.30,.25,-8),(-.62,-.34,.18,-7)]):
    b('Upright grass blade',(x,y,h/2+.005),(.035,.035,h),6 if i%3==0 else 5,.002)
    if tilt:b('Bent grass tip',(x+.012,y,h+.035),(.032,.035,.11),5,.002,rotation=(0,tilt,0))

def flower(x,y,z,orange=False):
    b('Flower stem',(x,y,(z-.02)/2),(.035,.035,z-.02),2,.002)
    b('Flower center',(x,y,z),(.052,.052,.045),9 if orange else 7,.002)
    for dx,dy in [(-.05,0),(.05,0),(0,-.05),(0,.05)]:
        b('Orange petal' if orange else 'Ivory petal',(x+dx,y+dy,z),(.05,.05,.05),10 if orange else 8,.003)
    if orange:b('Raised orange petal',(x,y+.025,z+.063),(.052,.054,.10),10,.003)
for p in [(-.22,-.46,.16),(-.25,-.28,.39),(.01,-.42,.26)]:flower(*p)
flower(.42,-.24,.32,True)
for ob in a.parts:
    if ob.get('part','').startswith('Left'):ob.location.x-=.11
    if ob.get('part','').startswith('Right'):ob.location.x+=.12
    if 'petal' in ob.get('part','').lower():
        for v in ob.data.vertices:v.co*=1.16
    if ob.get('part') in ['Upright grass blade','Bent grass tip']:
        ob.location.z*=1.25
        for v in ob.data.vertices:v.co.z*=1.25
    ob.location.y*=.80;ob.location.z*=.82
    for v in ob.data.vertices:v.co.y*=.80;v.co.z*=.82
a.studio(focus=(.03,0,.43),location=(-4,-8,5.6),scale=2.30)
a.scene.render.resolution_x=1100;a.scene.render.resolution_y=1100
a.scene.view_settings.exposure=-.40
result=a.save()
