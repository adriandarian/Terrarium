"""Partly submerged angular river stones with wet, water-tinted upper faces."""
from meshkit import Mesh
def build():
    m=Mesh('SM_RiverStones_v1',7128)
    for x,y,w,d,top in [(-41,9,50,44,27),(4,-20,44,39,18),(34,16,38,33,12),(-20,43,31,29,7),(48,-23,27,21,4)]:
        m.box((x,y,(top-65)/2),(w,d,top+65),m.rng.choice(['456c64','4f7268','587b70']),5,rot=(0,0,m.rng.uniform(-17,17)))
        m.box((x-3,y+2,top+.25),(w*.54,d*.65,.8),m.rng.choice(['61877a','628b7f','52786e']),.3,rot=(0,0,m.rng.uniform(-12,12)))
    return m.save()
