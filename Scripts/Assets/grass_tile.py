"""Repeatable 200 cm ground tile with warm earth sides and mossy turf facets."""
from meshkit import Mesh
def build():
    m=Mesh('SM_GrassTile',81)
    m.box((0,0,-13),(200,200,26),'soil',5)
    for x in [-75,-25,25,75]:
        for y in [-75,-25,25,75]:
            m.box((x,y,2+m.rng.uniform(-1,1)),(50,50,12),m.rng.choice(['grass','grass','moss','grass_light']),4)
    for x,y in [(-63,55),(56,-49),(22,60)]:m.box((x,y,9),(25,21,5),'moss',2)
    return m.save()
if __name__=='__main__':build()
