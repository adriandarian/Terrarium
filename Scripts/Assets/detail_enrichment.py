"""Add crafted secondary forms to the existing soft asset recipes, in cm.

Base silhouettes, origins and contact elevations are retained. Surface markings
are embedded geometry; no texture downloads or replacement art designs.
"""
import math

def leaf(m,p,size=12,tint='74863d',yaw=0):
    m.ellipsoid(p,(size,size*.48,size*.21),tint,5,3,rot=(0,-12,yaw))

def tuft(m,x,y,z,size=1):
    for k in range(5):
        a=k*math.tau/5+.4
        tip=(x+math.cos(a)*12*size,y+math.sin(a)*12*size,z+(11+k%3*5)*size)
        m.beam((x,y,z),tip,2.4*size,'667c35',depth=1.1*size)
        leaf(m,tip,13*size,['829244','6f863c','8c984f'][k%3],math.degrees(a))

def barrel(m,x,y,z,r=20,h=46):
    m.ellipsoid((x,y,z+h/2),(r*2,r*2,h),'55422b',10,4)
    for i in range(10):
        a=i*math.tau/10
        m.box((x+math.cos(a)*r*.90,y+math.sin(a)*r*.90,z+h/2),
              (r*.57,4,h*.91),m.rng.choice(['8b6b40','745432','987448']),1.2,rot=(0,0,math.degrees(a)+90))
    for zz in (z+h*.2,z+h*.8):
        for i in range(10):
            a=i*math.tau/10
            m.box((x+math.cos(a)*r*.99,y+math.sin(a)*r*.99,zz),(r*.64,3,3),'535447',.5,rot=(0,0,math.degrees(a)+90))
    m.ellipsoid((x,y,z+h*.97),(r*1.64,r*1.64,3),'473a27',10,2)
    for offset in (-.5,0,.5):m.box((x,y+offset*r,z+h),(r*1.4,r*.43,2),'887046',.4)

def surface_details(m,name):
    """Sparse surface-bound marks using the original outward polygon normals."""
    # One candidate per existing solid: avoids multiplying every triangle seam.
    from meshkit import sub,cross,norm,dot
    base_parts=list(m.parts)
    stone=any(s in name for s in ('Cliff','Stone','Rock','Outcrop'))
    timber=any(s in name for s in ('Cottage','Shed','Bridge','Fence','Well','Lantern'))
    if not (stone or timber):return
    limit=100 if 'Cottage' in name else (45 if timber else 28)
    made=0
    for part in base_parts:
        if made>=limit:break
        if m.rng.random()>.48:continue
        candidates=[]
        for tri in m.triangles[part['first']:part['end']]:
            a,b,c=[m.vertices[i] for i in tri]
            n=norm(cross(sub(b,a),sub(c,a)))
            area=math.sqrt(dot(cross(sub(b,a),sub(c,a)),cross(sub(b,a),sub(c,a))))/2
            if area>70:candidates.append((area,a,b,c,n))
        if not candidates:continue
        _,a,b,c,n=max(candidates,key=lambda q:q[0])
        p=tuple((a[k]+b[k]+c[k])/3+n[k]*.12 for k in range(3))
        # Face-aligned shallow chips, with conservative size based on area.
        length=min(16,math.sqrt(candidates[0][0])*.45)
        if abs(n[2])>.8:
            size=(length,2.4 if timber else length*.45,.7)
            rot=(0,0,m.rng.uniform(-15,15))
        elif abs(n[0])>.8:
            size=(.7,2.0 if timber else length*.6,length)
            rot=(0,0,0)
        elif abs(n[1])>.8:
            size=(2.0 if timber else length*.6,.7,length)
            rot=(0,0,0)
        else:continue
        # Derive pigment from the sampled part so plaster never gains brown scratches.
        rgb=m.colors[m.triangles[part['first']][0]]
        factor=m.rng.choice([.73,1.19])
        from meshkit import color
        start=len(m.colors)
        m.box(p,size,'stone',.2,rot=rot,variation=0)
        m.colors[start:]=[tuple(min(.9,v*factor) for v in rgb)]*(len(m.colors)-start)
        made+=1

