"""Irregular overlapping moss facets over a solid terrain core; no paving grid."""
from meshkit import Mesh
def build():
    m=Mesh('SM_MeadowTile_v2',282);m.refinement_pass=2;m.revises='SM_GrassTile'
    m.box((0,0,-160),(203,203,320),'555b3e',2)
    m.box((0,0,-2),(206,206,15),'626d33',3)
    for i in range(72):
        x=m.rng.uniform(-98,98);y=m.rng.uniform(-98,98)
        m.box((x,y,m.rng.uniform(4,7)),(m.rng.uniform(14,47),m.rng.uniform(11,39),m.rng.uniform(3,9)),m.rng.choice(['667133','697638','727d3c','5a672e','77803b']),2,rot=(0,0,m.rng.uniform(-22,22)))
    for i in range(10):
        x=m.rng.uniform(-91,91);y=m.rng.uniform(-91,91)
        m.box((x,y,11),(m.rng.uniform(7,14),m.rng.uniform(7,13),m.rng.uniform(9,20)),m.rng.choice(['6c7935','4b5f29']),2,rot=(0,0,m.rng.uniform(-25,25)))
    return m.save()
