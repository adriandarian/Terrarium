"""Reference-traced paths and a diagonal bridge/stair connection."""
import math
import reference as ref
from placement import place,place_xyz,rng
def build():
    for h,path,width in ref.PATHS:
        for a,b in zip(path,path[1:]):
            va,vb=ref.world(*a,h),ref.world(*b,h)
            length=math.hypot(vb[0]-va[0],vb[1]-va[1]);steps=max(1,math.ceil(length/90))
            yaw=math.degrees(math.atan2(vb[1]-va[1],vb[0]-va[0]))
            for i in range(steps):
                t=(i+.5)/steps
                xyz=(va[0]+(vb[0]-va[0])*t,va[1]+(vb[1]-va[1])*t,h+11)
                place_xyz('PathTile_v3',xyz,((length/steps+7)/200,width/200,.65),yaw,'Paths')
    # Anchor the last tread to the traced top step; stairs descend toward -Y.
    yaw=2;r=math.radians(yaw);sx=1;sy=.75;sz=280/249
    top=ref.world(157,429,560)
    offset=(-math.sin(r)*147*sy,math.cos(r)*147*sy,249*sz)
    place_xyz('StoneStairs_v2',tuple(top[i]-offset[i] for i in range(3)),(sx,sy,sz),yaw,'Stairs',False)
    deck=ref.world(306,579,280)
    place_xyz('PlankBridge_v2',(deck[0],deck[1],deck[2]-58),(.9,1.4,1),-4,'Bridge',False)
