"""Small weathered timber shed with broad blue-green shingle roof."""
from meshkit import Mesh

def build():
    m=Mesh('SM_Shed',23)
    for x in [-83,83]:
        for y in [-71,71]:m.box((x,y,16),(47,44,30),'stone',5)
    m.box((0,0,29),(191,159,18),'wood_dark',3)
    for i in range(8):
        x=-79+i*23
        m.box((x,70,109),(22,18,160),m.rng.choice(['wood','wood_light']),2)
        if i in [0,1,6,7]:m.box((x,-70,109),(22,18,160),'wood_light',2)
    for x in [-85,85]:
        for i in range(6):m.box((x,-57+i*23,110),(18,22,162),'wood_light',2)
        for y in [-74,74]:m.box((x,y,109),(23,24,180),'wood',3)
    m.gable((0,0,187),180,151,64,'wood')
    m.box((0,-73,105),(82,16,142),'wood_dark',2)
    for x in [-29,-9,11,31]:m.box((x,-84,103),(19,12,134),'wood_light',2)
    m.beam((-31,-94,55),(32,-94,146),10,'wood')
    for z in [53,145]:m.box((0,-92,z),(84,9,10),'wood',2)
    m.box((0,-112,15),(116,57,25),'stone_light',4)
    for side in [-1,1]:
        m.box((side*55,0,218),(145,206,17),'teal_dark',4,rot=(0,side*33,0))
        for row in range(3):
            x=side*(20+row*39)
            for col in range(5):
                m.box((x,-83+col*43,268-abs(x)*.66),(54,45,15),m.rng.choice(['teal','teal','teal_light']),3,rot=(0,side*33,0))
    for y in range(-88,100,38):m.box((0,y,274),(27,43,21),'teal_light',5)
    return m.save()

if __name__=='__main__':build()
