"""Source-specific voxel vegetation, rock, wheat and crossing geometry, in cm."""
import math
from meshkit import Mesh

LEAF=['71842b','819131','607327','899a37','526b2d']
WOOD=['86562c','a36d37','96612f','765030']

def proportions(m,sx,sy,sz=1):
    m.vertices=[(x*sx,y*sy,z*sz) for x,y,z in m.vertices]
    for part in m.parts:
        x,y,z=part['center'];part['center']=(x*sx,y*sy,z*sz)
    return m

def tessbox(m,p,size,cell,palette,bevel=.45):
    n=[max(1,round(v/cell)) for v in size];step=[size[i]/n[i] for i in range(3)]
    for x in range(n[0]):
        for y in range(n[1]):
            for z in range(n[2]):
                if x not in (0,n[0]-1) and y not in (0,n[1]-1) and z not in (0,n[2]-1):continue
                pos=tuple(p[i]-size[i]/2+(q+.5)*step[i] for i,q in enumerate((x,y,z)))
                m.box(pos,tuple(v-.08 for v in step),m.rng.choice(palette) if isinstance(palette,list) else palette,bevel)

def crown(m,p,size,cell=11,vines=False):
    cells=set();radii=[v/2 for v in size]
    for x in range(-math.ceil(radii[0]/cell),math.ceil(radii[0]/cell)+1):
        for y in range(-math.ceil(radii[1]/cell),math.ceil(radii[1]/cell)+1):
            for z in range(-math.ceil(radii[2]/cell),math.ceil(radii[2]/cell)+1):
                if sum(abs(q*cell/radii[i])**3.0 for i,q in enumerate((x,y,z)))<1+ .09*math.sin(x*2+y*3+z):cells.add((x,y,z))
    for x,y,z in sorted(cells):
        if all((x+dx,y+dy,z+dz) in cells for dx,dy,dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]):continue
        key=m.rng.choice(LEAF)
        m.box((p[0]+x*cell,p[1]+y*cell,p[2]+z*cell),(cell,)*3,key,.12)
    # Source-specific projecting bunches break the smooth clipped-ball outline.
    for i in range(17):
        angle=m.rng.uniform(0,math.tau);z=m.rng.uniform(-.32,.38)*size[2]
        x=math.cos(angle)*size[0]*.40;y=math.sin(angle)*size[1]*.40
        chunk=(cell*m.rng.choice([2,3]),cell*m.rng.choice([2,3]),cell*m.rng.choice([2,3]))
        tessbox(m,(p[0]+x,p[1]+y,p[2]+z),chunk,cell,m.rng.choice(LEAF),.12)
    for dx,dy,dz in [(-.16,-.12,.45),(.17,.06,.5),(.02,.2,.38)]:
        tessbox(m,(p[0]+size[0]*dx,p[1]+size[1]*dy,p[2]+size[2]*dz),(cell*2,cell*2,cell*2),cell,m.rng.choice(LEAF),.12)
    if vines:
        for k in range(7):
            x=p[0]+m.rng.uniform(-size[0]*.4,size[0]*.4);y=p[1]+m.rng.uniform(-size[1]*.4,size[1]*.4)
            count=m.rng.randint(3,8)
            for j in range(count):m.box((x,y,p[2]-size[2]*.35-j*cell*.76),(cell*.68,cell*.65,cell*.75),m.rng.choice(LEAF),.35)

def flower(m,p,size=6,orange=False):
    key='dd6c3d' if orange else 'e6dec6'
    for x,y,z in [(0,0,0),(size,0,0),(-size,0,0),(0,0,size),(0,0,-size)]:m.box((p[0]+x,p[1]+y,p[2]+z),(size,)*3,key,.35)

