"""Final ground refinement: broad quiet moss plates with sparse tufts."""
from meshkit import Mesh

def build():
    m=Mesh('SM_MeadowTile_v3',382);m.refinement_pass=3;m.revises='SM_MeadowTile_v2'
    m.box((0,0,-160),(203,203,320),'555b3e',2)
    m.box((0,0,-2),(206,206,15),'737a38',3,variation=.015)
    for row in range(3):
        for col in range(3):
            x=-68+col*68+m.rng.uniform(-8,8);y=-68+row*68+m.rng.uniform(-8,8)
            m.box((x,y,m.rng.uniform(4,5)),(m.rng.uniform(54,85),m.rng.uniform(50,82),m.rng.uniform(3,5)),m.rng.choice(['757e3b','7b813b','6b7534','828842','707b38']),2,rot=(0,0,m.rng.uniform(-8,8)),variation=.015)
    for x,y in [(-63,19),(67,-56)]:
        for d in [-3,4]:
            m.box((x+d,y,11),(5,4,m.rng.uniform(10,15)),'778341',1,rot=(0,0,13))
    return m.save()
