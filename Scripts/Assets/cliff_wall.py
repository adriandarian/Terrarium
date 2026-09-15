"""One repeatable 400 cm wide, 300 cm tall, moss-capped cliff section."""
from meshkit import Mesh

def build():
    m=Mesh('SM_CliffWall',41)
    for row in range(5):
        for col in range(5):
            x=-160+col*80
            z=30+row*59
            # A full-depth core maintains a closed plateau edge; front stones
            # have staggered strata and restrained silhouette irregularity.
            m.box((x,m.rng.uniform(-3,3),z),(79,m.rng.uniform(112,125),58),m.rng.choice(['stone','stone','stone_dark']),7,rot=(0,m.rng.uniform(-1,1),m.rng.uniform(-1,1)))
            if row in (1,3):m.box((x,-64,z+15),(71,5,5),'stone_dark',1)
    for col in range(8):
        x=-175+col*50
        m.box((x,-1,301),(52,126,22),m.rng.choice(['grass','moss','grass_light']),7)
        if col%2==0:m.box((x,-65,281),(29,9,26),'moss',3)
    return m.save()

if __name__=='__main__':build()
