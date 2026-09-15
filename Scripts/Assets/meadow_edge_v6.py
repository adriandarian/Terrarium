"""Recessed edge soil lets fractured cliff stones own the exposed silhouette."""
from meshkit import Mesh
def build():
    m=Mesh('SM_MeadowTile_Edge_v6',706)
    m.refinement_pass=6;m.revises='SM_MeadowTile_v5'
    m.box((0,0,-155),(165,165,314),'555b3e',2)
    m.box((0,0,2),(202,202,8),'737745',1,variation=.008)
    return m.save()
