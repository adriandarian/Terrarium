"""The cottage, teal shed, fenced kitchen garden, and upper wheat terrace."""
from placement import place,segment
import math

def fence(points,z):
    for a,b in zip(points,points[1:]):
        length=math.hypot(b[0]-a[0],b[1]-a[1]);n=max(1,round(length/180))
        for i in range(n):
            p=(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n)
            q=(a[0]+(b[0]-a[0])*(i+1)/n,a[1]+(b[1]-a[1])*(i+1)/n)
            place('FencePost',*p,z,1,0,'Garden/Fence')
            segment('FenceRails',p,q,z,1,'Garden/Fence',170)
        place('FencePost',*b,z,1,0,'Garden/Fence')

def build():
    place('Cottage',-20,290,380,1.14,90,'Buildings')
    place('Shed',-540,-10,380,1.03,90,'Buildings')
    for u in [310,550]:
        for v in [-10,200]:place('GardenBed',u,v,382,.98,-135,'Garden/Crops')
    fence([(190,-145),(700,-145),(760,390),(200,430)],380)
    fence([(-710,200),(-650,430),(-380,610)],380)
    for u in [70,360,650,940]:
        for v in [1040,1295,1550]:place('WheatPatch',u,v,696,1,-135,'WheatField')
    fence([(-80,900),(1100,900),(1100,1740),(-80,1740)],696)
