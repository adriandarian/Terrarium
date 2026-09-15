"""Measured building and crop anchors, with the garden well and lanterns."""
import math
import reference as ref
from placement import place,place_xyz,rng

def fence(points,h):
    for a,b in zip(points,points[1:]):
        va,vb=ref.world(*a,h),ref.world(*b,h)
        length=math.hypot(vb[0]-va[0],vb[1]-va[1]);n=max(1,round(length/170))
        yaw=math.degrees(math.atan2(vb[1]-va[1],vb[0]-va[0]))
        for i in range(n):
            for t in [i/n,(i+.5)/n]:
                xyz=(va[0]+(vb[0]-va[0])*t,va[1]+(vb[1]-va[1])*t,h+8)
                if t==i/n:place_xyz('FencePost',xyz,.78,yaw,'Fences')
                else:place_xyz('FenceRails',xyz,(length/n/170,.85,.78),yaw,'Fences')
        place_xyz('FencePost',(vb[0],vb[1],h+8),.78,yaw,'Fences')

def build():
    place('Cottage_v4',260,308,568,1.08,90,'Buildings',False)
    place('Shed_v2',132,351,568,.87,90,'Buildings',False)
    place('GardenWell_v2',351,352,568,1.08,90,'Garden',False)
    place('LanternPost',273,369,568,1.25,0,'Garden',False)
    for px,py in [(304,376),(365,354)]:place('GardenBed_v2',px,py,570,1.03,0,'Garden',False)
    fence([(265,353),(328,319),(411,339),(352,383)],560)
    fence([(146,310),(165,300),(188,287),(211,291)],560)
    # Crop placement is clipped to the traced parallelogram, without a large
    # enclosing fence absent from the reference.
    corners=[ref.world(*p,880) for p in ref.WHEAT]
    x0=min(p[0] for p in corners);x1=max(p[0] for p in corners)
    y0=min(p[1] for p in corners);y1=max(p[1] for p in corners)
    for x in range(int(x0),int(x1)+1,110):
        for y in range(int(y0),int(y1)+1,110):
            px,py=ref.pixel(x,y,880)
            if ref.inside((px,py),ref.WHEAT):place_xyz('WheatPatch_v2',(x,y,890),(.48,.48,.8),0,'Wheat')
