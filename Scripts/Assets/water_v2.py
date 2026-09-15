"""Still water made from a continuous irregular triangulated teal mosaic."""
from meshkit import Mesh
def build():
    m=Mesh('SM_WaterTile_v2',285);m.refinement_pass=2;m.revises='SM_WaterTile'
    m.box((0,0,-15),(302,302,29),'245959',2)
    points={}
    for x in range(13):
        for y in range(13):points[x,y]=(-150+x*25+(m.rng.uniform(-7,7) if 0<x<12 else 0),-150+y*25+(m.rng.uniform(-7,7) if 0<y<12 else 0))
    for x in range(12):
        for y in range(12):
            p=[points[x,y],points[x+1,y],points[x+1,y+1],points[x,y+1]]
            for tri in [(0,1,2),(0,2,3)]:
                vs=[(*p[i],z) for z in [-1,1] for i in tri]
                m.solid(vs,[[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]],m.rng.choice(['2c6463','2c6866','306d6b','285e60','347170']),variation=.035)
    for i in range(17):m.box((m.rng.uniform(-135,135),m.rng.uniform(-135,135),2),(m.rng.uniform(4,14),m.rng.uniform(2,5),1),'55887f',.2,rot=(0,0,23))
    return m.save()
