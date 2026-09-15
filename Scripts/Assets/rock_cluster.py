"""Original softened, stratified river stones with a little moss."""
from meshkit import Mesh
def build():
    m=Mesh('SM_RockCluster',131)
    for x,y,z,s in [(-27,5,23,(76,61,55)),(28,6,17,(56,49,39)),(4,-29,11,(47,35,27))]:
        m.ellipsoid((x,y,z),s,'stone',7,4,rot=(7,-8,12))
        m.box((x,y-2,z+s[2]*.28),(s[0]*.56,s[1]*.55,7),'moss',2,rot=(0,-8,12))
    return m.save()
