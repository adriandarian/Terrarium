"""Low rustic two-rail fence with irregular posts and restrained weathering."""
from meshkit import Mesh

def post():
    m=Mesh('SM_FencePost_Reference',1581)
    m.box((0,0,7),(24,23,14),'686b4d',3)
    m.box((0,0,57),(15,17,108),'6b4e2c',2.4,rot=(0,1.5,-1.2))
    m.box((1,0,112),(18,20,10),'987144',2.8,rot=(0,-6,3))
    for z in (42,82):
        for dz in (-3,1,5):m.box((0,0,z+dz),(17,20,2),'8c774b',.5)
    for x in (-4,3):m.box((x,-9,64),(1.5,1,54),'ad8750',.3)
    m.box((5,5,14),(16,13,9),'647335',2)
    return m.save()

def rails():
    m=Mesh('SM_FenceRails_Reference',1582)
    m.beam((-85,0,39),(0,-1,41),8,'957043',depth=10)
    m.beam((0,-1,41),(85,0,38),8,'8a6639',depth=10)
    m.beam((-85,0,83),(-8,1,80),9,'9c7543',depth=11)
    m.beam((-8,1,80),(85,0,84),9,'886237',depth=11)
    for x in (-75,75):
        for z in (40,82):m.box((x,-5,z),(3,2,3),'47412d',.5)
    for x,z in [(-49,82),(36,39)]:m.box((x,-5,z),(28,1.3,1.5),'b18d56',.3)
    return m.save()
