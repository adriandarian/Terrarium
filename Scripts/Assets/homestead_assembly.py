"""Complete homestead asset family guided by the isolated assembly reference."""
import math,random
from meshkit import Mesh,sub,cross,dot
import cottage_reference,shed_context

def recipe(fn):
    save=Mesh.save
    try:
        Mesh.save=lambda self:self
        return fn()
    finally:Mesh.save=save

def refresh(m):
    for p in m.parts:
        ts=m.triangles[p['first']:p['end']];ids={i for t in ts for i in t}
        c=tuple(sum(m.vertices[i][k] for i in ids)/len(ids) for k in range(3))
        p['center']=c;p['volume']=sum(dot(sub(m.vertices[t[0]],c),cross(sub(m.vertices[t[1]],c),sub(m.vertices[t[2]],c)))/6 for t in ts)
        assert p['volume']>0

def wear(m,budget=100):
    """Small relief patches on actual broad faces, colored from their material."""
    rng=random.Random(3109);done=0
    for part in list(m.parts):
        if done>=budget:break
        ts=m.triangles[part['first']:part['end']];ids={i for t in ts for i in t}
        lo=[min(m.vertices[i][k] for i in ids) for k in range(3)]
        hi=[max(m.vertices[i][k] for i in ids) for k in range(3)]
        span=[hi[k]-lo[k] for k in range(3)]
        for axis in (2,0,1):
            uv=[k for k in range(3) if k!=axis]
            if min(span[k] for k in uv)<16 or rng.random()>.60:continue
            for sign in ((1,) if axis==2 else (-1,1)):
                center=[(lo[k]+hi[k])/2 for k in range(3)]
                center[axis]=(hi[axis] if sign==1 else lo[axis])+sign*.18
                for k in uv:center[k]+=rng.uniform(-.22,.22)*span[k]
                size=[min(span[k]*.20,rng.uniform(5,12)) for k in range(3)];size[axis]=.65
                start=len(m.colors);rgb=m.colors[next(iter(ids))]
                m.box(tuple(center),tuple(size),'stone',.2,variation=0)
                factor=rng.choice((.68,.80,1.20,1.37))
                m.colors[start:]=[tuple(min(.95,v*factor) for v in rgb)]*(len(m.colors)-start)
                done+=1
    return m

def roof_wear(m,teal=False):
    for p in list(m.parts):
        ts=m.triangles[p['first']:p['end']];ids={i for t in ts for i in t}
        lo=[min(m.vertices[i][k] for i in ids) for k in range(3)];hi=[max(m.vertices[i][k] for i in ids) for k in range(3)]
        if teal:
            if lo[2]<192 or not (25<hi[0]-lo[0]<85 and 25<hi[1]-lo[1]<85):continue
        elif not p.get('roof_role','').startswith('reference'):continue
        cx,cy,cz=p['center'];w=hi[0]-lo[0];d=hi[1]-lo[1]
        light='529589' if teal else 'bf8546';dark='24584e' if teal else '794024'
        m.box((cx-w*.24,cy+d*.17,hi[2]+.10),(w*.24,d*.18,1.0),light,.3)
        m.box((cx+w*.19,lo[1]-.15,cz+3),(w*.23,.8,8),light,.3)
        m.box((lo[0]-.15,cy-d*.12,cz-2),(.8,d*.18,10),dark,.3)

def cottage():
    m=recipe(cottage_reference.build)
    for part in m.parts:
        if part.get('roof_role','').startswith('reference'):
            z=part['center'][2]
            for i in {i for t in m.triangles[part['first']:part['end']] for i in t}:
                x,y,zz=m.vertices[i];m.vertices[i]=(x,y,z+(zz-z)*1.43)
    refresh(m)
    # A compact side porch/railing beside the front steps.
    m.box((97,-181,43),(83,74,16),'6c4d2b',2.8)
    for x in (65,134):
        for y in (-213,-155):m.box((x,y,30),(17,17,61),'51412a',2)
    for x in (66,134):m.box((x,-221,70),(17,17,77),'695031',2.5)
    for z in (53,88):m.box((100,-224,z),(91,12,13),'927043',2)
    for x in (64,136):m.box((x,-183,85),(12,89,13),'7b5a31',2)
    # Articulated dark stone corner plinths and visibly rooted moss.
    for x in (-136,136):
        for y in (-154,153):
            for z in (15,42,70):m.box((x,y,z),(40,42,25),m.rng.choice(('525845','656a55','7a7c63')),3)
            for dx,dy,z in [(17,9,9),(-7,23,14),(9,-13,77)]:
                m.box((x+dx,y+dy,z),(25,23,12),m.rng.choice(('758138','5e702b','879140')),2)
    # Broad, broken plaster areas stay behind the principal timber framing.
    for x in (-78,82,109):
        for z in (94,132,209,244):
            if x<0 and z<209:continue
            m.box((x,-156,z),(m.rng.uniform(12,26),1.8,m.rng.uniform(10,27)),m.rng.choice(('b1ad84','ddd0a1','c3b991')),1)
    for y in (-121,-38,38,120):
        for z in (97,245):m.box((-126,y,z),(1.7,19,22),m.rng.choice(('a9aa80','d9cca0','b9b188')),1)
    # Stacked boards and a braced crate nest below the side windows.
    m.box((-156,66,30),(42,64,59),'493d27',2)
    for y in (42,59,76,93):m.box((-180,y,30),(8,15,52),'79532e',1.8)
    for z in (8,51):m.box((-185,66,z),(8,69,9),'917044',1.5)
    m.beam((-190,38,12),(-190,94,48),7,'594629')
    for y in (105,120,135):m.box((-152,y,13),(40,12,24),'566334',2)
    roof_wear(m);wear(m,220);m.name='SM_Assembly_Cottage_v2';m.revises='SM_Cottage_Reference_v2';return m.save()

