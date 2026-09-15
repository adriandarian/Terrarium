"""Reference bridge: broad worn planks, pegged rails and trestles reaching into water."""
from meshkit import Mesh

def build():
    m=Mesh('SM_PlankBridge_v2',351);m.refinement_pass=2;m.revises='SM_PlankBridge'
    for x in [-74,74]:m.box((x,0,28),(25,537,35),'4f3d26',4)
    # Eleven broad boards, rather than the first version's seventeen narrow ones.
    for i in range(11):
        y=-245+i*49;z=58+m.rng.uniform(-1.8,1.8)
        m.box((m.rng.uniform(-2,2),y,z),(192+m.rng.uniform(-3,3),44+m.rng.uniform(-1,1),20),m.rng.choice(['806036','89673a','927042','775a32']),4,rot=(0,m.rng.uniform(-.6,.6),m.rng.uniform(-1,1)))
        for x in [-72,72]:m.box((x,y,z+10.3),(4,4,1.5),'514730',.6)
        for j in range(3):
            xx=m.rng.uniform(-55,45);yy=y+m.rng.uniform(-15,15)
            m.box((xx,yy,z+10.3),(m.rng.uniform(22,62),m.rng.uniform(.6,1.3),.45),'6c512f',.12,rot=(0,0,m.rng.uniform(-2,2)))
        if i%3==0:m.box((m.rng.choice([-83,83]),y+8,z+10.5),(24,2,1),'4e4027',.3,rot=(0,0,8))
    for x in [-104,104]:
        for y in [-245,-82,82,245]:
            m.box((x,y,79),(21,22,139),'73522d',3)
            m.box((x,y,149),(26,28,13),'8b683c',3)
            m.box((x,y-6,135),(26,7,7),'ad824b',1)
        for y in [-164,0,164]:
            m.box((x,y,130),(14,168,17),'917044',3)
            m.box((x,y,87),(11,168,11),'654c2c',2)
    # Six piles and three braced trestles continue below the modeled waterline.
    # The scene's bridge origin is about 215 cm above the river; -240 cm is submerged.
    for y in [-194,0,194]:
        for x in [-76,76]:
            m.box((x,y,-92),(28,31,296),'5c472b',4)
            for z in [-157,-130]:m.box((x,y,z),(31,34,8),'526037',2)
        m.box((0,y,19),(193,31,23),'695030',3)
        m.beam((-74,y,-154),(74,y,16),12,'4f3e27')
        m.beam((74,y,-154),(-74,y,16),12,'59462a')
    for y in [-267,267]:m.box((0,y,18),(229,49,34),'6c7056',5)
    return m.save()
