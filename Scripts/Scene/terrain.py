"""Stepped mossy land and a continuous teal river, composed from reviewed modules."""
from placement import place
import math

def river(v_u):return -1210+.10*(v_u-520)+65*math.sin((v_u-520)/540)

def height(u,v):
    u=round(u/200)*200;v=round(v/200)*200
    if abs(v-river(u))<240:return None
    if v<river(u):return 60
    if v<-300:
        if -700<=u<=900 and v>=river(u)+240:return 60
        if v>-650 and abs(u)>850:return 60
        return None
    if v>=800 and u>=-200:return 684
    if u<-1100 or u>1100:return 60 if v<650 else 372
    return 372

def build():
    cells=[]
    for u in range(-2400,2401,200):
        for v in range(-3200,3201,200):
            h=height(u,v)
            if h is None:continue
            cells.append((u,v,h))
            # A full-depth stone module fills each column. The grass overlaps its
            # cap by a few centimetres so no internal surface is exposed.
            for bottom in range(int(h)-312,-253,-312):
                place('CliffWall',u,v,bottom,(.505,1.62,1),-135,'Terrain/Strata')
            place('GrassTile',u,v,h,(1.012,1.012,1),-135,'Terrain/Turf')
    for u in range(-2700,2701,300):
        for v in range(-2000,-299,300):
            place('WaterTile',u,v,5,(1.004,1.004,1),-135,'River')
    return cells
