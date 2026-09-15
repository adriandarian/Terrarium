"""An original still clump of olive reeds for the shallow river margin."""
from meshkit import Mesh
def build():
    m=Mesh('SM_Reeds',133)
    for i in range(15):
        x=m.rng.uniform(-31,31);y=m.rng.uniform(-28,28);h=m.rng.uniform(42,89)
        m.beam((x,y,-10),(x+5,y,h),2.5,'stalk')
        m.ellipsoid((x+5,y,h),(7,7,19),'wheat',5,3)
        m.beam((x,y,2),(x-11,y+4,h*.7),3,'leaf')
    return m.save()