def shed():
    m=recipe(shed_context.build)
    # Small recessed side light in the visible left wall, as in the reference.
    m.box((96,5,111),(4,45,56),'433723',1)
    m.box((99,5,111),(4,32,43),'986b2a',1)
    for y in (-23,33):m.box((102,y,111),(11,9,68),'86663e',2)
    for z in (77,145):m.box((102,5,z),(12,64,10),'ac8750',2)
    m.box((106,5,110),(8,5,46),'5d442a',1)
    for x,y,z in [(121,45,12),(160,69,8),(-100,-73,11),(83,-69,15)]:
        m.box((x,y,z),(25,23,16),'718131',2.5)
    roof_wear(m,True);wear(m,150);m.name='SM_Assembly_BlueShed_v2';m.revises='SM_Shed_Context_Reference';return m.save()

def tower():
    m=Mesh('SM_Assembly_Tower',3112)
    # Four staggered courses give the pedestal a broken, stepped silhouette.
    for row in range(4):
        span=128-row*12;z=14+row*28
        for side in (-1,1):
            for k in (-1,1):m.box((k*span/4,side*(span/2-14),z),(span/2-2,30,29),m.rng.choice(('777c65','969981','626b57')),3)
            m.box((side*(span/2-14),0,z),(30,span-53,29),'828771',3)
    for z in (117,159,195):m.box((0,0,z),(71,66,13),'4f3d22',2)
    m.box((0,0,155),(49,48,92),'77562c',2)
    for x in (-31,31):
        for y in (-29,29):m.box((x,y,176),(13,13,162),'5e4928',2)
    for y in (-34,34):
        for x in (-14,10):m.box((x,y,158),(17,7,45),'a07035',1.4)
        m.beam((-31,y,134),(28,y,175),8,'3e3825')
        for z in (208,251):m.box((0,y,z),(78,11,12),'594324',2)
        m.box((0,y,230),(49,5,33),'e5b346',1)
        for x in (-22,0,22):m.box((x,y*1.10,230),(5,5,36),'4b3820',1)
    for x in (-35,35):
        m.box((x,0,230),(5,47,33),'b38932',1)
        for y in (-21,0,21):m.box((x*1.08,y,230),(5,5,36),'4a3d24',1)
    # Irregular stone crown and short spires, replacing the old clock-like cap.
    m.box((0,0,263),(91,86,15),'4b513d',3)
    for x,y,z,s in [(-30,-21,278,(33,32,19)),(23,-24,276,(36,30,20)),(-16,24,281,(40,33,24)),
                      (32,20,279,(31,34,18)),(0,0,297,(29,29,26)),(-27,19,312,(25,24,34)),(18,-18,326,(27,26,41))]:
        m.box((x,y,z),s,m.rng.choice(('636953','79806a','535b48')),2.8)
    for x,y in [(-48,45),(44,37),(-40,-47)]:m.box((x,y,10),(27,25,17),'65743a',3)
    wear(m,90);return m.save()

def lantern():
    m=Mesh('SM_Assembly_Lantern',3113)
    m.box((0,0,14),(48,44,28),'74795d',3)
    m.box((0,0,32),(24,24,10),'596044',2)
    m.box((0,0,109),(12,13,148),'4e4a2c',1.5)
    m.box((0,0,184),(35,33,45),'e1b04a',2)
    for x in (-20,20):
        for y in (-19,19):m.box((x,y,184),(6,6,50),'3d4030',1)
    for z in (159,208):m.box((0,0,z),(49,45,9),'484b38',2)
    for x in (-15,15):
        for y in (-13,13):m.box((x,y,220),(21,19,16),'68705b',2)
    for x,y,z in [(-13,9,233),(12,-10,239),(0,1,241)]:m.box((x,y,z),(9,9,19),'91957a',1.7)
    for x in (-7,7):m.box((x,-18,184),(4,3,36),'77602e',.7)
    m.box((-15,13,27),(18,13,7),'687d35',2)
    wear(m,35);return m.save()

