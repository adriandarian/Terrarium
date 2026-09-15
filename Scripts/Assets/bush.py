"""Low clustered shrub; distinct from the tree canopy silhouette."""
from meshkit import Mesh
def build():
    m=Mesh('SM_Bush',65)
    for x,y,z,s in [(-36,0,30,1),(32,9,31,.95),(0,-24,36,1),(1,21,45,1),(-11,1,61,.8)]:
        m.ellipsoid((x,y,z),(65*s,59*s,62*s),m.rng.choice(['leaf','leaf_light','leaf_dark']),7,4)
    for x,y,z in [(-34,-11,48),(32,9,52),(0,12,74)]:m.box((x,y,z),(31,30,24),'leaf_light',7,rot=(3,5,9))
    return m.save()
if __name__=='__main__':build()
