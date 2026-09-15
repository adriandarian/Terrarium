"""Compact reference cottage with individually jointed clay roof, small foundation courses and timber joints."""
from meshkit import Mesh, sub, dot, cross
from cottage_roof_v6 import add_main_roof, add_projecting_gable_roof

def build_mesh():
    m=Mesh('SM_Cottage_v6',217);m.refinement_pass=6;m.revises='SM_Cottage_v5'
    # Two smaller staggered courses retain the original footprint and footing.
    stone=('77765e','858067','6d7056','8c866c')
    for row in range(2):
        for y in [-180,180]:
            for col in range(8):
                x=-139+col*39+(4 if row else 0)
                m.box((x,y,12+row*24),(37,43,23),m.rng.choice(stone),3.2,
                      rot=(0,0,m.rng.uniform(-1.8,1.8)),variation=.02)
        for x in [-154,154]:
            for col in range(9):
                y=-153+col*38+(3 if row else 0)
                m.box((x,y,12+row*24),(39,36,23),m.rng.choice(stone),3.2,
                      rot=(0,0,m.rng.uniform(-1.8,1.8)),variation=.02)
    m.box((0,0,177),(278,346,268),'c9c5a0',7)
    m.gable((0,0,307),278,346,139,'b7b594')
    for y in [-179,179]:
        for x in [-138,138]:
            m.box((x,y,181),(22,24,278),'4e4229',3)
            for k in range(5):m.box((x-5,y-13,87+k*42),(3,2,24),'68563b',.7)
        for z in [60,306]:m.box((0,y,z),(294,23,21),'54432a',3)
        m.beam((-147,y,309),(0,y,454),18,'493d28')
        m.beam((0,y,454),(147,y,309),18,'493d28')
        m.box((0,y,372),(45,13,66),'2f3023',2)
        for xx in [-27,27]:m.box((xx,y-8,371),(9,16,74),'5e4c2f',2)
        m.box((0,y-8,411),(63,18,9),'635030',2)
    for x in [-145,145]:
        for y in [-170,0,170]:m.box((x,y,177),(22,20,267),'51432a',3)
        for z in [61,306]:m.box((x,0,z),(22,360,20),'52472d',3)
        for y in [-88,89]:
            m.box((x*1.04,y,195),(13,69,110),'294f45',3)
            for yy in [y-42,y+42]:m.box((x*1.12,yy,195),(20,12,126),'726043',2)
            for zz in [134,258]:m.box((x*1.12,y,zz),(24,96,13),'8b7753',3)
            m.box((x*1.14,y,194),(15,8,111),'6a5b3e',2)
            m.box((x*1.15,y,129),(32,106,13),'645337',3)
            for yy in [y-26,y+22]:m.box((x*1.08,yy,195),(6,5,89),'477363',1)
    # The reference gable has a single centered doorway, and timber steps.
    m.box((0,-182,148),(93,16,177),'29291e',3)
    for x in [-34,-17,0,17,34]:
        m.box((x,-194,147),(16,17,174),'685332',2)
        m.box((x+4,-204,150),(2,2,133),'493c29',.6)
    for x in [-57,57]:m.box((x,-199,150),(20,25,194),'5b482c',4)
    m.box((0,-201,250),(141,34,26),'79613b',4)
    for z in [111,204]:m.box((0,-207,z),(89,5,8),'453925',1)
    m.ellipsoid((27,-213,157),(8,8,10),'metal',6,3)
    for i in range(3):
        z=31-i*11
        m.box((0,-224-i*26,z),(135+i*9,44,19),'7d6239',3)
        for x in [-53,53]:m.box((x,-224-i*26,z-10),(19,32,22),'4f422b',2)
    # Gap 14 owns the fine roof recipe; no original coarse tiles remain.
    add_main_roof(m)
    # Front-left chimney, with a visibly open soot-dark throat.
    for row in range(6):
        z=408+row*27
        for x in [66,94]:m.box((x,-88,z),(27,52,26),m.rng.choice(['85836a','99947a','74765d']),4)
    m.box((80,-88,566),(34,31,7),'292b22',1)
    for x in [55,105]:m.box((x,-88,578),(15,69,18),'a09b7f',3)
    for y in [-114,-62]:m.box((80,y,578),(40,15,18),'a09b7f',3)
    for i in range(28):
        x=m.rng.choice([-1,1])*m.rng.uniform(128,170);y=m.rng.uniform(-190,190)
        m.box((x,y,m.rng.uniform(4,16)),(m.rng.uniform(12,31),m.rng.uniform(14,34),m.rng.uniform(6,17)),m.rng.choice(['5b6830','778037','495a2a']),3,rot=(0,0,m.rng.uniform(-15,15)))
    for side in [-1,1]:
        for i in range(9):
            m.box((side*147,-148+i*37,56),(17,35,24),m.rng.choice(['5c654b','778064','878468']),4)
    # Small side-facing projecting gable, visible on the camera-facing roof.
    vs=[(-205,-127,350),(-205,7,350),(-205,-60,428),(-75,-127,350),(-75,7,350),(-75,-60,428)]
    m.solid(vs,[[0,2,1],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],'a9aa86')
    for y in [-127,7]:m.beam((-209,y,351),(-209,-60,434),10,'55432a')
    m.box((-211,-60,380),(8,34,34),'2e3c2b',2)
    add_projecting_gable_roof(m)
    # Visible pegged joints and short corner braces articulate the timber frame.
    for y in [-193,193]:
        for x in [-129,129]:
            m.beam((x,y,261),(x-(38 if x>0 else -38),y,298),8,'685335')
            for z in [70,292]:
                m.box((x,y,z),(5,4,5),'a58a57',.7,variation=.015)
    for x in [-161,161]:
        for y in [-157,157]:
            m.beam((x,y,263),(x,y-(34 if y>0 else -34),298),8,'695637')
    # Thin threshold and small sill brackets help the facade feel constructed.
    m.box((0,-213,55),(119,29,10),'8d7851',2)
    for x in [-162,162]:
        for y in [-115,-62,62,115]:
            m.box((x,y,115),(23,10,21),'55472e',2)
    # Worn plaster patches stay thin so the timber and wall shapes remain clear.
    for xside in [-1,1]:
        for yy,zz,w,h in [(-133,91,25,40),(42,108,36,24),(135,270,24,32),(-24,260,18,37)]:
            m.box((xside*140,yy,zz),(2,w,h),m.rng.choice(['a7ab88','b9b993','d0cba4']),1,variation=.02)
    # Compress only the wall zone by 17%; preserve footing, steps and roof pitch.
    # Mapping every finished vertex keeps chimney, dormer and joinery coherent.
    def compact_z(z):
        return z if z <= 60 else (60 + (z-60)*.83 if z < 306 else z-41.82)
    m.vertices=[(x,y,compact_z(z)) for x,y,z in m.vertices]
    # Refresh component metadata after the piecewise geometric transform.
    for part in m.parts:
        faces=m.triangles[part['first']:part['end']]
        ids=sorted({i for face in faces for i in face})
        center=tuple(sum(m.vertices[i][axis] for i in ids)/len(ids) for axis in range(3))
        volume=0
        for face in faces:
            a,b,c=[sub(m.vertices[i],center) for i in face]
            volume+=dot(a,cross(b,c))/6
        assert volume>0, 'Compact cottage component has nonpositive volume'
        part['center']=center;part['volume']=volume
    return m


def build():
    return build_mesh().save()
