"""Low golden earth tile with worn irregular stepping facets."""
from meshkit import Mesh
def build():
    m=Mesh('SM_PathTile',82)
    m.box((0,0,-8),(200,200,17),'path',4)
    for i in range(18):
        x=m.rng.uniform(-83,83);y=m.rng.uniform(-83,83)
        m.box((x,y,3),(m.rng.uniform(18,42),m.rng.uniform(17,36),5),m.rng.choice(['path','path_light']),6,rot=(0,0,m.rng.uniform(-32,32)))
    return m.save()
if __name__=='__main__':build()
