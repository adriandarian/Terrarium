"""Original small stone garden well with a timber canopy and hanging warm lantern."""
from meshkit import Mesh
import math
def build():
    m=Mesh('SM_GardenWell',291)
    for row in range(4):
        for i in range(8):
            a=i*math.tau/8+(row%2)*math.pi/8
            m.box((math.cos(a)*52,math.sin(a)*52,16+row*28),(43,35,29),m.rng.choice(['71735a','858166','626951']),5,rot=(0,0,math.degrees(a)+90))
    m.ellipsoid((0,0,87),(75,75,8),'2f4c3e',8,3)
    for x in [-57,57]:m.box((x,0,170),(15,21,192),'514129',3)
    m.box((0,0,253),(139,23,15),'6e5732',3)
    for side in [-1,1]:
        for i in range(4):m.box((side*38,-49+i*34,260),(96,34,14),'514c35',3,rot=(0,side*29,0))
    m.box((0,0,285),(21,143,19),'726d50',4)
    m.beam((0,0,249),(0,0,204),3,'metal')
    m.box((0,0,186),(31,29,43),'c3a351',3)
    for x in [-18,18]:
        for y in [-17,17]:m.box((x,y,186),(5,5,50),'454638',1)
    for z in [160,212]:m.box((0,0,z),(43,41,7),'53533f',2)
    for x,y in [(-64,24),(32,65),(60,-40)]:m.box((x,y,9),(25,29,17),'657533',4)
    return m.save()
