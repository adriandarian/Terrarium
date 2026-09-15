"""Tall mixed flowers beside the courtyard tower, separate from vegetables."""
from meshkit import Mesh
import math

def build():
    m=Mesh('SM_CourtyardFlowerBed_Reference',12932)
    m.box((0,0,7),(155,188,14),'594831',3)
    for x in (-80,80):m.box((x,0,14),(8,192,19),'wood',2)
    for y in (-97,97):m.box((0,y,14),(168,8,19),'wood_light',2)
    for row in range(3):
        for col in range(4):
            x=-53+row*53+m.rng.uniform(-6,6);y=-70+col*45+m.rng.uniform(-6,6)
            h=m.rng.uniform(43,76)
            m.beam((x,y,15),(x+3,y,h),3,'leaf_dark')
            for k in range(4):
                angle=k*math.tau/4+m.rng.random()
                dx,dy=math.cos(angle)*13,math.sin(angle)*13
                m.box((x+dx,y+dy,28+k*7),(10,25,7),m.rng.choice(['4c6d3d','637c41','748b48']),2,rot=(0,25,k*83))
            for dx,dy in [(-5,0),(5,0),(0,-5),(0,5)]:
                m.box((x+3+dx,y+dy,h),(9,9,7),m.rng.choice(['a54f27','bd632a','cc7d32']),2)
            m.box((x+3,y,h+3),(5,5,5),'d49e43',1)
    return m.save()
