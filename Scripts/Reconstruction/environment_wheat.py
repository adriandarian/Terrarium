"""Sparse, readable wheat ears for the assembled environment, in centimeters.

Host-safe recipe construction: returns one unsaved meshkit.Mesh. The nominal
placement footprint is 200x200 cm and every stem starts at Z=0. There is no field
base, soil rectangle, grass carpet or other continuous ground-cover geometry.
"""
from meshkit import Mesh


SPECS = {
    'wheat_patch': {
        'name': 'SM_Env_WheatPatch',
        'placement_footprint_cm': [200, 200],
        'bounds_cm': {'min': [-93.08545, -90.90647, 0], 'max': [93.26202, 89.98827, 115]},
        'dimensions_cm': [186.34747, 180.89474, 115],
        'ground_z': 0,
        'stalk_count': 64,
        'stalk_grid': [8, 8],
        'stalk_height_range_cm': [70, 115],
        'stem_width_cm': 3,
        'head_width_range_cm': [8, 10],
        'notes': 'Individually grounded, irregularly spaced stalks; three or four broad angular grain courses; sparse angled leaves. No solid field base.',
    },
}


def block(m,pos,size,color,role,plant,bevel=.18):
    m.box(pos,size,color,bevel,variation=.012)
    m.parts[-1]['role']=role
    m.parts[-1]['plant']=plant


def wheat_patch():
    m=Mesh(SPECS['wheat_patch']['name'],2301)
    heads=('c9ae52','d0b359','c2a24a','d5b961')
    stems=('ac9141','b69b47','a78e40')
    for iy in range(8):
        for ix in range(8):
            plant=iy*8+ix
            # 24cm primary spacing leaves room to read individual 8-10cm ears.
            # Row drift and bounded jitter remove ruler-straight field edges.
            x=(ix-3.5)*24+m.rng.uniform(-3.4,3.4)+(1.3 if iy%2 else -1.3)
            y=(iy-3.5)*24+m.rng.uniform(-3.8,3.8)
            height=70+(plant*17)%46
            courses=3 if plant%3==0 else 4
            head_base=height-courses*7-5
            stem_top=head_base+4
            block(m,(x,y,stem_top/2),(3,3,stem_top),stems[plant%3],'grounded_stem',plant,.12)
            for row in range(courses):
                # Nearly contiguous thick kernels form an angular ear, rather
                # than thin grass-like filaments or a cloud of tiny seed cubes.
                taper=[9.2,9.6,8.3,5.5] if courses==4 else [9.6,8.7,5.8]
                width=taper[row]
                offset=.15 if row%2 else -.15
                z=head_base+(row+.5)*7
                block(m,(x+offset,y,z),(width,6.5 if row<courses-1 else 5.5,7.25),
                      heads[(plant+row)%len(heads)],'grain_course',plant,.30)
            block(m,(x,y,height-2.65),(2.2,2.2,5.3),'d4b85d','short_awn',plant,.12)
            # Only sixteen plants receive one broad angled leaf. Endpoints stay
            # inside the native footprint even on its irregular outer fringe.
            if plant%4==1:
                side=-1 if (ix+iy)%2 else 1
                start=(x,y,stem_top*.42)
                end=(max(-95,min(95,x+side*17)),max(-95,min(95,y+(-6 if iy%2 else 6))),stem_top*.42+9)
                m.beam(start,end,5.8,'9b9441' if plant%8==1 else 'aca049',depth=1.7)
                m.parts[-1]['role']='broad_leaf'
                m.parts[-1]['plant']=plant
    m.stalk_count=64
    m.placement_footprint_cm=(200,200)
    m.ground_z=0
    m.refinement_pass=1
    return m


BUILDERS={'wheat_patch':wheat_patch}
