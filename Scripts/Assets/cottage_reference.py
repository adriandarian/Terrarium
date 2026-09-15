"""Reference-led cottage: compact plan, broad clay courses and short chimney."""
import math,random
from meshkit import Mesh,sub,cross,dot
import cottage_v6

CLAY=('914a2a','a95b32','ae6235','854228','9a512e','b16a3b','78402b')

def roof(m,origin=(0,0,0),z_scale=1):
    rng=random.Random(1501)
    for side in (-1,1):
        m.box((side*88,0,373),(252,422,12),'63402c',3,rot=(0,side*43,0))
        for row in range(5):
            x=side*(17+row*39)
            for col in range(8):
                y=-197+col*56+(7 if row%2 else -4)
                z=476-abs(x)*.94+rng.uniform(-2.5,2.5)
                m.box((x+rng.uniform(-2,2),y,z),(55,54+rng.uniform(-3,3),28+rng.uniform(-2,2)),
                      rng.choice(CLAY),4.2,rot=(0,rng.uniform(-2,2),rng.uniform(-1,1)))
                m.parts[-1]['roof_role']='reference_main_tile'
                if (row*8+col)%7==0:
                    m.box((x+side*14,y-9,z+14),(13,18,1.4),'bd804a',.6)
        m.box((side*185,0,288),(13,429,16),'5b452c',3)
    for i in range(7):
        m.box((0,-204+i*67,487+rng.uniform(-2,2)),(41,68,32),rng.choice(CLAY),4.7)
        m.parts[-1]['roof_role']='reference_ridge'

def gable_roof(m,origin=(0,0,0),z_scale=1):
    rng=random.Random(1502)
    for side in (-1,1):
        m.box((-150,-60+side*33,385),(163,105,10),'623e29',2.5,rot=(-side*49,0,0))
        for row in range(3):
            for col in range(4):
                x=-210+col*43;y=-60+side*(12+row*25)
                z=444-abs(y+60)*1.16+rng.uniform(-2,2)
                m.box((x,y,z),(46,40,23),rng.choice(CLAY),3.4)
                m.parts[-1]['roof_role']='reference_gable_tile'
    for x in (-214,-165,-116,-73):
        m.box((x,-60,451),(50,32,25),rng.choice(CLAY),3.7)
        m.parts[-1]['roof_role']='reference_gable_ridge'

def build():
    previous=(cottage_v6.add_main_roof,cottage_v6.add_projecting_gable_roof)
    try:
        cottage_v6.add_main_roof=roof;cottage_v6.add_projecting_gable_roof=gable_roof
        m=cottage_v6.build_mesh()
    finally:cottage_v6.add_main_roof,cottage_v6.add_projecting_gable_roof=previous
    # The underlying cottage, joinery and side gable stay coherent. The new
    # detailing pass's broad planters and shutters are intentionally absent.
    chimney_vertices=set()
    for part in m.parts:
        x,y,z=part['center']
        ids={i for t in m.triangles[part['first']:part['end']] for i in t}
        span=max(m.vertices[i][2] for i in ids)-min(m.vertices[i][2] for i in ids)
        if 45<x<113 and -123<y<-45 and z>365 and span>6 and 'roof_role' not in part:
            chimney_vertices.update(ids)
    result=[]
    for i,(x,y,z) in enumerate(m.vertices):
        if i in chimney_vertices:z=365+(z-365)*.60
        z=z if z<=60 else (60+(z-60)*1.10 if z<264.18 else z+20.418)
        result.append((x*.90,y*.86,z))
    m.vertices=result
    # A narrow front light and modest window framing from the concept.
    m.box((85,-159,183),(17,9,69),'34483a',1.5)
    for x in (98,73):m.box((x,-165,183),(6,9,79),'9c956e',1.5)
    for z in (142,223):m.box((85,-165,z),(32,12,7),'b4ad85',1.5)
    m.box((85,-166,183),(17,4,3),'a4a079',.6)
    # Footing moss and irregular weathering sit against the existing wall.
    for side in (-1,1):
        for y,z in [(-125,81),(-62,69),(97,91),(128,62)]:
            m.box((side*129,y,z),(4,19,15),'899071',1.2)
    # Recompute validation metadata after the nonuniform body/chimney edits.
    for part in m.parts:
        tris=m.triangles[part['first']:part['end']]
        ids={i for t in tris for i in t}
        center=tuple(sum(m.vertices[i][a] for i in ids)/len(ids) for a in range(3))
        volume=sum(dot(sub(m.vertices[t[0]],center),cross(sub(m.vertices[t[1]],center),sub(m.vertices[t[2]],center)))/6 for t in tris)
        assert volume>0
        part['center']=center;part['volume']=volume
    m.name='SM_Cottage_Reference_v2';m.revises='SM_Cottage_v6_Detail';m.refinement_pass=10
    return m.save()
