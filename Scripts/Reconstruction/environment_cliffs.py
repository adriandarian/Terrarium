"""Fine interlocking cliff courses preserving the 323.5 cm terrain contract.

Three unsaved meshkit.Mesh builders. No editor calls or scene mutations.
Each prop stays within a 100 x 100 cm footprint and has exact Z bounds 0..323.5.
"""
from meshkit import Mesh

STONE=('625e49','8b896b','777654','686b50','999271','80845b')
MOSS=('768443','808c4a','6f7e3c','87914f','798846')
HEIGHT=323.5
FOOTPRINT=100.0

SPECS={
    'cliff_a':{'name':'SM_Env_Cliff_A','seed':6101},
    'cliff_b':{'name':'SM_Env_Cliff_B','seed':6173},
    'cliff_c':{'name':'SM_Env_Cliff_C','seed':6257},
}


def block(m,position,size,color,bevel=.8):
    m.box(position,size,color,bevel,variation=.008)


def divisions(m,row,axis,variant):
    """Mostly two broad stones, with occasional finer interlocking courses."""
    count=3 if (row+axis+variant)%4==2 else 2
    # Instance centers are 72 cm apart with native XY scale 72/84. A narrower
    # stone body leaves face joints visible instead of burying them in neighbors.
    width=m.rng.uniform(78.0,83.0)
    offset=m.rng.uniform(-1.5,1.5)
    low,high=offset-width/2,offset+width/2
    if count==2:
        # The center joint moves independently across consecutive courses.
        edges=[low,offset+m.rng.uniform(-3,3),high]
    else:
        edges=[low,offset-width/6+m.rng.uniform(-1.2,1.2),
               offset+width/6+m.rng.uniform(-1.2,1.2),high]
    return list(zip(edges,edges[1:]))


def build(key):
    spec=SPECS[key];variant=list(SPECS).index(key)
    m=Mesh(spec['name'],spec['seed']);m.refinement_pass=2
    # Closed core seals the thin mortar gaps and meets both footing and cap.
    block(m,(0,0,151.5),(68,68,303),'625f4b',.6)
    for row in range(10):
        # 30.3 cm courses remain squat at the scene's enlarged vertical scales.
        bottom=row*30.3;top=(row+1)*30.3
        x_ranges=divisions(m,row,0,variant)
        y_ranges=divisions(m,row,1,variant)
        for ix,(left,right) in enumerate(x_ranges):
            for iy,(front,back) in enumerate(y_ranges):
                # Different tones per individual stone avoid continuous stripes.
                color=STONE[(ix*2+iy*3+row+variant+m.rng.randrange(3))%len(STONE)]
                # Individually protruding/recessed exposed faces create cube
                # silhouettes and shadow changes, not a continuous brick veneer.
                l,r,f,b=left,right,front,back
                if ix==0:l-=m.rng.uniform(-2.0,4.0)
                if ix==len(x_ranges)-1:r+=m.rng.uniform(-2.0,4.0)
                if iy==0:f-=m.rng.uniform(-2.0,4.0)
                if iy==len(y_ranges)-1:b+=m.rng.uniform(-2.0,4.0)
                l=max(l,-43.5);r=min(r,43.5)
                f=max(f,-43.5);b=min(b,43.5)
                z_shift=0 if row in (0,9) else m.rng.uniform(-1.8,1.8)
                gap=.65
                block(m,((l+r)/2,(f+b)/2,(bottom+top)/2+z_shift),
                      (r-l-gap,b-f-gap,top-bottom-.5),color,
                      m.rng.uniform(.6,1.0))
    body_bounds={'min':[min(v[i] for v in m.vertices) for i in range(3)],
                 'max':[max(v[i] for v in m.vertices) for i in range(3)]}
    # The cap is exactly one module wide, without projecting broad ledges.
    cell=FOOTPRINT/3
    heights=[]
    for ix in range(3):
        for iy in range(3):
            top=HEIGHT if (ix,iy)==(1,1) else m.rng.choice((319.5,321.5,323.5))
            heights.append(top)
            # Coplanar edges touch; shallow bevels retain small voxel highlights.
            block(m,((ix-1)*cell,(iy-1)*cell,top-10),(cell,cell,20),
                  MOSS[(ix+2*iy+variant)%len(MOSS)],.75)
    # A few broken moss trails blend cap into upper courses, not a green belt.
    for face in range(4):
        run=(-27,4,29)[(face+variant)%3]
        length=2+(face+variant)%2
        for step in range(length):
            z=304-step*13
            size=12 if step==length-1 else 16
            if face in (0,1):
                pos=((-1 if face==0 else 1)*39,run+step*2,z)
                dimensions=(10,size,14)
            else:
                pos=(run-step*2,(-1 if face==2 else 1)*39,z)
                dimensions=(size,10,14)
            block(m,pos,dimensions,MOSS[(face+step+variant)%len(MOSS)],.65)
    bounds={'min':[min(v[i] for v in m.vertices) for i in range(3)],
            'max':[max(v[i] for v in m.vertices) for i in range(3)]}
    assert abs(bounds['min'][2])<1e-9 and abs(bounds['max'][2]-HEIGHT)<1e-9
    assert all(-50.000001<=v[i]<=50.000001 for v in m.vertices for i in (0,1))
    spec.update(bounds_cm=bounds,dimensions_cm=[bounds['max'][i]-bounds['min'][i] for i in range(3)],
                stone_courses=10,stone_body_bounds_cm=body_bounds,core_width_cm=68,
                cap_cells=9,cap_heights_cm=heights,
                triangles=len(m.triangles),closed_components=len(m.parts),
                reference='environment image-1.png; stage5 cliff comparison')
    return m


def cliff_a():return build('cliff_a')
def cliff_b():return build('cliff_b')
def cliff_c():return build('cliff_c')


BUILDERS={'cliff_a':cliff_a,'cliff_b':cliff_b,'cliff_c':cliff_c}
