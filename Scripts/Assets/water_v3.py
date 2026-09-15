"""Final water refinement: quieter broad teal facets and sparse pale glints."""
from meshkit import Mesh

def build():
    m=Mesh('SM_WaterTile_v3',385);m.refinement_pass=3;m.revises='SM_WaterTile_v2'
    m.box((0,0,-15),(302,302,29),'285f60',2,variation=.01)
    points={}
    for x in range(6):
        for y in range(6):
            points[x,y]=(-150+x*60+(m.rng.uniform(-14,14) if 0<x<5 else 0),-150+y*60+(m.rng.uniform(-14,14) if 0<y<5 else 0))
    for x in range(5):
        for y in range(5):
            p=[points[x,y],points[x+1,y],points[x+1,y+1],points[x,y+1]]
            for tri in [(0,1,2),(0,2,3)]:
                vs=[(*p[i],z) for z in [-1,1] for i in tri]
                m.solid(vs,[[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]],m.rng.choice(['326b67','346d69','306966','376e69']),variation=.01)
    for i in range(11):
        x,y=m.rng.uniform(-130,130),m.rng.uniform(-130,130)
        length=m.rng.uniform(10,26)
        m.box((x,y,2),(length,m.rng.uniform(2,4),1),m.rng.choice(['69998b','8dafa0','507e75']),.3,rot=(0,0,23),variation=.01)
        if i%4==0:m.box((x+8,y+6,2),(length*.45,2,1),'769d90',.3,rot=(0,0,23))
    return m.save()
