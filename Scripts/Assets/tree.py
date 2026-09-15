"""A branching orchard tree with asymmetric faceted olive foliage."""
from meshkit import Mesh
def build():
    m=Mesh('SM_OrchardTree',61)
    m.beam((0,0,3),(8,3,239),33,'wood')
    for end in [(90,12,324),(-78,17,314),(9,-85,341),(14,54,381)]:
        m.beam((6,2,175),end,19,'wood')
    for x,y,z,s in [(-73,5,300,1),(72,8,314,1),(4,-72,342,1),(9,63,352,.9),(-49,-27,395,1.05),(50,29,405,1),(0,8,458,.9)]:
        m.ellipsoid((x,y,z),(157*s,141*s,132*s),m.rng.choice(['leaf','leaf','leaf_light']),7,4,rot=(0,0,m.rng.uniform(0,40)))
    for i in range(17):
        x=m.rng.uniform(-114,113);y=m.rng.uniform(-93,92);z=m.rng.uniform(320,438)
        m.box((x,y,z),(m.rng.uniform(35,57),m.rng.uniform(33,59),m.rng.uniform(31,51)),m.rng.choice(['leaf','leaf_light','leaf_dark']),8,rot=(m.rng.uniform(-6,6),m.rng.uniform(-6,6),m.rng.uniform(-12,12)))
    for end in [(48,22,3),(-45,21,3),(6,-43,3)]:m.beam((1,0,36),end,17,'wood_dark')
    for x,y in [(-72,0),(53,67),(34,-83)]:m.ellipsoid((x,y,286),(12,12,14),'fruit',6,3)
    return m.save()
if __name__=='__main__':build()
