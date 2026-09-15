"""Tiered grey outcrop with inset teal mineral bands and olive caps from rock.png."""
import sys,random,math
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
P=[('747970','mineral'),('666f68','mineral'),('85877a','mineral'),('566862','mineral'),
   ('747c51','mineral'),('858b60','mineral'),('697647','mineral'),
   ('3d6c67','mineral'),('497a74','mineral'),('315953','mineral')]
a=Asset('MossRock','rock.png',P);b=a.box;rng=random.Random(851)
caps=[(-.05,.02,.38,.15,1.30),(-.17,.12,.17,.36,1.32),(.16,.06,.20,.18,1.31),
   (-.49,-.16,.26,.20,.95),(-.51,-.40,.23,.16,.54),(-.72,-.22,.17,.20,.45),
   (.42,-.10,.24,.20,.84),(.49,.10,.20,.19,1.12),(.49,-.41,.23,.20,.49),
   (-.37,-.55,.25,.22,.15),(-.67,-.39,.17,.17,.26),(.68,.43,.20,.18,.50)]
# Explicit large columns reproduce the stepped silhouette and central mineral recess.
# x, y, width, depth, top height, material; front is -Y.
columns=[(-.50,-.38,.30,.28,.53,0),(-.21,-.40,.31,.29,.48,0),(.12,-.46,.25,.27,.31,1),(.42,-.40,.26,.29,.47,0),
 (-.68,-.16,.20,.27,.43,1),(-.46,-.10,.30,.29,.94,0),(-.17,-.10,.27,.30,1.29,0),(.12,-.12,.18,.20,1.24,7),
 (.37,-.10,.29,.31,.83,1),(.64,-.08,.23,.28,.56,3),(-.62,.15,.27,.25,.67,1),(-.35,.19,.30,.29,1.22,0),
 (-.06,.22,.27,.29,1.48,0),(.21,.22,.26,.29,1.39,3),(.49,.24,.27,.27,1.10,1),(.70,.23,.19,.24,.48,3),
 (-.45,.46,.27,.23,.78,1),(-.17,.48,.27,.25,1.32,1),(.10,.48,.29,.25,1.30,3),(.39,.48,.26,.24,1.03,3),
 (-.72,-.38,.17,.22,.24,1),(-.70,.41,.23,.22,.37,1),(.68,-.35,.22,.26,.37,3),(.66,.47,.23,.25,.48,3),
 (-.43,-.64,.27,.21,.14,1),(-.07,-.63,.21,.18,.12,0),(.34,-.64,.23,.21,.18,1),(.56,-.61,.18,.20,.10,3)]

def masonry(label,x,y,w,d,h,index,z0=0):
    nx=max(1,round(w/.12));ny=max(1,round(d/.12));nz=max(1,round(h/.12))
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                px=x-w/2+(ix+.5)*w/nx;py=y-d/2+(iy+.5)*d/ny;color=index
                if label=='Stone outcrop blocks' and index<4 and iz==nz-1:
                    for ci,(cx,cy,cw,cd,cz) in enumerate(caps):
                        if abs(h-cz)<.15 and abs(px-cx)<cw/2+w/nx*.3 and abs(py-cy)<cd/2+d/ny*.3:color=4+ci%3
                b(label,(px,py,z0+(iz+.5)*h/nz),(w/nx-.0015,d/ny-.0015,h/nz-.0015),color,.0025)
for x,y,w,d,h,index in columns:masonry('Stone outcrop blocks',x,y,w,d,h,index)
# Source's central teal cleft continues through a ledge and several lower exposures.
for x,y,w,d,h,z in [(.10,-.34,.25,.24,.37,.30),(.23,-.38,.24,.22,.33,.06),(.10,-.26,.18,.18,.15,.70),
                    (.59,-.22,.18,.15,.40,.09),(-.13,-.53,.10,.10,.11,.08)]:
    masonry('Teal mineral seam',x,y,w,d,h,rng.choice([7,7,8,9]),z)
# Moss is pigment on the outer stone blocks themselves, with no hovering slabs.
for ob in a.parts:
    ob.location.x*=1.08;ob.location.y*=1.08;ob.location.z*=.84
    for v in ob.data.vertices:v.co.x*=1.08;v.co.y*=1.08;v.co.z*=.84
a.studio(focus=(0,0,.60),location=(-8,-8,6.5),scale=2.48)
a.scene.render.resolution_x=1100;a.scene.render.resolution_y=1100
a.scene.view_settings.exposure=-.30
result=a.save()
