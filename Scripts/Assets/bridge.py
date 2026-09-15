"""Broad plank bridge with timber beams, low rails, and pegged joinery."""
from meshkit import Mesh
def build():
    m=Mesh('SM_PlankBridge',51)
    for x in [-71,71]:m.box((x,0,30),(22,529,34),'wood_dark',4)
    for i in range(17):
        y=-248+i*31
        m.box((m.rng.uniform(-2,2),y,58+m.rng.uniform(-2,2)),(191,29,19),m.rng.choice(['wood','wood_light','wood_light']),3,rot=(0,m.rng.uniform(-1,1),m.rng.uniform(-1.2,1.2)))
        for x in [-69,69]:m.box((x,y,70),(6,6,3),'wood_dark',1)
    for x in [-104,104]:
        for y in [-235,0,235]:
            m.box((x,y,70),(20,22,142),'wood',3)
            m.box((x,y,144),(27,28,12),'wood_light',3)
        for y in [-117,117]:
            m.box((x,y,129),(14,251,17),'wood_light',3)
            m.box((x,y,85),(11,249,12),'wood',2)
    for y in [-263,263]:m.box((0,y,19),(232,54,36),'stone_dark',5)
    return m.save()
if __name__=='__main__':build()
