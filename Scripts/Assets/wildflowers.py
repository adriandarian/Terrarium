"""A small original patch of cream and amber meadow flowers."""
from meshkit import Mesh
import math
def build():
    m=Mesh('SM_Wildflowers',132)
    for i in range(9):
        x=m.rng.uniform(-36,36);y=m.rng.uniform(-30,30);h=m.rng.uniform(23,47)
        m.beam((x,y,0),(x+2,y,h),2,'leaf_dark')
        m.ellipsoid((x-5,y,10),(18,8,7),'leaf',5,3,rot=(0,-25,i*41))
        for a in range(5):
            angle=a*math.tau/5
            m.ellipsoid((x+2+math.cos(angle)*4,y+math.sin(angle)*4,h),(8,7,5),'e6dbac' if i%3 else 'd8aa46',5,3)
        m.ellipsoid((x+2,y,h+2),(5,5,4),'wheat',5,3)
    return m.save()
