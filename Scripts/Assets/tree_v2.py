"""Smaller branching trees with many individual chunky foliage sprays."""
from meshkit import Mesh
def build():
    m=Mesh('SM_OrchardTree_v2',261);m.refinement_pass=2;m.revises='SM_OrchardTree'
    m.beam((0,0,0),(8,3,238),24,'5a4627')
    for x,y,z in [(61,13,252),(-65,12,239),(12,-63,279),(9,53,294),(-33,-20,326)]:
        m.beam((5,0,105),(x,y,z),13,'59472a')
        for i in range(17):
            xx=x+m.rng.uniform(-45,45);yy=y+m.rng.uniform(-43,43);zz=z+m.rng.uniform(-27,39)
            m.box((xx,yy,zz),(m.rng.uniform(23,51),m.rng.uniform(23,50),m.rng.uniform(19,45)),m.rng.choice(['63722d','526629','7c8131','445925','74802f']),5,rot=(m.rng.uniform(-8,8),m.rng.uniform(-8,8),m.rng.uniform(-14,14)))
    for i in range(12):
        x=m.rng.uniform(-85,85);y=m.rng.uniform(-65,65);z=m.rng.uniform(175,278)
        m.ellipsoid((x,y,z),(10,10,11),'a5682e',6,3)
    for end in [(38,14,2),(-30,26,2),(12,-32,2)]:m.beam((0,0,25),end,14,'514729')
    return m.save()
