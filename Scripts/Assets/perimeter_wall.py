"""Short 200 cm wall segment with oversailing weathered coping."""
from meshkit import Mesh
def build():
    m=Mesh('SM_PerimeterWall',96)
    for row in range(3):
        for col in range(4):
            m.box((-75+col*50,0,17+row*33),(49,51,32),m.rng.choice(['stone','stone_light','stone_dark']),5)
    for col in range(4):
        m.box((-75+col*50,0,105),(53,63,18),'stone_light',5)
        if col%2==0:m.box((-73+col*50,3,116),(37,41,6),'moss',3)
    return m.save()
if __name__=='__main__':build()
