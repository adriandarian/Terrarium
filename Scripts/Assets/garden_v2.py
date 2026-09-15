"""Second garden pass: fuller cabbage leaves, red produce and worn edging."""
from meshkit import Mesh
import math

def build():
    m=Mesh('SM_GardenBed_v2',192)
    m.refinement_pass=2;m.revises='SM_GardenBed'
    m.box((0,0,8),(205,155,16),'soil',5)
    for x in [-103,103]:
        m.box((x,0,16),(13,173,23),'wood',3)
        for y in [-76,0,76]:m.box((x,y,22),(18,15,32),'wood_dark',3)
    for y in [-83,83]:
        m.box((0,y,16),(219,13,23),'wood_light',3)
        for x in [-70,0,70]:m.box((x,y-7,18),(43,1.5,2),'wood_dark',.2)
    for row in range(3):
        y=-51+row*51
        m.box((0,y,18),(182,31,13),'574b2e',4)
        for col in range(5):
            x=-77+col*38
            m.ellipsoid((x,y,31),(25,25,25),'536932',7,3)
            for k in range(7):
                a=k*math.tau/7+m.rng.uniform(-.2,.2)
                dx,dy=math.cos(a)*11,math.sin(a)*11
                m.ellipsoid((x+dx,y+dy,32+m.rng.uniform(-3,3)),(23,19,11),m.rng.choice(['526c32','708141','81934b']),5,3)
                m.beam((x,y,34),(x+dx*1.6,y+dy*1.6,34),1.1,'87954b')
            if (col+row)%2==0:
                for dx,dy in [(-7,-5),(6,0),(0,7)]:
                    m.ellipsoid((x+dx,y+dy,43),(11,11,12),m.rng.choice(['b64a29','c36832']),6,3)
                    m.box((x+dx,y+dy,49),(5,5,3),'leaf_dark',.7)
            else:m.ellipsoid((x,y,44),(19,20,19),'80944b',6,3)
    for _ in range(26):
        x,y=m.rng.uniform(-96,96),m.rng.uniform(-74,74)
        m.ellipsoid((x,y,18),(4,5,3),'8d8268',5,2)
    return m.save()
