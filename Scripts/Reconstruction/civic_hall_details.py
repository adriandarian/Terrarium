"""Civic hall entrance depth and four-sided coursed masonry, in centimeters.

Runs before the architecture recipe's final X scale/reflection. Replaces only
explicitly recorded solid groups; the remaining geometry and colors are retained.
"""
from meshkit import Mesh

COURSES=(('50564b','585e52','606558','555b50'),
         ('69705f','747966','7b806c','707662'),
         ('898e78','939680','9d9e86','8f937d'),
         ('a5a58e','afac93','b5b099','a8a78f'))
MOSS=('6d7a39','7b8640','879248','727f39')
SAND=('dfc99c','e7d5ac','d4bd90','e3cfa5')
WOOD=('684727','714c2a','76512d','604123')
TEAL=('087269','087d74','117e76','0c897e')


def box(m,p,s,c,b=1.15):
    m.box(p,s,c,b,variation=.025)


def remove_sections(m,sections):
    removed={i for a,b in sections for i in range(a,b)}
    parts=[p for i,p in enumerate(m.parts) if i not in removed]
    triangles=[t for p in parts for t in m.triangles[p['first']:p['end']]]
    used=sorted({i for t in triangles for i in t})
    remap={old:new for new,old in enumerate(used)}
    cursor=0
    for p in parts:
        count=p['end']-p['first']
        p['first']=cursor;p['end']=cursor+count;cursor+=count
    m.vertices=[m.vertices[i] for i in used]
    m.colors=[m.colors[i] for i in used]
    m.triangles=[tuple(remap[i] for i in t) for t in triangles]
    m.parts=parts


def foundation(m):
    # Original wall-shaped masonry envelope, without the old corner outgrowths.
    half_x,half_y=436.5,184.5
    # Match the original -1 cm construction minimum so final pivot normalization
    # leaves all retained walls, windows and roof at their exact saved height.
    box(m,(0,0,51.5),(846,332,105),COURSES[0][0],.6)
    counts={}
    moss_vertices=[]
    for side,length,plane in [('front',856,-176),('back',856,176),('left',352,-428),('right',352,428)]:
        counts[side]=0
        for row in range(4):
            n=round(length/29)
            edges=[-length/2]+[-length/2+length/n*(i+(.5 if row%2 else 1)) for i in range(n if row%2 else n-1)]+[length/2]
            for col,(left,right) in enumerate(zip(edges,edges[1:])):
                center=(left+right)/2; width=right-left
                moss=row>=2 and ((col*7+row*3)%19<4 or (row==3 and (col<2 or col>=n-2)))
                color=MOSS[(col+row)%4] if moss else COURSES[row][(col*3+row)%4]
                start=len(m.vertices)
                if side in ('front','back'):
                    p=(center,plane,13+row*26);s=(width-1.2,16.5,24.8)
                else:
                    p=(plane,center,13+row*26);s=(16.5,width-1.2,24.8)
                m.box(p,s,color,1.4,variation=.065)
                if moss:moss_vertices.extend(m.vertices[start:])
                counts[side]+=1
                # Small mineral flakes on each side remain inside the envelope.
                for flake in range(m.rng.choice((0,1,1,2)) if width>18 else 0):
                    accent=COURSES[max(0,row-1)][m.rng.randrange(4)]
                    offset=m.rng.uniform(-width*.3,width*.3)
                    z=13+row*26+m.rng.uniform(-7,7)
                    flake_width=m.rng.uniform(2.2,5.2);flake_height=m.rng.uniform(1.2,3.0)
                    if side in ('front','back'):
                        pos=(center+offset,(1 if plane>0 else -1)*184.2,z)
                        size=(flake_width,.6,flake_height)
                    else:
                        pos=((1 if plane>0 else -1)*436.2,center+offset,z)
                        size=(.6,flake_width,flake_height)
                    box(m,pos,size,accent,.15)
    assert moss_vertices and all(abs(x)<=half_x and abs(y)<=half_y and 0<=z<=104 for x,y,z in moss_vertices)
    return {'stone_blocks_by_side':counts,'stone_course_colors_bottom_to_top':COURSES,
            'moss_contained_in_base_envelope':True,'base_half_extents_before_x_scale_cm':[half_x,half_y],
            'moss_colored_vertices':len(moss_vertices)}


