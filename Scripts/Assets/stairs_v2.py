"""Second stair pass: irregular worn treads and moss in the edge joints."""
from meshkit import Mesh

def build():
    m=Mesh('SM_StoneStairs_v2',144)
    m.refinement_pass=2;m.revises='SM_StoneStairs'
    for i in range(8):
        y=-147+i*42;h=30*(i+1)
        m.box((0,y,h/2),(200,43,h),'stone_dark',5)
        for j,x in enumerate([-67,0,67]):
            m.box((x,y+m.rng.uniform(-1,1),h+3),(66,45,12),m.rng.choice(['8d8268','a49a7b','999374']),5,rot=(0,0,m.rng.uniform(-.8,.8)))
            m.box((x+m.rng.uniform(-18,18),y-22,h+1),(m.rng.uniform(8,15),2,3),'695f4b',.6)
        for x in [-111,111]:
            # Separate masonry courses break up the original tall side blocks.
            for k in range(i+1):
                m.box((x,y,k*30+20),(24,41,29),m.rng.choice(['stone','stone_dark']),4)
            m.box((x,y,h+19),(28,42,12),'7d8350',4)
            if i%2==0:
                m.box((x*.86,y+12,h+11),(19,11,3),'657132',1)
                for d in [-5,3]:m.beam((x,y+d,h+23),(x-4,y+d,h+34),1.5,'819045')
    return m.save()
