"""Second garden structure pass: low stone ring and open timber lifting frame."""
from meshkit import Mesh
import math

def build():
    m=Mesh('SM_GardenWell_v2',391);m.refinement_pass=2;m.revises='SM_GardenWell'
    for row in range(3):
        for i in range(8):
            a=i*math.tau/8+(row%2)*math.pi/8
            m.box((math.cos(a)*46,math.sin(a)*46,15+row*25),(39,28,27),m.rng.choice(['838575','737867','90917f']),5,rot=(0,0,math.degrees(a)+90))
    m.ellipsoid((0,0,40),(62,62,6),'2f463c',8,3)
    for x in [-43,43]:
        for y in [-26,26]:
            m.box((x,y,142),(12,14,208),'574b30',3)
        m.beam((x,-36,211),(x,0,269),10,'675c3c')
        m.beam((x,0,269),(x,36,211),10,'675c3c')
    m.box((0,0,269),(111,15,15),'6e6c49',3)
    for y in [-28,28]:m.box((0,y,206),(112,13,13),'5e5033',3)
    m.beam((-60,0,160),(60,0,160),10,'wood_dark')
    for x in range(-19,20,7):m.box((x,0,160),(6,27,27),'8a7950',3)
    m.beam((60,0,160),(60,0,138),5,'wood')
    m.beam((60,0,138),(77,0,138),5,'wood_light')
    m.beam((0,0,157),(0,0,72),2,'8d805b')
    for y in [-30,30]:m.beam((-43,y,90),(0,y,140),6,'wood_dark')
    # Warm hanging lamp on the front of the open frame.
    m.beam((0,-28,207),(0,-28,183),2,'metal')
    m.box((0,-28,162),(24,23,35),'c0a14d',2)
    for x in [-14,14]:
        for y in [-41,-15]:m.box((x,y,162),(4,4,39),'454b38',1)
    for z in [140,185]:m.box((0,-28,z),(35,34,6),'555c45',2)
    for x,y in [(-55,31),(29,57),(51,-39)]:m.box((x,y,7),(23,24,13),'687a38',4)
    return m.save()
