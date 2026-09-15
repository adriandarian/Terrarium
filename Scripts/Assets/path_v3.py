"""Final path pass: flush irregular earth mosaic without raised paving shadows."""
from meshkit import Mesh

def build():
    m=Mesh('SM_PathTile_v3',183);m.refinement_pass=3;m.revises='SM_PathTile_v2'
    points={}
    for x in range(5):
        for y in range(4):
            px=-101+x*50.5+(m.rng.uniform(-10,10) if 0<x<4 else 0)
            py=-93+y*62+(m.rng.uniform(-14,14) if 0<y<3 else m.rng.uniform(-9,9))
            points[x,y]=(px,py)
    for x in range(4):
        for y in range(3):
            p=[points[x,y],points[x+1,y],points[x+1,y+1],points[x,y+1]]
            vs=[(*q,z) for z in [-15,0] for q in p]
            m.solid(vs,[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],m.rng.choice(['b5a06c','baa875','bea974','b49b66','b7a16e']),variation=0)
    # Low earth fragments break the edge without elevated plank-like surfaces.
    for side in [-1,1]:
        for x in [-82,-37,31,79]:
            m.box((x,side*m.rng.uniform(94,102),-2),(m.rng.uniform(18,35),m.rng.uniform(14,24),3),'a99564',4,rot=(0,0,m.rng.uniform(-24,24)),variation=.01)
    return m.save()
