"""Reference-led shed revision: stepped teal tiles, timber hatch, trough and stone footing."""
from meshkit import Mesh

def build():
    m=Mesh('SM_Shed_v2',323);m.refinement_pass=2;m.revises='SM_Shed'
    # Several uneven foundation blocks replace the isolated corner feet.
    for x in [-78,-26,26,78]:
        for y in [-69,69]:m.box((x,y,15),(51,43,28),m.rng.choice(['777960','85836d','696f56']),4)
    for x in [-100,101]:
        for y in [-40,18,72]:m.box((x,y,9),(45,54,17),'74785e',4)
    m.box((0,0,28),(190,159,17),'473d29',3)
    for side in [-1,1]:
        for i in range(7):
            y=-64+i*21
            m.box((side*85,y,108),(17,20,157),m.rng.choice(['705835','80643a','68522f']),2)
            if i%2==0:m.box((side*94,y-4,110),(1.5,2.2,111),'493d28',.5)
        for y in [-74,74]:m.box((side*85,y,108),(23,22,178),'5d492b',3)
        for z in [37,188]:m.box((side*88,0,z),(21,163,16),'5e4b2e',3)
    for i in range(8):
        x=-79+i*23
        m.box((x,72,109),(22,18,157),m.rng.choice(['705b36','66512f']),2)
        if i in [0,1,6,7]:m.box((x,-72,109),(22,17,157),'79603a',2)
    m.gable((0,0,186),180,151,64,'59452b')
    # Small deeply framed front hatch, with modeled stave seams and iron latch.
    m.box((0,-78,107),(90,17,134),'29281d',2)
    for x in [-32,-10,12,34]:
        m.box((x,-88,105),(20,13,130),m.rng.choice(['6a502c','765b33','5e4728']),2)
        m.box((x+5,-95,103),(1.5,1.5,89),'433521',.4)
    for x in [-52,52]:m.box((x,-94,110),(13,21,153),'987447',3)
    for z in [34,185]:m.box((0,-96,z),(119,23,16),'82633a',3)
    for z in [62,143]:
        m.box((-27,-100,z),(35,4,6),'444333',1)
        m.box((-44,-103,z),(5,3,5),'77715b',.7)
    m.box((20,-102,111),(19,6,7),'3f4030',1)
    # Horizontal clay/wood shingle courses create the chunky stepped silhouette.
    for side in [-1,1]:
        m.box((side*55,0,216),(147,210,15),'234f4b',3,rot=(0,side*33,0))
        for row in range(3):
            x=side*(20+row*39)
            for col in range(5):
                y=-85+col*43+(5 if row%2 else -2)
                z=263-abs(x)*.66+m.rng.uniform(-2,2)
                m.box((x,y,z),(55,47,23),m.rng.choice(['2b7069','367e75','326e64','3c8378']),4,rot=(0,m.rng.uniform(-1,1),m.rng.uniform(-2,2)))
                if (row+col)%5==0:m.box((x+side*19,y-11,z+12),(8,14,2),'558b78',1)
    for i,y in enumerate(range(-91,101,38)):
        m.box((0,y,272),(33,42,29),m.rng.choice(['387d71','438577','2c6d63']),5,rot=(0,0,(i%2-.5)*2))
    # The reference's open wooden trough sits in front of the hatch.
    for x in [-42,42]:
        for y in [-140,-177]:m.box((x,y,18),(10,10,36),'59492c',2)
    m.box((0,-158,36),(108,49,8),'554329',2)
    m.box((0,-158,41),(91,33,3),'383b25',1)
    for y in [-184,-132]:m.box((0,y,49),(117,8,23),'8d6c3c',2)
    for x in [-56,56]:m.box((x,-158,49),(8,49,23),'7d5d33',2)
    # Broad flat gray rocks and low moss connect the footing to the meadow.
    for x,y,z,s in [(120,-78,13,(66,49,26)),(134,-40,9,(45,47,19)),(-112,48,8,(51,46,18))]:
        m.ellipsoid((x,y,z),s,'7f816a',7,3,rot=(0,0,19))
    for x,y in [(101,72),(-94,-83),(113,-26),(-71,83)]:
        m.box((x,y,11),(27,23,16),'657239',3,rot=(0,0,14))
    return m.save()
