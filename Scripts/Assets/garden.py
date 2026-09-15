"""A raised kitchen-garden bed with three rows of chunky leafy crops."""
from meshkit import Mesh
def build():
    m=Mesh('SM_GardenBed',91)
    m.box((0,0,8),(205,155,16),'soil',5)
    for x in [-103,103]:m.box((x,0,16),(13,173,23),'wood',3)
    for y in [-83,83]:m.box((0,y,16),(219,13,23),'wood_light',3)
    for row in range(3):
        y=-51+row*51
        m.box((0,y,18),(182,25,13),'soil',4)
        for col in range(5):
            x=-77+col*38
            m.ellipsoid((x,y,31),(24,24,24),'crop',6,3)
            for dx,dy in [(-9,0),(9,0),(0,-9),(0,9)]:
                m.ellipsoid((x+dx,y+dy,31),(16,16,13),m.rng.choice(['crop','crop_light']),5,3)
            if row==1:m.ellipsoid((x,y,43),(9,9,10),'fruit',5,3)
    return m.save()
if __name__=='__main__':build()
