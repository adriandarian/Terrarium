"""Final cliff pass: larger warm stone courses with quiet faces and moss caps."""
from meshkit import Mesh

def build():
    m=Mesh('SM_CliffColumn_v3',341);m.refinement_pass=3;m.revises='SM_CliffColumn_v2'
    m.box((0,0,157),(89,89,314),'555844',3)
    for row in range(4):
        z=39+row*78
        m.box((m.rng.uniform(-2,2),m.rng.uniform(-2,2),z),(m.rng.uniform(97,104),m.rng.uniform(97,104),m.rng.uniform(76,80)),m.rng.choice(['77725a','80795e','6d6c51','888065']),7,rot=(0,m.rng.uniform(-1,1),m.rng.uniform(-2,2)),variation=.025)
        if row in [1,3]:
            m.box((-17,50,z+13),(31,1.3,16),'74725a',2,rot=(0,0,-2),variation=.01)
            m.box((50,16,z-17),(1.3,29,19),'707059',2,variation=.01)
    for x in [-26,26]:
        for y in [-26,26]:
            m.box((x,y,310),(56,56,27),m.rng.choice(['778039','848942','6d7935']),5,rot=(0,0,m.rng.uniform(-3,3)),variation=.02)
    for x,y,z in [(-49,23,287),(-49,-19,274),(49,12,285),(14,49,295),(-29,-49,288)]:
        m.box((x,y,z),(17,18,31),'657433',4)
    return m.save()
