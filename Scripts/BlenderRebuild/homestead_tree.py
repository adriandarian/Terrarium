"""Homestead tree: stepped forks, an irregular olive crown and sparse low branches."""
import sys,math,random
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
P=[('727713','canopy'),('808315','canopy'),('626c13','canopy'),('8c8b18','canopy'),('495611','canopy'),
   ('684218','timber'),('785020','timber'),('5c3e18','timber'),('875821','timber'),('62691a','canopy')]
a=Asset('HomesteadTree','homestead_tree_v2.png',P);b=a.box;rng=random.Random(913)
# u spans the reference image; v moves deeper into the tree, away from the camera.
def xyz(u,v,z):return ((u+v)/math.sqrt(2),(v-u)/math.sqrt(2),z)
wood=set();cell=.075
def limb(points,width):
    count=max(1,round(width/cell));offsets=range(-(count//2),count-count//2)
    points=[xyz(*p) for p in points]
    for start,end in zip(points,points[1:]):
        steps=max(1,math.ceil(math.dist(start,end)/(cell*.35)))
        for i in range(steps+1):
            p=[round((start[k]+(end[k]-start[k])*i/steps)/cell) for k in range(3)]
            for dx in offsets:
                for dy in offsets:
                    for dz in offsets:wood.add((p[0]+dx,p[1]+dy,p[2]+dz))
limb([(0,0,.15),(0,0,1.40),(.07,.03,1.9),(.10,.04,2.55)],.30)
# A few thicker roots blend the trunk into the uneven mossy foot.
for u,v in [(-.37,-.17),(.30,-.26),(-.25,.31),(.36,.23),(0,-.40)]:
    limb([(0,0,.31),(u*.50,v*.50,.15),(u,v,.09)],.15)
paths=[([(0,0,.98),(-.28,-.02,1.07),(-.28,-.02,1.24),(-.72,-.03,1.24),(-.78,-.03,1.40)],.15),
       ([(0,.02,1.45),(.31,.03,1.57),(.31,.03,1.72),(.82,.03,1.89),(.94,.03,2.07)],.225),
       ([(0,0,1.63),(-.35,0,1.78),(-.35,0,1.97),(-.93,0,2.12)],.225),
       ([(.05,.03,2.00),(.38,.07,2.16),(.38,.07,2.35),(.59,.07,2.51)],.15),
       ([(.07,.05,2.17),(-.36,.07,2.34),(-.36,.07,2.53),(-.53,.07,2.71)],.15),
       ([(0,0,1.52),(-.22,-.28,1.70),(-.22,-.28,1.93)],.15),
       ([(.55,.03,1.81),(.76,-.04,1.68),(.76,-.04,1.32)],.075),
       ([(.02,.06,1.84),(.10,.44,2.03),(.34,.47,2.25)],.15)]
for points,width in paths:limb(points,width)
# Only the exterior bark cubes are needed; every authored cube remains closed.
for ix,iy,iz in sorted(wood):
    if iz<0:continue
    if all((ix+dx,iy+dy,iz+dz) in wood for dx,dy,dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]):continue
    b('Stepped bark',(ix*cell,iy*cell,iz*cell+cell/2),(cell+.0003,)*3,5+(ix*3+iy+iz//3)%4,.0012)

def leaf(u,v,z,w=.235,d=.235,h=.235,color=None,label='Crown leaf'):
    return b(label,xyz(u,v,z),(w,d,h),rng.choice([0,2,4] if z<2.15 else [0,0,1,2,3]) if color is None else color,.0025)
# Columns establish the top silhouette without a spherical or flat canopy.
columns=[(-.03,.17,3.22,.28,.28,.36),(.23,.19,3.34,.28,.28,.25),(-.26,.16,3.13,.26,.26,.31),
         (.04,-.03,3.10,.27,.27,.27),(.29,-.02,3.11,.29,.26,.24),(.48,.12,3.10,.26,.27,.23),
         (-.57,.05,2.99,.25,.26,.31),(-.77,.02,2.93,.23,.24,.31),(-.57,-.18,2.82,.24,.24,.29),
         (-.39,-.21,2.67,.24,.25,.31),(-.16,-.16,2.90,.25,.25,.27),(.17,-.24,2.88,.26,.25,.25),
         (.45,-.04,2.82,.26,.26,.30),(.68,.03,2.66,.25,.26,.28),(.81,.16,2.73,.24,.24,.29),
         (.91,.10,2.47,.25,.24,.27),(.66,-.19,2.42,.24,.25,.29),(.93,-.14,2.27,.24,.24,.22),
         (-.95,.04,2.37,.25,.25,.32),(-.75,-.17,2.47,.26,.25,.28),(-.99,-.16,2.11,.24,.26,.31),
         (-1.15,-.07,2.05,.23,.23,.29),(-.88,-.32,2.22,.24,.24,.25),(-.62,-.34,2.06,.24,.24,.23),
         (-.34,-.25,2.27,.24,.25,.23),(-.04,-.29,2.42,.25,.26,.26),(.18,-.22,2.49,.24,.24,.27),
         (.38,-.14,2.54,.24,.25,.26),(.52,.02,2.24,.25,.24,.23),(-.13,.12,2.76,.42,.40,.45),
         (.16,.21,2.62,.43,.39,.45),(-.43,.12,2.54,.34,.31,.39),(.39,.19,2.47,.32,.32,.39),
         (-.72,.14,2.20,.32,.30,.37),(.77,.15,2.21,.30,.31,.34)]
for values in columns:leaf(*values)
for u,v,z,w,d,h in [(0,.02,2.27,.50,.44,.44),(-.48,.04,2.19,.33,.30,.32),(.40,.13,2.09,.34,.30,.35),
                    (-.19,.15,2.99,.39,.38,.35),(.33,.19,2.84,.36,.35,.36)]:leaf(u,v,z,w,d,h,4,'Inner shaded foliage')
# Inferred rear leaves continue the branching crown while keeping its sides open.
for u,v,z in [(-.25,.49,2.94),(.05,.51,3.06),(.31,.48,2.91),(-.47,.42,2.70),(.56,.40,2.65),
              (-.65,.35,2.40),(.77,.32,2.38),(-.13,.53,2.51),(.30,.53,2.35),(-.76,.37,2.10),(.59,.44,2.12)]:leaf(u,v,z,.27,.27,.30,2,'Rear leaf')
def cluster(u,v,z,shape,label):
    for du,dv,dz,w,d,h in shape:leaf(u+du,v+dv,z+dz,w,d,h,label=label)
small=[(0,0,0,.24,.24,.30),(-.17,0,-.12,.20,.22,.24),(.16,.03,-.12,.21,.22,.22),(0,-.14,-.21,.18,.19,.24),(0,.12,-.09,.20,.21,.23)]
cluster(-.78,-.03,1.33,small,'Lower left leaves')
cluster(.80,-.04,1.29,[(0,0,0,.20,.21,.24),(-.14,0,.09,.18,.19,.25),(.10,-.09,-.12,.19,.18,.25)],'Lower right leaves')
cluster(-.22,-.28,1.97,small,'Front twig leaves')
cluster(1.02,.03,1.95,[(0,0,0,.27,.27,.26),(-.20,-.10,-.09,.24,.24,.30),(.22,.02,.06,.24,.24,.23),(.34,.06,-.13,.20,.23,.21),(.07,-.18,-.23,.21,.21,.24)],'Right branch leaves')
for u,v in [(-.36,-.17),(.32,-.26),(-.25,.30),(.37,.23),(0,-.40),(-.24,-.31),(.20,.28)]:leaf(u,v,.095,.19,.19,.19,9,'Mossy root')
a.studio(focus=(0,0,1.77),location=(-8,-8,7.8),scale=4.50)
a.scene.render.resolution_x=1100;a.scene.render.resolution_y=1200
a.scene.view_settings.exposure=-.25
result=a.save()