def enrich(m):
    original=m.name
    before=len(m.triangles)
    surface_details(m,original)
    if 'MeadowTile' in original:
        # Distinct living turf over the original low substrate; no regular pixel grid.
        for i in range(11):
            x,y=m.rng.uniform(-85,85),m.rng.uniform(-85,85)
            size=m.rng.uniform(17,36)
            m.box((x,y,6.2),(size,size*m.rng.uniform(.45,.85),2.7),
                  m.rng.choice(['6e7f37','829047','74863b','92984f']),1.2,
                  rot=(0,0,m.rng.uniform(-35,35)))
        for x,y in [(-57,21),(46,52),(11,-57)]:
            for i in range(4):
                leaf(m,(x+i*3,y-i*2,6.8),18,'819044',i*63)
        for i in range(4):
            m.ellipsoid((m.rng.uniform(-85,85),m.rng.uniform(-85,85),7),
                        (8,6,4),'8b8966',5,3)
        detail='overlapping low turf leaves and embedded pebbles; taller grass remains in planted clusters'
    elif 'Cottage' in original:
        # Existing side windows, compacted facade coordinates.
        for side in (-1,1):
            for yy in (-88,89):
                for edge in (-1,1):
                    y=yy+edge*53
                    m.box((side*160,y,170),(12,24,92),'5c6640',2)
                    for dz in range(135,208,13):m.box((side*168,y,dz),(3,21,9),'82905b',1)
                    for dz in (140,202):m.box((side*171,y,dz),(2,25,4),'474b32',.5)
                m.box((side*179,yy,112),(30,99,23),'725735',2)
                for z in (107,120):m.box((side*195,yy,z),(3,101,3),'a0824f',.5)
                for y in (yy-32,yy,yy+32):
                    tuft(m,side*180,y,125,.9)
        # Small lean-to stack of split firewood at the back footing.
        for row in range(3):
            for col in range(4-row):
                m.box((-117+col*21,204,18+row*17),(19,47,15),['826139','a1804b'][col%2],2)
        for side in (-1,1):
            for yy in (-130,35,130):
                for zz in (99,128):m.box((side*142,yy,zz),(3,26,12),'b3aa82',1)
        barrel(m,119,215,0,20,44)
        detail='slatted shutters, planted sill boxes, plaster repair edges, stacked firewood, stave barrel, surface wear'
    elif 'Shed' in original:
        barrel(m,-117,14,0,21,48)
        for x in (-43,43):
            for z in (65,144):
                m.box((x,-105,z),(5,2,5),'ad9765',.5)
        for x in range(-40,41,16):m.box((x,-158,44),(12,29,2),'596845',.4)
        for y in range(-177,-139,8):m.box((0,y,45),(86,1.6,.8),'709080',.2)
        for x in (-87,87):
            for y in (-58,-12,34,64):
                m.box((x*1.09,y,150),(1,5,10),'ac8c58',.3)
        detail='barrel, hinge pins, trough boards and water, worn plank edges'
    elif 'PlankBridge' in original:
        for x in (-104,104):
            for y,z in ((-245,95),(0,98),(245,94)):
                for dz in (-5,0,5):m.box((x,y,z+dz),(15,16,2.4),'b39b67',.6)
        for i in range(13):
            y=-246+i*41
            m.ellipsoid(((-1)**i*43,y,68),(14,7,1.2),'644b2e',7,2)
            m.ellipsoid(((-1)**i*43+1,y,68.6),(7,3,.7),'a08452',6,2)
        detail='rope lashings, embedded plank knots, grain and chipped end marks'
    elif 'FencePost' in original:
        for y in (-11,11):
            for z in (47,96):m.box((0,y,z),(5,2,5),'454632',.5)
            for x in (-4,3):m.box((x,y,70),(1.4,1,62),'aa8854',.2)
        tuft(m,8,6,15,.6)
        detail='nails, split wood grain, rooted moss tuft'
    elif 'FenceRails' in original:
        for x in (-71,71):
            for z in (48,98):m.box((x,-7.5,z),(4,2,4),'494631',.5)
        for z in (48,98):
            for x in (-45,20):m.box((x,-7,z),(29,1,1.2),'bc9960',.2)
        m.box((45,-7,47),(11,1,5),'665037',.4)
        detail='pegged rail joints, elongated grain streaks, dark timber knot'
    elif 'GardenWell' in original:
        # A real open bucket alongside the stone ring.
        for i in range(9):
            a=i*math.tau/9
            m.box((64+math.cos(a)*12,-28+math.sin(a)*12,17),(8,3,27),'96764c',1,rot=(0,0,math.degrees(a)+90))
        for x in (52,76):m.beam((x,-28,30),(x,-28,48),2,'565b4b')
        m.beam((52,-28,48),(76,-28,48),2,'565b4b')
        for i in range(8):
            x=-17+i*5
            m.box((x,-14,160),(2,2,22),'c1ad7b',.4)
        for a in range(0,360,60):
            r=math.radians(a);tuft(m,math.cos(r)*48,math.sin(r)*48,69,.37)
        detail='open stave bucket, winding-rope strands, small moss rooted in stone joints'
    elif 'LanternPost' in original:
        for z in (179,202):m.box((0,-17,z),(34,2,2),'666745',.5)
        m.box((0,-18,191),(2,2,37),'6d6b48',.5)
        for x in (-10,10):m.box((x,-17.5,191),(2,1,19),'ebcf7c',.3)
        for z in (51,121):m.box((0,0,z),(16,16,5),'8b8054',1)
        detail='pane mullions and reflected strips, post collars, weathering'
    elif 'GardenBed' in original:
        wide='v3' in original
        xr,yr=(124,97) if wide else (88,67)
        for i in range(26):
            x,y=m.rng.uniform(-xr,xr),m.rng.uniform(-yr,yr)
            m.ellipsoid((x,y,21),(8,5,4),'806540',5,3)
        for x in (-xr,xr):
            m.beam((x,0,20),(x,0,69),3,'b19861')
            m.box((x,-1,59),(19,4,13),'c2b28a',1)
        # Small crop veins and curled tips at multiple heights, kept over soil.
        for i in range(12):
            x,y=m.rng.uniform(-xr*.8,xr*.8),m.rng.uniform(-yr*.8,yr*.8)
            leaf(m,(x,y,30),13,'809947',i*37)
        detail='soil clods, plant labels, overlapping young leaves and vein accents'
    elif 'Traveler' in original:
        m.beam((-12,-21,112),(13,-23,81),3,'75542e')
        for z in (85,96,106):m.box((0,-21,z),(2.4,1.2,2.4),'e4c27b',.4)
        m.box((23,10,78),(13,13,18),'7d6339',2)
        m.box((23,10,87),(14,14,5),'aa8a50',1)
        for x in (-12,12):
            for y in (-10,-4,2):m.box((x,y,14),(9,1.3,1),'99825e',.2)
        m.box((0,30,115),(24,2,5),'d0b47e',.5)
        detail='diagonal satchel strap, fasteners, belt pouch, boot laces, bedroll stitching'
    elif 'Wheat' in original:
        for i in range(22):
            x,y=m.rng.uniform(-124,124),m.rng.uniform(-104,104)
            m.beam((x,y,8),(x+16,y+9,13),1.8,'b2a154')
        for x in (-92,0,92):tuft(m,x,82,8,.85)
        detail='fallen straw, low green companion growth between existing grain stalks'
    elif 'Tree' in original or 'Bush' in original:
        tall='Tree' in original
        centers=[(-56,13,177),(48,-27,201),(-39,-35,258),(43,18,281),(-24,30,308),(3,7,359)] if tall else [(-33,3,58),(25,17,64),(0,-23,75),(4,25,85)]
        for cx,cy,cz in centers:
            for i in range(9):
                a=i*math.tau/9
                p=(cx+math.cos(a)*23,cy+math.sin(a)*22,cz+m.rng.uniform(-6,12))
                leaf(m,p,m.rng.uniform(10,17),m.rng.choice(['8b9947','647d31','7e913b']),math.degrees(a))
        for z in range(22,290 if tall else 45,23):
            m.box((-8,-10,z),(6,1.5,14),'a1834b',.5)
        if not tall:
            for p in [(-28,-19,53),(28,-17,61),(33,22,63)]:
                m.ellipsoid(p,(7,7,8),'c28a43',6,3)
        detail='small overlapping leaf tips, bark ridges, berry and bud accents'
    elif 'MeadowGrass' in original:
        for x,y,s in [(-13,3,.65),(11,-5,.9),(2,13,.5)]:tuft(m,x,y,0,s)
        detail='broad leafy bases and intermediate blades around fine existing grass'
    elif 'MeadowFlowers' in original:
        for i in range(5):
            a=i*math.tau/5;x,y=math.cos(a)*17,math.sin(a)*13
            leaf(m,(x,y,7),15,'768842',i*72)
            m.beam((x,y,0),(x+2,y,23),1.5,'5f7734')
            m.ellipsoid((x+2,y,23),(4,4,7),'cdb66a',5,3)
        detail='basal rosette leaves and unopened flower buds'
    elif 'GroundPlants' in original:
        for i in range(5):
            a=i*math.tau/5
            m.beam((0,0,2),(math.cos(a)*14,math.sin(a)*14,27),1.3,'9a9d57')
            leaf(m,(math.cos(a)*13,math.sin(a)*13,26),9,'8d9b4e',i*72)
        detail='upright young fern fronds and pale growing tips'
    elif 'Reeds' in original:
        for i in range(9):
            a=i*math.tau/9;x,y=math.cos(a)*18,math.sin(a)*18
            m.beam((x,y,-2),(x+14,y-7,40+i*3),2,'85924a',depth=.8)
            leaf(m,(x+13,y-6,32+i*3),12,'9aa65b',i*40)
        detail='curved secondary reed leaves and lighter leaf ribs'
    elif 'CliffMoss' in original:
        for z in range(-75,1,12):
            for y in (-7,5):leaf(m,(20,y,z),8,'8c984b',z*3)
        detail='layered small moss leaves over the original hanging fingers'
    elif 'CliffColumn' in original:
        for axis in (0,1):
            for sign in (-1,1):
                for i in range(9):
                    p=[m.rng.uniform(-32,32),m.rng.uniform(-32,32),m.rng.uniform(265,313)]
                    p[axis]=sign*49
                    size=[m.rng.uniform(7,16),m.rng.uniform(7,16),m.rng.uniform(5,12)];size[axis]=5
                    m.box(tuple(p),tuple(size),m.rng.choice(['71813b','879044','596f31']),1.4)
        detail='small lichen colonies, moss transition clusters, mineral surface chips'
    elif 'StoneStairs' in original:
        for i in range(8):
            y=-147+i*42;z=30*(i+1)+9
            for x in (-53,30):m.box((x,y-5,z-.2),(17,9,1.2),'b2a582',.5,rot=(0,0,i*11))
            for x in (-93,93):tuft(m,x,y+14,z,.35)
        detail='polished foot-wear patches, small grasses growing from tread corners'
    elif any(s in original for s in ('RockCluster','ShoreOutcrop','RiverStones')):
        # Surface placements derived from the real top triangles keep lichen attached.
        from meshkit import sub,cross,norm
        surfaces=[]
        for tri in list(m.triangles):
            a,b,c=[m.vertices[i] for i in tri];n=norm(cross(sub(b,a),sub(c,a)))
            if n[2]>.75:
                p=tuple((a[k]+b[k]+c[k])/3 for k in range(3))
                if p[2]>5:surfaces.append(p)
        for p in m.rng.sample(surfaces,min(15,len(surfaces))):
            m.ellipsoid((p[0],p[1],p[2]+.1),(6,4,1.2),'829062',5,2)
        detail='surface-bound lichen flecks, mineral chips, weathering'
    elif 'PathTile' in original:
        for i in range(12):
            x,y=m.rng.uniform(-98,98),m.rng.uniform(-78,78)
            m.ellipsoid((x,y,1),(m.rng.uniform(4,10),m.rng.uniform(3,7),2),
                        m.rng.choice(['aa9873','baa57b','8e805d']),5,3)
        for x,y in [(-76,94),(51,-97)]:tuft(m,x,y,1,.55)
        detail='embedded gravel of mixed sizes, low verge leaves, broken soil texture'
    elif 'Water' in original:
        for i in range(10):
            x,y=m.rng.uniform(-125,125),m.rng.uniform(-125,125)
            for j in range(2):
                m.box((x+j*7,y+j*4,2.1),(m.rng.uniform(7,15),1.3,.5),'63aca7',.1,rot=(0,0,23))
        detail='paired broken ripple glints over the original continuous surface'
    else:raise ValueError('Missing detail specification: '+original)
    m.name=original+'_Detail';m.revises=original;m.refinement_pass=9
    assert len(m.triangles)>before,original
    return {'original':original,'asset':m.name,'detail':detail,'triangles_before':before,'triangles_after':len(m.triangles)}