def tree():
    m=Mesh('SM_Recon_AncientTree',703)
    for x,y,s,h in [(-24,0,38,90),(14,13,38,200),(-5,-12,37,310),(34,10,27,142)]:
        tessbox(m,(x,y,h/2),(s,s,h),12,WOOD)
    for x,y in [(-52,-30),(45,-26),(-42,35),(48,28),(-12,-48),(12,48)]:
        tessbox(m,(x,y,12),(36,32,24),12,WOOD)
    branches=[((-18,-5,138),(-148,-10,148)),((12,16,175),(140,22,182)),((-8,1,250),(-122,4,268)),((15,10,286),(116,20,302))]
    for start,end in branches:
        steps=math.ceil(abs(end[0]-start[0])/12)
        for i in range(steps+1):
            t=i/max(steps,1);p=tuple(start[j]+(end[j]-start[j])*t for j in range(3));tessbox(m,p,(24,30,24),12,WOOD)
    for p,size in [((0,2,347),(166,135,143)),((-132,-10,175),(105,88,68)),((135,22,207),(118,88,80)),((-116,6,283),(106,87,82)),((109,18,321),(126,97,78))]:
        crown(m,p,size,12,True)
    for p in [(-54,-50,308),(68,-48,350),(126,-23,219),(-143,-29,167),(-18,-43,64),(36,-37,165)]:
        tessbox(m,p,(23,22,22),11,['678a63','7d9b73','4e795e'])
    for p in [(25,-42,420),(-42,-48,305),(-124,-30,168),(143,-20,245),(40,-35,80)]:flower(m,p,5,True)
    for i in range(32):
        x,y=m.rng.uniform(-53,53),m.rng.uniform(-43,43);m.box((x,y,m.rng.choice([10,22,34])),(12,12,10),m.rng.choice(LEAF),.4)
    for i in range(55):
        z=m.rng.uniform(12,300);x=m.rng.choice([-1,1])*m.rng.uniform(18,35);y=m.rng.uniform(-27,23)
        size=m.rng.choice([18,24,30]);tessbox(m,(x,y,z),(size,size,size*1.4),12,WOOD,.2)
        if i%3==0:tessbox(m,(x,y,z+size*.7),(size,size,12),12,LEAF,.15)
    return proportions(m,1.27,1.22)

