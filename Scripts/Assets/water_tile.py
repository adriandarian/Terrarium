"""Opaque painterly teal water module: color facets and small raised ripples."""
from meshkit import Mesh
def build():
    m=Mesh('SM_WaterTile',83)
    m.box((0,0,-12),(300,300,24),'water_dark',2)
    for x in [-120,-60,0,60,120]:
        for y in [-120,-60,0,60,120]:
            m.box((x,y,1),(60.2,60.2,5),m.rng.choice(['water','water','water_light','water_dark']),.7,variation=.025)
    for i in range(10):
        x=m.rng.uniform(-131,131);y=m.rng.uniform(-131,131)
        m.box((x,y,4),(m.rng.uniform(12,34),m.rng.uniform(3,7),1),'water_light',.3,rot=(0,0,-20))
    return m.save()
if __name__=='__main__':build()
