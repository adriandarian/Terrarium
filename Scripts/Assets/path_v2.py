"""Second path pass: broad worn earth facets and an irregular low verge."""
from meshkit import Mesh

def build():
    m=Mesh('SM_PathTile_v2',182);m.refinement_pass=2;m.revises='SM_PathTile'
    # Tile repeats along X. Its irregular Y edges soften the ribbon silhouette.
    verts=[(-101,-85,-15),(101,-85,-15),(101,85,-15),(-101,85,-15),(-101,-88,0),(101,-94,0),(101,88,0),(-101,96,0)]
    m.solid(verts,[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],'b6a06e',variation=.015)
    for row in range(3):
        for col in range(4):
            x=-75+col*50+m.rng.uniform(-7,7);y=-59+row*59+m.rng.uniform(-8,8)
            m.box((x,y,1),(m.rng.uniform(41,62),m.rng.uniform(43,67),3),m.rng.choice(['b5a06c','baa875','c0ab76','b49b66']),5,rot=(0,0,m.rng.uniform(-12,12)),variation=.015)
    for side in [-1,1]:
        for x in [-77,-26,27,78]:
            m.box((x,side*m.rng.uniform(91,100),-2),(m.rng.uniform(27,44),m.rng.uniform(16,30),4),'aa9563',5,rot=(0,0,m.rng.uniform(-18,18)))
    return m.save()