def fence_post():
    m=Mesh('SM_Assembly_FencePost',3114)
    m.box((0,0,69),(21,22,138),'71502a',2)
    m.box((0,0,139),(26,26,12),'a47940',2)
    m.box((0,-11,68),(12,1.5,110),'896332',.3)
    for z in (43,96):m.box((0,-12,z),(24,5,27),'5a4225',1)
    m.box((2,2,9),(29,27,18),'6a7041',2.5)
    wear(m,16);return m.save()

def fence_rails():
    m=Mesh('SM_Assembly_FenceRails',3115)
    for z in (42,96):
        m.box((0,0,z),(172,13,15),'8b5a2d',1.6)
        m.box((0,-7,z+4),(170,2,4),'b08043',.4)
        for x in (-66,65):m.box((x,-8,z),(4,2,4),'423a26',.5)
    wear(m,20);return m.save()

def vegetable_bed():
    m=Mesh('SM_Assembly_VegetableBed',3116)
    m.box((0,0,8),(258,212,16),'524529',3)
    for x in (-131,131):m.box((x,0,20),(12,223,28),'79502a',2)
    for y in (-108,108):m.box((0,y,20),(274,12,28),'916135',2)
    for x in (-132,0,132):
        for y in (-109,109):
            m.box((x,y,23),(19,19,45),'634223',2)
            m.box((x,y,46),(22,22,7),'a77d45',1.5)
    for row in range(4):
        y=-78+row*52;m.box((0,y,17),(241,33,13),'68512a',2.5)
        for col in range(5):
            x=-101+col*50;z=33+m.rng.uniform(-2,3)
            if (row+col)%4==0:
                for dx,dy in [(-6,0),(6,4)]:m.box((x+dx,y+dy,29),(13,14,18),'a86b28',2.4)
                for k in range(4):m.box((x+(k%2*2-1)*7,y+(k//2*2-1)*7,43),(9,19,20),'6d7b35',2,rot=(0,30,k*90))
            else:
                m.box((x,y,z),(28,27,25),'547032',5,rot=(0,0,13))
                for k in range(5):
                    ang=k*math.tau/5
                    m.box((x+math.cos(ang)*13,y+math.sin(ang)*13,z-2),(26,16,13),m.rng.choice(('73833d','49642c','89924a')),3,rot=(0,22,math.degrees(ang)))
                m.box((x-3,y+1,z+11),(20,18,14),'7e9149',3)
    wear(m,60);return m.save()

def flower_border():
    m=Mesh('SM_Assembly_FlowerBorder',3117)
    m.box((0,0,6),(205,69,12),'50552b',3)
    for x in range(-96,100,24):
        for y in (-34,34):m.box((x,y,10),(23,16,21),m.rng.choice(('60722e','788032','4d6329')),2)
    for i in range(9):
        x=-87+i*22;y=(-1)**i*12;h=37+(i%4)*15
        m.beam((x,y,9),(x+3,y,h),3.5,'506329')
        for k in range(3):m.box((x+(-1)**k*9,y,18+k*10),(17,12,13),m.rng.choice(('5e762f','3d5d2b','7b8636')),3,rot=(0,20,k*80))
        for dx,dy in [(-4,0),(4,0),(0,-4),(0,4)]:m.box((x+dx,y+dy,h),(9,9,10),m.rng.choice(('b57121','cf8428','9d571d')),1.8)
        m.box((x,y,h+4),(6,6,8),'e29e37',1.5)
    # One taller branched flower anchors the outer end, as in the reference.
    m.beam((-94,12,9),(-94,12,111),4,'624b25')
    for dx,dy,z in [(-8,0,99),(9,0,108),(0,-8,112),(0,8,119)]:m.box((-94+dx,12+dy,z),(12,12,16),'d18022',2)
    wear(m,30);return m.save()

BUILDERS={'SM_Assembly_Cottage_v2':cottage,'SM_Assembly_BlueShed_v2':shed,'SM_Assembly_Tower':tower,
 'SM_Assembly_Lantern':lantern,'SM_Assembly_FencePost':fence_post,'SM_Assembly_FenceRails':fence_rails,
 'SM_Assembly_VegetableBed':vegetable_bed,'SM_Assembly_FlowerBorder':flower_border}