def entrance(m):
    # Facing -Y: smaller Y values project toward the viewer.
    # Sandstone front -237, inner wood front -222, door face -184.
    for sx in (-1,1):
        # Outer dark timber outline wraps the complete sandstone arch.
        for row in range(6):
            box(m,(sx*85,-214,115+row*22),(14,32,22),WOOD[row%4],.9)
        for i in range(4):
            box(m,(sx*(82-i*17),-214,251+i*16),(20,32,24),WOOD[i%4],.9)
        box(m,(sx*14,-214,316),(18,32,24),WOOD[0],.9)
        # Sandstone jambs and stepped voussoirs retain individual joints.
        for row in range(6):
            box(m,(sx*66,-219,115+row*22),(22,36,21.1),SAND[row%4],1.25)
        for i in range(4):
            box(m,(sx*(64-i*17),-219,251+i*16),(25,36,22),SAND[(i+1)%4],1.25)
        # Deep wood reveal returns to the recessed leaf; no flat teal overlay.
        for row in range(6):
            box(m,(sx*49,-202,115+row*22),(10,40,22),WOOD[(row+1)%4],.7)
        for i in range(3):
            box(m,(sx*(46-i*17),-202,248+i*16),(19,40,18),WOOD[(i+1)%4],.7)
    box(m,(0,-214,328),(37,32,12),WOOD[0],.9)
    box(m,(0,-219,310),(25,36,25),SAND[1],1.25)
    box(m,(0,-202,294),(19,40,12),WOOD[0],.7)
    for row in range(9):
        width=88 if row<6 else (62 if row==6 else 28 if row==7 else 10)
        z=115+row*22 if row<8 else 287
        h=22 if row<8 else 10
        box(m,(0,-172,z),(width+5,6,h),'153e32',.3)
        n=max(1,round(width/18))
        for col in range(n):
            box(m,(-width/2+(col+.5)*width/n,-178,z),(width/n-.65,12,h-.45),TEAL[col%4],.8)
    for x in (-29,0,29):
        box(m,(x,-186,180),(4,5,146),TEAL[1],.45)
    for z in (151,206,250):
        width=82 if z<240 else 55
        box(m,(0,-187,z),(width,5,5),TEAL[2],.5)
    # Threshold spans the recess, physically joining the landing and door.
    for col in range(4):
        box(m,(-45+(col+.5)*22.5,-199,105),(22,49,10),COURSES[3][col],.8)
    return {'outer_timber_frame':True,'inner_timber_reveal':True,
            'sandstone_front_y_cm':-237,'door_front_y_cm':-184,
            'door_recess_cm':53,'inner_reveal_depth_cm':40}


def steps(m):
    for row in range(5):
        height=(5-row)*20.8;y=-231-row*26
        for course in range(5-row):
            for col in range(6):
                palette=COURSES[3] if course==4-row else COURSES[min(2,course)]
                box(m,(-84+(col+.5)*28,y,10.4+course*20.8),(27.2,27,20),palette[(col+row)%4],1.0)
        for sx in (-1,1):
            # Timber railing sits inside a wider stone cheek, exposing a band
            # of stone on its outside rather than ending in a bare wood slab.
            for course in range(5-row):
                box(m,(sx*125,y,10.4+course*20.8),(25,27,20),COURSES[min(3,course)][(row+course)%4],1.0)
            for course in range(max(1,round((height+30)/24))):
                count=max(1,round((height+30)/24));h=(height+30)/count
                box(m,(sx*100,y,course*h+h/2),(32,30,h-.45),WOOD[(row+course)%4],1.0)
    return {'stone_cheeks_both_sides':True,'stone_projection_beyond_timber_cm':21.5,
            'step_count':5,'individual_stone_riser_courses':True}


def refine(m,sections):
    remove_sections(m,sections)
    # These additions use an independent RNG so prior color variation survives.
    state=m.rng.getstate();m.rng.seed(1606)
    details={}
    details.update(foundation(m));details.update(entrance(m));details.update(steps(m))
    m.rng.setstate(state)
    m.entrance_foundation_details=details
