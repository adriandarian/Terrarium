"""Reference study: narrow gable, deep side wall, thick staggered roof and worn joinery."""
from meshkit import Mesh

def build():
    m=Mesh('SM_Cottage_v4',217);m.refinement_pass=4;m.revises='SM_Cottage_v3'
    # Uneven individual foundation stones and patchy plaster, all closed solids.
    for y in [-180,180]:
        for x in [-110,-37,37,110]:m.box((x,y,25),(72,44,49),m.rng.choice(['797761','6b6d54','8a8469']),6)
    for x in [-154,154]:
        for y in [-145,-73,0,73,145]:m.box((x,y,25),(39,72,49),'70725a',6)
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
    # A thin dark structural roof is hidden by chunky non-coplanar clay courses.
    for side in [-1,1]:
        m.box((side*84,0,389),(242,406,17),'643d27',3,rot=(0,side*43,0))
        for row in range(5):
            x=side*(19+row*35)
            for col in range(7):
                y=-190+col*62+(9 if row%2 else -4)+m.rng.uniform(-3,3)
                z=472-abs(x)*.94+m.rng.uniform(-4,4)
                # Offset top faces, deep exposed tile ends, chipped clay patches.
                m.box((x,y,z),(55,68,31),m.rng.choice(['8d4b28','a4572c','9a512a','ac602f']),5,rot=(0,m.rng.uniform(-2,2),m.rng.uniform(-3,3)))
                if (row+col)%7==0:m.box((x+side*23,y-19,z+16),(7,12,2),'a76835',1,rot=(0,0,1))
    for i in range(8):m.box((0,-213+i*61,481),(48,65,38),m.rng.choice(['98522d','aa6031','854727']),6,rot=(0,0,m.rng.uniform(-2,2)))
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
    for side in [-1,1]:
        for row in range(3):
            yy=-60+side*(14+row*24)
            for col in range(4):
                xx=-210+col*40+(5 if row%2 else 0)
                m.box((xx,yy,441-abs(yy+60)+m.rng.uniform(-2,2)),(45,37,24),m.rng.choice(['96502b','a15b30','b16837','8c492a']),4,rot=(0,0,m.rng.uniform(-2,2)))
    for col in range(4):m.box((-211+col*40,-60,445),(46,30,27),'a75c32',4)
    # Worn plaster patches stay thin so the timber and wall shapes remain clear.
    for xside in [-1,1]:
        for yy,zz,w,h in [(-133,91,25,40),(42,108,36,24),(135,270,24,32),(-24,260,18,37)]:
            m.box((xside*140,yy,zz),(2,w,h),m.rng.choice(['a7ab88','b9b993','d0cba4']),1,variation=.02)
    result=m.save()
    import unreal,json
    from pathlib import Path
    sm=unreal.load_asset('/Game/Terrarium/Meshes/SM_Cottage_v4')
    mat=unreal.load_asset('/Game/Terrarium/Materials/M_WeatheredDetails')
    assert sm and mat
    sm.set_material(0,mat);assert unreal.EditorAssetLibrary.save_loaded_asset(sm)
    p=Path(unreal.Paths.project_dir(),'Docs/Phase1/Validation/SM_Cottage_v4.json')
    report=json.loads(p.read_text());report['surface_material']=mat.get_path_name()
    p.write_text(json.dumps(report,indent=2))
    return result