def homestead_tree():
    m=Mesh('SM_Recon_HomesteadTree',718)
    root2=math.sqrt(2)
    def xyz(u,v,z):return ((v-u)/root2,(v+u)/root2,z)
    wood=set()
    def limb(points,width=16):
        points=[xyz(*p) for p in points]
        offsets=(-1,0,1) if width==24 else ((0,1) if width==16 else (0,))
        for start,end in zip(points,points[1:]):
            length=math.dist(start,end)
            for i in range(math.ceil(length/4)+1):
                t=i/max(1,math.ceil(length/4));p=[start[j]+(end[j]-start[j])*t for j in range(3)]
                ix,iy,iz=[round(v/8) for v in p]
                for dx in offsets:
                    for dy in offsets:wood.add((ix+dx,iy+dy,iz))
    limb([(0,0,8),(0,0,128),(5,4,192),(1,8,272)],24)
    # Exposed tiered branch forks connect the lower scattered clusters to the stem.
    branch_paths=[
        [(0,0,88),(-24,-2,96),(-24,-2,112),(-72,-3,112),(-72,-3,130)],
        [(0,0,128),(32,1,144),(32,1,160),(91,1,176),(98,1,192)],
        [(0,0,160),(-34,1,176),(-34,1,192),(-89,1,204)],
        [(3,4,193),(39,6,209),(39,6,225),(59,6,246)],
        [(4,5,216),(-34,9,232),(-34,9,248),(-54,9,265)],
        [(0,0,148),(-22,-23,160),(-22,-23,181)],
        [(50,1,165),(74,-5,153),(74,-5,128)],
        [(0,2,185),(16,43,201),(34,48,220)],
    ]
    for points in branch_paths:limb(points)
    for u,v in [(-38,-12),(34,-20),(-28,27),(32,26),(0,-35)]:
        limb([(0,0,24),(u*.5,v*.5,8),(u,v,0)],16)
    bark=['714919','80531e','69451a','785021']
    for ix,iy,iz in sorted(wood):
        if all((ix+a,iy+b,iz+c) in wood for a,b,c in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]):continue
        m.box((ix*8,iy*8,iz*8),(8.025,8.025,8.025),bark[(ix*3+iy+iz//4)%4],.075,variation=.035)
    leaves=['65700c','727a10','58620a','7d8413','4e5909']
    def cluster(u,v,z,size,seed):
        x,y,z=xyz(u,v,z);cell=16;r=[s/2 for s in size]
        for ix in range(-math.ceil(r[0]/cell),math.ceil(r[0]/cell)+1):
            for iy in range(-math.ceil(r[1]/cell),math.ceil(r[1]/cell)+1):
                for iz in range(-math.ceil(r[2]/cell),math.ceil(r[2]/cell)+1):
                    q=sum(abs(a*cell/r[j])**2.7 for j,a in enumerate((ix,iy,iz)))
                    if q>1+.12*math.sin(ix*3+iy*5+iz+seed):continue
                    m.box((x+ix*cell,y+iy*cell,z+iz*cell),(16.03,16.03,16.03),leaves[(ix*3+iy+iz//2+seed)%5],.12,variation=.035)
    # Upper crown remains full, while lower branch tips have separated leafage.
    clusters=[(0,12,288,(102,82,108)),(-54,9,266,(72,60,76)),(59,6,248,(66,56,68)),
              (-91,1,208,(66,54,60)),(98,1,192,(66,48,44)),
              (-72,-3,130,(38,34,42)),(74,-5,118,(42,36,40)),
              (-22,-23,181,(34,30,38)),(34,48,221,(47,43,45)),
              (-45,-15,300,(38,35,42)),(-18,-36,264,(42,35,44)),
              (67,-18,236,(36,34,42)),(-102,-12,194,(34,36,42))]
    for seed,(u,v,z,size) in enumerate(clusters):cluster(u,v,z,size,seed)
    for u,v in [(-39,-12),(37,-20),(-27,28),(33,28),(0,-37)]:
        x,y,z=xyz(u,v,5);m.box((x,y,z),(16,16,12),leaves[int(u)%5],.12)
    m.vertices=[(x*1.1,y*1.1,z) for x,y,z in m.vertices]
    for part in m.parts:
        x,y,z=part['center'];part['center']=(x*1.1,y*1.1,z);part['volume']*=1.21
    m.refinement_pass=5
    m.tree_structure={'trunk_width_cm':26.4,'branch_width_cm':17.6,'leaf_block_cm':17.6,
                      'leaf_clusters':len(clusters),'exposed_branch_paths':len(branch_paths)}
    return m

def shrub():
    m=Mesh('SM_Recon_MeadowShrub',716)
    for p,s in [((-34,6,33),(52,50,63)),((0,12,46),(66,58,87)),((43,7,27),(57,52,51)),((14,-16,16),(72,46,28))]:crown(m,p,s,8)
    for x,y,h in [(-39,-26,33),(-27,-34,28),(37,-30,26),(50,-19,42),(61,12,24)]:m.box((x,y,h/2),(4,4,h),'899627',.3)
    for p in [(-21,-43,19),(3,-46,13),(12,-41,29)]:flower(m,p,4)
    flower(m,(35,-32,32),4,True)
    # Ground-level sparse leaves and roots, not a plinth.
    for i in range(20):m.box((m.rng.uniform(-50,55),m.rng.uniform(-28,30),3.5),(8,8,7),m.rng.choice(LEAF),.3)
    return m

def rock():
    m=Mesh('SM_Recon_MossRock',722)
    # Asymmetric column mass from the specific image; tile-sized stone facets.
    heights=[[18,35,49,36,18],[30,78,114,67,29],[51,96,150,117,45],[31,69,132,86,35],[20,43,62,37,16]]
    for iy,row in enumerate(heights):
        for ix,h in enumerate(row):
            x,y=(ix-2)*26,(iy-2)*24
            palette=['75796c','818172','696e66'] if (ix+iy)%3 else ['4a7168','56786d','3f655e']
            tessbox(m,(x,y,h/2),(26,24,h),12,palette)
            if (ix*5+iy)%4 in (0,1):tessbox(m,(x,y,h+3),(25,23,6),12,['858e4e','768441','94985a'])
    # Broad mound and interrupted ledges, matching the original rock silhouette.
    for x,y,z,s in [(-42,-61,18,27),(17,-58,32,24),(43,-31,53,26),(-36,8,71,23),(9,-22,84,21)]:
        tessbox(m,(x,y,z),(s,s,22),11,['6e746a','7f8477','476e65'],.12)
    m.vertices=[(x*1.25,y*1.25,z*.92) for x,y,z in m.vertices]
    for part in m.parts:
        x,y,z=part['center'];part['center']=(x*1.25,y*1.25,z*.92)
    return m

def wheat():
    m=Mesh('SM_Recon_WheatField',731)
    for ix in range(50):
        for iy in range(32):
            x=(ix-24.5)*5+m.rng.uniform(-.8,.8);y=(iy-15.5)*5+m.rng.uniform(-.8,.8);h=m.rng.uniform(25,47)
            m.box((x,y,2.5),(5,5,5),m.rng.choice(['777d2b','566b28','828b35']),.12)
            m.box((x,y,h*.45),(2.7,2.7,h*.9),m.rng.choice(['b69a32','c6a337','9e832a']),.12)
            for j in range(3):
                z=h-9+j*4;m.box((x+(j%2-.5)*.8,y,z),(3.7,3.7,5),m.rng.choice(['d4b545','c8a43a','e0bf55']),.12)
            m.box((x,y,h+2),(2.5,2.5,6),'d4b64b',.12)
    return m

def riverbank():
    m=Mesh('SM_Recon_Riverbank',750)
    # Source-local palette: dark olive ground, yellow-olive foliage, ochre heads.
    # None of the generic bright green LEAF palette or rectangular clumps is used.
    ground=['5b630b','5e670b','57600a','646b0d','545e09']
    foliage=['454f06','596508','68720a','3c4906','74800d']
    root2=math.sqrt(2)
    def xy(u,v):return ((v-u)/root2,(v+u)/root2)
    def block(u,v,z,size,key):
        x,y=xy(u,v);m.box((x,y,z),size,key,.075,variation=.035)
    cells={}
    for ix in range(-22,23):
        for iy in range(-22,23):
            x,y=ix*6,iy*6;u=(y-x)/root2;v=(x+y)/root2
            edge=(u/112)**2+(v/57)**2
            if edge>1+.045*math.sin(ix*3+iy*2):continue
            cells[ix,iy]=(u,v)
            m.box((x,y,3),(6.03,6.03,6),ground[(ix*3+iy*7)%5],.075,variation=.04)
    # Tapered left bank assembled from small exposed voxels. Its skyline and
    # reverse step down cell by cell instead of enclosing a fabricated big box.
    heights={}
    peaks=[(-74,19,10,10),(-65,25,14,10),(-54,17,12,10),(-66,4,7,12),
           (-47,8,8,11),(-35,18,9,10),(-25,9,6,10),(-42,-6,7,10),(-74,-8,6,9)]
    for (ix,iy),(u,v) in cells.items():
        q=((u+54)/38)**2+((v-9)/29)**2
        n=0
        if q<1:
            n=max(1,int(3*(1-q)))
            for pu,pv,ph,radius in peaks:
                distance=math.hypot(u-pu,v-pv)
                if distance<radius:n=max(n,round(ph*(1-distance/radius)**.3))
        elif v>-24 and abs(u)<100 and (ix*7+iy*11)%5==0:
            n=1+(ix*3+iy*2)%5
        if n:heights[ix,iy]=n
    for (ix,iy),n in heights.items():
        for level in range(n):
            if level<n-1 and all(heights.get((ix+dx,iy+dy),0)>level for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]):continue
            m.box((ix*6,iy*6,9+level*6),(6.03,6.03,6.03),foliage[(ix*2+iy*3)%5],.075,variation=.035)
    # Tall narrow cattails occupy the middle/rear. Keep the foreground apron open.
    reeds=[(-8,24,94),(7,26,82),(18,30,88),(29,26,96),(-24,17,64),
           (45,20,73),(61,29,86),(78,17,73),(94,24,83),(52,1,74),
           (26,-4,49),(20,-7,47),(80,-2,60),(91,-15,47),(62,-16,38),
           (76,-24,34),(44,-22,29),(-10,38,58),(40,37,53),(67,39,49)]
    for i,(u,v,h) in enumerate(reeds):
        block(u,v,6+h/2,(1.65,1.65,h),['465509','53600a','3e5008'][i%3])
        for j in range(3):block(u,v,6+h-8+j*4,(4.1,4.1,4.04),['9b7f07','aa8e08','8f7606'][i%3])
        block(u,v,6+h+3.5,(1.7,1.7,3),'b4980b')
        for side in (-1,1):
            height=h*(.38+.09*((i+side)%3))
            block(u+side*3,v+side*2,6+height/2,(2.3,2.3,height),foliage[(i+side)%5])
    # Sparse short shoots and small gray stones make the extending floor legible.
    for u,v,h in [(-93,-7,18),(-82,-25,14),(-59,-32,17),(-32,-34,20),
                  (-21,-39,12),(12,-37,16),(45,-31,15),(102,-4,18),(105,14,13)]:
        block(u,v,6+h/2,(3.6,3.6,h),foliage[int(h)%5])
    stones=[(-78,-25,6),(-72,-26,5),(-48,-42,6),(-30,-44,6),(3,-29,7),
            (21,-24,5),(33,-37,6),(84,-25,6),(97,-19,7),(89,-9,8),(7,-5,10)]
    for i,(u,v,w) in enumerate(stones):
        block(u,v,6+w/2,(w,w,w),['656962','737771','585d57'][i%3])
    block(7,-5,21,(8,8,10),'686c65')
    m.refinement_pass=6
    m.riverbank_details={'ground_cell_cm':6,'ground_cells':len(cells),'cattails':len(reeds),
        'cattail_stem_cm':1.65,'cattail_head_cm':4.1,'foreground_apron':True,'rectangular_clumps':0}
    return m

def crossing():
    m=Mesh('SM_Recon_RiverCrossing',760)
    # Long narrow plank bridge, two rails, 3 pairs of posts, four stone risers.
    for x in (-51,51):tessbox(m,(x,0,41),(12,280,20),10,WOOD)
    for i in range(27):
        y=-130+i*10;tessbox(m,(0,y,56),(112,9.2,9),9,['987232','ac813a','8e632b'])
        for x in (-44,44):m.box((x,y,61),(3,3,1.2),'6f7061',.2)
    for x in (-59,59):
        for y in (-133,-44,44,133):
            tessbox(m,(x,y,59),(15,17,118),12,WOOD);m.box((x,y,121),(20,21,8),'ae813a',.7)
            for z in (31,92):m.box((x,y,z),(16,18,4),'696b59',.3)
        for z in (89,113):tessbox(m,(x,0,z),(8,267,9),10,WOOD)
    for i in range(4):
        h=63+i*17;y=151+i*29;tessbox(m,(0,y,h/2),(118,29,h),14,['989b82','a7a88d','8d9279'])
        for x in (-50,42):m.box((x,y,h+1.5),(12,20,3),'738041',.3)
    return m

BUILDERS={'tree':tree,'homestead_tree_v2':homestead_tree,'meadow_shrub':shrub,'rock':rock,'wheat_field':wheat,'homestead_riverbank_v2':riverbank,'river_crossing':crossing}
SPECS={k:{'sources':[k+'.png'],'revision':3} for k in BUILDERS}
