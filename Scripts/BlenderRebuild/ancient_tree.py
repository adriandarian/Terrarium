"""The broad ancient tree from tree.png, with five distinct crowns and hanging vines."""
import sys,math,random
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
P=[('93652f','mineral'),('a97739','mineral'),('805828','mineral'),('ab7b40','mineral'),('6c532f','mineral'),
   ('8c913c','mineral'),('a09b43','mineral'),('6b7c3c','mineral'),('768442','mineral'),('586e40','mineral'),
   ('548c77','mineral'),('81ab93','mineral'),('3e735e','mineral'),('c75d30','flower'),('e17c44','flower'),('ad4b29','flower'),('727d38','mineral')]
a=Asset('AncientTree','tree.png',P);b=a.box;rng=random.Random(1309)
def xyz(u,v,z):return ((u+v)/math.sqrt(2),(v-u)/math.sqrt(2),z)
# A coarse, irregular wood lattice keeps branch forks solid and the root profile stepped.
cell=.135;wood=set()
def timber_box(u,v,z,w,d,h):
    x,y,z=xyz(u,v,z)
    ranges=[range(math.floor((p-s/2)/cell),math.ceil((p+s/2)/cell)) for p,s in zip((x,y,z),(w,d,h))]
    for ix in ranges[0]:
        for iy in ranges[1]:
            for iz in ranges[2]:
                if iz>=0:wood.add((ix,iy,iz))
for u,v,z,w,d,h in [(0,0,1.6,.50,.49,3.2),(-.20,.03,1.06,.31,.30,2.12),(.24,.12,.79,.31,.30,1.58),
                     (.08,.08,2.85,.35,.36,1.17),(-.20,-.20,.43,.34,.33,.86),(.34,-.14,.36,.30,.32,.72)]:timber_box(u,v,z,w,d,h)
# Thick exposed horizontal forks and their raised shoulders.
for u,v,z,w,d,h in [(-.62,-.04,1.46,1.17,.26,.26),(-1.20,-.04,1.65,.27,.27,.48),
                     (.65,.10,1.93,1.05,.27,.27),(1.15,.10,2.16,.29,.29,.50),
                     (-.64,.07,2.58,.93,.29,.26),(-1.10,.07,2.76,.28,.28,.46),
                     (.62,.10,2.99,1.00,.29,.26),(1.12,.10,3.15,.29,.29,.43)]:
    # Screen-space branch lengths become a connected path of world-aligned cubes.
    steps=max(1,math.ceil(w/.09))
    for i in range(steps):timber_box(u-w/2+(i+.5)*w/steps,v,z,.20,d,h)
for u,v,w,h in [(-.62,-.36,.43,.26),(.55,-.35,.48,.28),(-.55,.39,.44,.32),(.59,.37,.42,.29),
                 (-.22,-.65,.42,.16),(.27,-.65,.42,.17),(-.23,.61,.41,.25),(.26,.58,.41,.22),
                 (-.37,-.23,.37,.58),(.43,.17,.34,.52)]:timber_box(u,v,h/2,w,w,h)
for u,v,z,w,h in [(-.28,-.29,.94,.26,.38),(.32,-.27,1.27,.27,.43),(-.30,.06,1.71,.27,.36),(.17,-.26,2.41,.29,.47),
                   (-.20,-.20,2.92,.28,.43),(.29,.20,.56,.30,.36),(.39,-.20,.88,.28,.32)]:timber_box(u,v,z,w,w,h)
for ix,iy,iz in sorted(wood):
    if all((ix+dx,iy+dy,iz+dz) in wood for dx,dy,dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]):continue
    color=rng.choices([0,1,2,3,4],[4,3,2,1,1])[0]
    b('Bark voxel',((ix+.5)*cell,(iy+.5)*cell,(iz+.5)*cell),(cell-.0015,)*3,color,.0055)

def leaves(label,u,v,z,w,d,h,color=None):
    # Broad ledges retain visible voxel joints but avoid random ball-shaped canopies.
    x,y,z=xyz(u,v,z);n=[max(1,round(s/.145)) for s in (w,d,h)]
    color=rng.choice([5,5,6,7,8,9]) if color is None else color
    for ix in range(n[0]):
        for iy in range(n[1]):
            for iz in range(n[2]):
                if all(0<q<nn-1 for q,nn in zip((ix,iy,iz),n)):continue
                p=(x-w/2+(ix+.5)*w/n[0],y-d/2+(iy+.5)*d/n[1],z-h/2+(iz+.5)*h/n[2])
                b(label,p,(w/n[0]-.001,d/n[1]-.001,h/n[2]-.001),color,.006)
