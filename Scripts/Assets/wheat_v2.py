"""Reference wheat revision: taller gold stems with individually modeled grain pairs."""
from meshkit import Mesh

def build():
    m=Mesh('SM_WheatPatch_v2',371);m.refinement_pass=2;m.revises='SM_WheatPatch'
    m.box((0,0,3),(278,248,6),'68703a',3)
    for col in range(9):
        x=-124+col*31
        m.box((x,0,7),(10,226,3),'5b6333',1)
        for row in range(8):
            y=-108+row*31+m.rng.uniform(-5,5);xx=x+m.rng.uniform(-6,6)
            h=m.rng.uniform(99,140);lean=m.rng.uniform(-8,9)
            m.beam((xx,y,7),(xx+lean*.35,y,h*.56),2.5,'a79643')
            m.beam((xx+lean*.35,y,h*.56),(xx+lean,y,h+24),2.3,'cbb35b')
            for side in [-1,1]:
                m.beam((xx+lean*.25,y,h*.40),(xx+side*13,y+3,h*.66),1.9,'ada04b')
                for tier in range(4):
                    z=h+tier*6
                    gx=xx+lean+side*(3.6-tier*.4)
                    gy=y+(tier%2-.5)*2
                    m.ellipsoid((gx,gy,z),(7.5-tier*.6,5.3,10),m.rng.choice(['d7bd62','cbb056','e0c874']),5,3,rot=(0,side*24,0))
                m.beam((xx+lean+side*2,y,h+18),(xx+lean+side*5,y,h+38),.8,'d6c06b')
    return m.save()
