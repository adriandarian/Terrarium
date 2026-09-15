"""A low branching shrub of individually modeled angular leaves and small berries."""
from meshkit import Mesh
def build():
    m=Mesh('SM_Bush_v2',262);m.refinement_pass=2;m.revises='SM_Bush'
    for x,y,h in [(-33,3,58),(25,17,64),(0,-23,75),(4,25,85)]:
        m.beam((0,0,0),(x,y,h),7,'534729')
        for i in range(10):m.box((x+m.rng.uniform(-21,21),y+m.rng.uniform(-23,23),h+m.rng.uniform(-20,14)),(m.rng.uniform(13,30),m.rng.uniform(14,28),m.rng.uniform(10,27)),m.rng.choice(['4d6227','69752b','788032','3f5626']),4,rot=(0,m.rng.uniform(-9,9),m.rng.uniform(-20,20)))
    for x,y,z in [(-31,-19,48),(20,-29,55),(41,6,43)]:m.ellipsoid((x,y,z),(9,9,10),'a5672d',5,3)
    return m.save()