# Tall central crown, offset to the left of the trunk as in the original.
main=[(-.15,.12,3.65,1.14,.86,.80),(-.17,.14,4.12,.70,.62,.29),(-.16,.14,4.35,.43,.41,.17),
      (-.57,.08,3.95,.44,.48,.29),(-.72,-.01,3.69,.43,.44,.31),(-.48,-.27,3.81,.43,.40,.32),
      (-.17,-.40,3.69,.42,.41,.38),(.19,-.22,4.00,.44,.40,.34),(.40,.01,3.77,.35,.35,.42),
      (.43,-.16,3.44,.38,.36,.29),(-.65,.12,3.45,.40,.40,.30),(-.37,-.34,3.41,.35,.37,.36),
      (.18,.42,3.72,.42,.38,.42),(-.32,.45,3.77,.42,.38,.36)]
for row in main:leaves('Upper crown',*row)
# Four separate branch crowns; each has asymmetric ledges and visible air beneath it.
crown_specs=[('Lower left',-1.45,-.06,1.91,1.17),('Upper left',-.98,.07,3.08,1.08),
             ('Upper right',1.27,.10,3.34,1.12),('Lower right',1.45,.11,2.32,1.14)]
shape=[(0,0,0,.66,.61,.34),(-.24,-.10,-.12,.34,.34,.28),(.27,.03,-.12,.34,.35,.31),
       (-.08,.05,.24,.43,.40,.24),(.17,.12,.14,.37,.36,.27),(-.38,.09,-.16,.25,.27,.28),
       (.38,-.05,-.22,.24,.26,.27),(-.14,-.26,-.18,.30,.29,.30)]
for label,u,v,z,scale in crown_specs:
    for du,dv,dz,w,d,h in shape:leaves(label+' crown',u+du*scale,v+dv*scale,z+dz*scale,w*scale,d*scale,h*scale)
    # Hanging chains join the underside of each crown; different lengths break the lower edge.
    for j,(du,dv,count) in enumerate([(-.30,-.13,5),(-.12,-.28,8),(.06,-.22,10),(.26,-.15,6),(.31,.08,4)]):
        if label=='Upper left':count=max(2,count-4)
        for k in range(count):
            side=.078 if k>count-3 else .096
            leaves('Hanging vine',u+du*scale+.022*math.sin(k*.8+j),v+dv*scale,z-.27*scale-k*.086,side,side,.087,rng.choice([7,8,9]))
# Teal accent leaf cubes sit on the nearer faces, not in a flat front decal.
for u,v,z,w in [(-.13,-.62,3.56,.25),(-1.26,-.30,2.86,.24),(-1.38,-.38,1.91,.24),(1.44,-.26,3.25,.27),
                 (1.66,-.27,2.25,.23),(.27,-.36,.63,.23),(.31,-.31,1.55,.21)]:
    leaves('Teal accent leaves',u,v,z,w,w,w,11)
    leaves('Teal shaded support',u+.03,v+.09,z-.18,w*.90,w*.9,.18,10)
    leaves('Teal side leaf',u-.15,v+.06,z-.15,w*.75,w*.8,.18,12)
    leaves('Teal lower leaf',u+.14,v+.04,z-.24,w*.65,w*.72,.19,10)
# Small moss blocks climb the trunk and mingle with the projecting root toes.
for u,v,z,s in [(-.35,-.33,.39,.16),(.30,-.38,.51,.18),(-.23,-.35,.85,.15),(.38,-.26,1.08,.18),
                 (-.28,-.31,1.48,.17),(.22,-.32,1.72,.15),(-.20,-.31,2.17,.18),(.37,-.17,2.48,.16),
                 (-.50,-.35,.19,.15),(.56,-.31,.20,.14),(-.21,-.65,.11,.13),(.28,-.62,.15,.17)]:leaves('Trunk moss',u,v,z,s,s,s,16)
def flower(u,v,z,s=.08):
    for du,dv,dz,color in [(0,0,0,15),(-s,0,0,13),(s,0,0,14),(0,0,s,14),(0,0,-s,13),(0,-s*.4,-s*.8,13)]:
        b('Orange blossom',xyz(u+du,v+dv,z+dz),(s,s,s),color,.006)
for p in [(.31,-.03,4.26),(-.58,-.42,3.11),(-.97,-.25,1.80),(1.25,-.23,2.96),(.17,-.38,1.14),(-.21,-.39,.45)]:flower(*p)
a.studio(focus=(0,0,2.16),location=(-8,-8,8.6),scale=5.45)
a.scene.render.resolution_x=1200;a.scene.render.resolution_y=1250
a.scene.view_settings.exposure=-.30
for ob in a.scene.objects:
    if ob.type=='LIGHT' and ob.name.startswith('Fill'):ob.data.energy=170
a.scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
result=a.save()
