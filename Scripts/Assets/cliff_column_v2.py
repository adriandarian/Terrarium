"""Reference-scale irregular stone column, layered seams, projecting moss cap."""
from meshkit import Mesh
def build():
    m=Mesh('SM_CliffColumn_v2',241);m.refinement_pass=2;m.revises='SM_CliffWall'
    m.box((0,0,157),(91,91,314),'515641',3)
    for row in range(7):
        for x in [-25,25]:
            for y in [-25,25]:
                m.box((x+m.rng.uniform(-3,3),y+m.rng.uniform(-3,3),22+row*43),(m.rng.uniform(46,54),m.rng.uniform(46,55),m.rng.uniform(39,45)),m.rng.choice(['76745a','66694f','7d7a5e','5d634b']),6,rot=(0,m.rng.uniform(-2,2),m.rng.uniform(-3,3)))
        for side in [-1,1]:
            if row%2==0:m.box((0,side*50,29+row*43),(78,4,5),'4c533c',1)
    for x in [-27,27]:
        for y in [-27,27]:m.box((x,y,310),(57,57,27),m.rng.choice(['687331','78803b','59682e']),5,rot=(0,0,m.rng.uniform(-3,3)))
    for i in range(18):
        x=m.rng.choice([-48,48]);y=m.rng.uniform(-47,47);z=m.rng.uniform(225,308)
        m.box((x,y,z),(m.rng.uniform(6,17),m.rng.uniform(11,24),m.rng.uniform(10,29)),m.rng.choice(['52652c','657432','7a813b']),3)
    return m.save()
