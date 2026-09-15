"""One reusable dense wheat patch; solid stalks and modeled grain heads."""
from meshkit import Mesh
def build():
    m=Mesh('SM_WheatPatch',71)
    m.box((0,0,5),(278,248,10),'soil',3)
    for row in range(10):
        for col in range(11):
            x=-125+col*25+m.rng.uniform(-5,5);y=-110+row*24+m.rng.uniform(-4,4)
            h=m.rng.uniform(65,96);lean=m.rng.uniform(3,9)
            m.beam((x,y,9),(x,y,h*.57),2.7,'stalk')
            m.beam((x,y,h*.57),(x+lean,y,h),2.7,'wheat')
            m.ellipsoid((x+lean,y,h+6),(10,8,26),m.rng.choice(['wheat','wheat_light']),5,4,rot=(0,-12,0))
            if (row+col)%3==0:m.beam((x,y,36),(x-8,y+4,54),2.5,'stalk')
    return m.save()
if __name__=='__main__':build()
