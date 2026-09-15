"""Repeatable two-rail fence infill with a light diagonal brace."""
from meshkit import Mesh
def build():
    m=Mesh('SM_FenceRails',32)
    m.box((0,0,48),(170,12,15),'wood_light',2,rot=(0,0,1))
    m.box((0,0,98),(170,13,16),'wood_light',2,rot=(0,0,-1))
    m.beam((-72,8,45),(69,8,102),9,'wood')
    return m.save()
if __name__=='__main__':build()
