"""Original stepped mossy stone outcrop for broken shallow river banks."""
from meshkit import Mesh

def build():
    m=Mesh('SM_ShoreOutcrop',613)
    for x,y,rows in [(-44,18,3),(31,26,2),(-6,-38,1),(66,-25,1)]:
        for row in range(rows):
            m.box((x+m.rng.uniform(-3,3),y+m.rng.uniform(-3,3),17+row*36),(m.rng.uniform(61,74),m.rng.uniform(56,72),35),m.rng.choice(['6b6d53','747354','77785a','5b624c']),5,rot=(0,0,m.rng.uniform(-5,5)))
        z=rows*36
        m.box((x,y,z),(70,67,10),m.rng.choice(['75823b','879043','657632']),4,rot=(0,0,m.rng.uniform(-4,4)))
        for dx,dy in [(-16,8),(19,-13)]:m.box((x+dx,y+dy,z+6),(25,27,3),'879044',2,rot=(0,0,8))
    for x,y,z in [(-69,5,83),(-49,49,62),(52,47,46)]:m.box((x,y,z),(13,18,23),'627333',3)
    return m.save()
