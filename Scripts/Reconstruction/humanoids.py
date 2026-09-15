"""Detailed voxel sculptures authored against the three original PNGs.

All dimensions are centimetres, -Y is front, +Z up. Each builder returns an
UNSAVED meshkit.Mesh; editor connection, material and saving belong to caller.
No old prototype geometry is used. This is static sculpture, not a rig.
"""
import math
from meshkit import Mesh, rotate, add

SPECS = {
    'player_front': {
        'name': 'SM_Recon_Player',
        'sources': ['player_front.png', 'player_back.png'],
        'height_cm': 160,
        'notes': 'Front/back source-guided detailed voxel sculpture; static.'},
    'ranger_sela': {
        'name': 'SM_Recon_RangerSela',
        'sources': ['ranger_sela.png'],
        'height_cm': 160,
        'notes': 'Source-guided silver bob, long coat, bent hand and satchel; static.'},
}

P = {
    'skin':'dca05c', 'skin_light':'e5ae6d', 'skin_shade':'c88b49',
    'hair':'34342b', 'hair_light':'44433a', 'hair_dark':'292b25',
    'coral':'b8552e', 'coral_light':'c76837', 'coral_dark':'99442a',
    'ochre':'d3a23e', 'ochre_light':'dfb14c', 'ochre_dark':'b98b2e',
    'shirt':'d5caac', 'shirt_light':'e2d8b7', 'shirt_shade':'b8ae91',
    'pants':'393d34', 'pants_light':'45483d', 'pants_dark':'2d332d',
    'boot':'685030', 'boot_light':'81623a', 'boot_dark':'493c29',
    'sole':'a48549', 'pack':'3c552f', 'pack_light':'526c3b', 'pack_dark':'2d452b',
    'teal':'2c5e5c', 'teal_light':'3b7270', 'teal_dark':'224d4b',
    'silver':'b6baae', 'silver_light':'cbd0c2', 'silver_dark':'949d92',
    'sela_skin':'c58e50', 'sela_light':'d49c59', 'sela_shade':'b47b40',
    'cream':'ddd2ac', 'cream_light':'ebe0bb', 'cream_dark':'b9b08e',
    'satchel':'b18430', 'satchel_light':'c29a3c', 'satchel_dark':'947027',
    'brass':'b7a370', 'dark':'292c24', 'white':'f0e5c8',
}


def box(m, p, size, key, bevel=.22, rot=(0,0,0), variation=.015):
    m.box(p,size,P.get(key,key),bevel,rot,variation)


def vox(m, p, size, key, cell=3.2, power=5, rot=(0,0,0),
        predicate=None, palette=None, bevel=.20, seed_bias=0):
    """Shaped solid represented by its exposed closed bevelled voxel cells.

    The occupancy is evaluated BEFORE removing fully buried cells. This keeps
    the visible volume contoured on every side, with actual 3D block thickness.
    Six-neighbour surface cells are closed individually by meshkit.
    """
    # R2 Lit comparison: R1's uniform 3 cm cells read as brickwork. Garments,
    # leather and hair use larger clean blocks; small hands stay articulated.
    if key not in ['skin','skin_light','skin_shade','sela_skin','sela_light','sela_shade']:
        cell*=1.50
    bevel=min(bevel,.07)
    counts=[max(1,round(d/cell)) for d in size]
    steps=[d/n for d,n in zip(size,counts)]
    occupied={}
    for ix in range(counts[0]):
        for iy in range(counts[1]):
            for iz in range(counts[2]):
                q=tuple((v+.5)*step-d/2 for v,step,d in zip((ix,iy,iz),steps,size))
                # Sampling half a cell inward rounds the volume while keeping
                # the intended outer extrema on broad, non-corner regions.
                if sum((abs(v)/(d/2))**power for v,d in zip(q,size))>1:
                    continue
                world=add(rotate(q,rot),p)
                if predicate and not predicate(*q):
                    continue
                occupied[(ix,iy,iz)]=(q,world)
    offsets=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    palette=palette or [key]
    for index,(q,world) in occupied.items():
        if all(tuple(a+b for a,b in zip(index,d)) in occupied for d in offsets):
            continue
        # Deterministic restrained patch shifts, not random multicolor noise.
        ix,iy,iz=index
        k=(ix*17+iy*7+iz*13+seed_bias)%19
        shade=palette[0] if k<14 else palette[(k-14)%len(palette)]
        # Cells contact exactly; the shallow bevel avoids R1's dark brick seams.
        box(m,world,steps,shade,bevel,rot)


def tube(m, a, b, widths, key, cell=3.1, palette=None):
    """Voxel limb; the grid follows the articulated limb's own long axis."""
    d=tuple(y-x for x,y in zip(a,b))
    length=math.sqrt(sum(v*v for v in d))
    yaw=math.degrees(math.atan2(d[1],d[0]))
    pitch=-math.degrees(math.asin(d[2]/length))
    vox(m,tuple((x+y)/2 for x,y in zip(a,b)),(length,widths[0],widths[1]),key,
        cell,5,(0,pitch,yaw),palette=palette)


def ribbon(m, points, width, depth, key, cell=3):
    for a,b in zip(points,points[1:]):
        tube(m,a,b,(depth,width),key,cell)


def boots(m, centers, sela=False):
    """Source: high ankle boots, layered cuffs, thick soles, front straps."""
    for cx,cy,angle in centers:
        def at(x,y,z): return add(rotate((x,y,z),(0,0,angle)),(cx,cy,0))
        def v(p,s,key,cell=3.1,power=5):
            vox(m,at(*p),s,key,cell,power,(0,0,angle))
        v((0,-5,1.6),(18,30,3.2),'boot_dark' if sela else 'sole',3.2)
        v((0,-5,4.6),(18,30,3),'boot_dark' if sela else 'sole',3.2)
        v((0,-6,9),(17,27,9),'boot',3.2,5)
        v((0,1,16),(15,18,16),'boot',3.2,5)
        v((0,1,24),(17,19,6),'boot_light',3.2,5)
        if sela:
            v((0,1,27),(16,18,4),'cream_dark',2.6,5)
        # Tongue and visibly separate toe, ankle and instep straps.
        v((0,-9.1,17),(8,2.5,15),'boot_dark',2.6)
        for z,y,w in [(10,-13.1,9),(16,-10.5,11),(22,-9.6,12)]:
            v((0,y,z),(w,3.5,3),'boot_light',2.6)
        for x in [-6,6]:
            box(m,at(x,-10.5,16),(2,2,2),'brass',.15,(0,0,angle))
        # Small heel block keeps a sensible contact footprint.
        v((0,8,4),(15,10,5),'boot_dark',3.1)


def legs(m, sela=False):
    if sela:
        joints=[((-11,0,70),(-11,1,49),(-12,1,28)),((11,0,70),(13,-1,48),(14,-1,28))]
    else:
        joints=[((-10,0,66),(-14,-1,47),(-16,-1,25)),((10,0,66),(14,3,46),(17,4,25))]
    for hip,knee,ankle in joints:
        tube(m,hip,knee,(16,17),'pants',3.1,['pants','pants_light','pants_dark'])
        tube(m,knee,ankle,(14,15),'pants',3.1,['pants','pants_dark'])
        vox(m,(knee[0],knee[1]-6.3,knee[2]+2),(13,4,10),'pants_light',3)
        vox(m,(ankle[0],ankle[1],ankle[2]+3),(16,17,5),'pants_dark',3)
        # Side cargo seam/patch is anatomical, not a detached giant block.
        side=1 if hip[0]>0 else -1
        vox(m,(hip[0]+side*7,hip[1]+1,hip[2]-8),(3,10,10),'pants_dark',2.7)
    vox(m,(0,1,66 if not sela else 70),(34,24,13),'pants',3.2,5)


def belt(m,z,width=35,y=-14):
    vox(m,(0,y,z),(width,3.3,5),'boot_dark',2.8,7)
    # True framed buckle with visibly open dark center and offset prong.
    for x in [-3.1,3.1]: box(m,(x,y-2,z),(1.3,2,6),'brass',.16)
    for dz in [-2.5,2.5]: box(m,(0,y-2,z+dz),(7.4,2,1.2),'brass',.14)
    box(m,(.5,y-3.1,z),(3.4,.9,.9),'brass',.1)


def hand(m,center,sela=False,raised=False,side=1):
    """Block fingers and distinct thumb; relaxed closed exploration pose."""
    key='sela_skin' if sela else 'skin'
    light='sela_light' if sela else 'skin_light'
    shade='sela_shade' if sela else 'skin_shade'
    cx,cy,cz=center
    if raised:
        vox(m,(cx,cy,cz),(10,8,11),key,2.5,4,palette=[key,light])
        for k in range(4):
            vox(m,(cx-3.6+k*2.4,cy-4.5,cz+.3),(2.2,4,7.5),light,2.4,5)
        vox(m,(cx-side*5,cy-2.5,cz+2.5),(3.5,4,6),shade,2.3,4,rot=(0,0,-side*15))
    else:
        vox(m,(cx,cy,cz+2),(11,10,9),key,2.6,4,palette=[key,light])
        for i in range(4):
            dz=[0,-1,-1.2,.4][i]
            vox(m,(cx-3.8+i*2.5,cy-1.2,cz-3+dz),(2.4,7,6.5),key,2.3,4)
            box(m,(cx-3.8+i*2.5,cy-4.9,cz-2+dz),(1.8,.8,2),light,.14)
        vox(m,(cx-side*6,cy-3,cz+1),(3.7,5,7),shade,2.4,4,rot=(0,side*12,side*12))


def player_arms(m):
    # Source arms splay gently at elbow, then return slightly at wrists.
    for s in [-1,1]:
        a=(s*22,0,99); elbow=(s*29,-1,83); wrist=(s*33,-5,68)
        vox(m,a,(18,22,21),'coral',3.1,4,palette=['coral','coral_light'])
        tube(m,(s*23,0,99),elbow,(19,19),'coral',3.1,['coral','coral_light'])
        tube(m,elbow,wrist,(17,17),'coral',3.1,['coral','coral_dark'])
        tube(m,(s*31.9,-4.3,72),(s*33.7,-5.8,67),(19.5,19.5),'coral_light',3.1)
        tube(m,(s*33.7,-5.8,66),(s*34.3,-6.1,64),(16,16),'coral_dark',3)
        hand(m,(s*34,-6,59.8),side=s)
        if s==-1:
            vox(m,(s*30,-2,96),(2.4,10,5),'shirt',2.5)


def player_torso(m):
    # Open padded jacket: front slab is deliberately cut away over the shirt.
    vox(m,(0,1,86),(40,28,41),'coral',3.1,5,
        predicate=lambda x,y,z: not (y<-8 and abs(x)<10.3),
        palette=['coral','coral_light','coral_dark'])
    vox(m,(0,-12.5,87),(22,5.5,37),'shirt',2.8,7,
        palette=['shirt','shirt_light','shirt_shade'])
    # Quilt-like padded front panels are independently contoured at the hem.
    for s in [-1,1]:
        for z,h,w in [(70,10,11),(82,13,11),(95,12,11),(104,7,10)]:
            vox(m,(s*14,-13.9,z),(w,7,h),'coral',3,5,palette=['coral','coral_light'])
        vox(m,(s*14,-18,91),(11,2.2,6),'ochre',2.8,7)
        vox(m,(s*19,-11,69),(5,8,10),'coral_dark',2.7)
        vox(m,(s*17,-16,73),(8,2,3),'coral_light',2.5)
    belt(m,67,33,-14.7)


def player_backpack(m):
    # player_back.png: deep-green box bag, stepped flap, two lower pockets,
    # ochre clasps over brown straps and a small coral flap tab.
    vox(m,(0,22,89),(38,18,37),'pack',3.1,5,palette=['pack','pack_light','pack_dark'])
    vox(m,(0,24,109),(37,18,8),'pack_light',3,5)
    vox(m,(0,32,103),(38,7,16),'pack',3,5,palette=['pack','pack_light'])
    vox(m,(0,32,110),(34,8,5),'pack_light',3)
    box(m,(0,36.1,104),(4.5,2,7),'coral',.25)
    vox(m,(0,37.3,99),(6.5,2.5,5),'ochre',2.3)
    for s in [-1,1]:
        vox(m,(s*10,32.4,82),(16,7,16),'pack_light',2.8,5,palette=['pack_light','pack'])
        vox(m,(s*10,35.8,84),(4,2,17),'boot',2.8)
        for z in [82,87]: box(m,(s*10,37.5,z),(6,2.2,3),'ochre',.25)
        # Side pockets read in both oblique front and rear inspection.
        vox(m,(s*20,23,85),(6,12,15),'pack_dark',2.8,5)
        # Shoulder straps follow the body in 3D: chest -> shoulder -> bag.
        points=[(s*17,-17,80),(s*18,-17,97),(s*19,-8,105),(s*18,8,109),(s*17,20,103)]
        ribbon(m,points,5,4,'pack',2.6)
        vox(m,(s*17,-20.5,87),(6,2.5,6),'pack_light',2.5)
        for dx in [-2.1,2.1]: box(m,(s*17+dx,-22,85),(1,1.5,5),'brass',.12)
        box(m,(s*17,-22,82.9),(5.2,1.5,1),'brass',.12)


def scarf_ring(m,p,width,depth,height,colors,cell=3):
    """Rounded rectangular cloth loop, open center; layered wrap edge."""
    key,light,shade=colors
    vox(m,p,(width,depth,height),key,cell,5,
        predicate=lambda x,y,z: abs(x)>width*.28 or abs(y)>depth*.25,
        palette=[key,light,shade])


def player_scarf(m):
    scarf_ring(m,(0,0,112),43,34,7,('ochre','ochre_light','ochre_dark'))
    scarf_ring(m,(0,-1,108),41,33,6,('ochre','ochre_light','ochre_dark'))
    vox(m,(0,-18.6,108),(29,7,6),'ochre',3.1,5,palette=['ochre','ochre_light'])
    vox(m,(0,-18.3,103.5),(22,6.5,5),'ochre',3.0,5)
    vox(m,(0,-18,100.5),(12,5,2),'ochre_light',2.8)
    # Front reference's single broad tail sweeps out behind the shoulder and
    # reads beyond the arm silhouette. Back PNG shows a settled animation state;
    # this sculpture now prioritizes the requested front three-quarter pose.
    ribbon(m,[(20,13,107),(29,19,103),(39,23,98),(51,25,96)],9,4,'ochre',3.2)
    for dx,z in [(0,94),(3,92),(-3,91)]:
        tube(m,(49+dx,25,z),(53+dx,26,z-5),(3,3),'ochre',2.5)


def face(m,sela=False):
    skin='sela_skin' if sela else 'skin'
    light='sela_light' if sela else 'skin_light'
    shade='sela_shade' if sela else 'skin_shade'
    width=34 if sela else 37
    # Broad upper head with inset chin tiers approximates the reference's
    # soft block cheeks; original proxy's tiny adult head is not retained.
    vox(m,(0,-.5,133),(width,30,35),skin,5.4,4.5,palette=[skin,light])
    vox(m,(0,-3,119),(width-7,23,9),skin,4.8,5)
    vox(m,(0,0,114),(14,15,11),shade,4.2,5)
    # Clean flat facial plane supports flush eye whites and a small cube nose.
    # R1 layered eyes floated above a rough voxel shell and cast black borders.
    # Larger contiguous skin blocks match the reference's broad cheek quads.
    box(m,(0,-15.5,133),(width-4,3,25),skin,.10)
    for z,h in [(124.5,6),(131,7),(138,7),(144,5)]:
        for x in [-12,-6,0,6,12]:
            box(m,(x,-17.08,z),(6.02,.22,h+.02),skin,.025,variation=.006)
    for s in [-1,1]:
        vox(m,(s*(width/2+.4),0,130),(6,10,12),skin,3.8,4,palette=[skin,light])
        box(m,(s*(width/2+1.7),-3.3,130),(3.2,3.5,7),shade,.12)
        # Raised cheeks frame the eyes and mouth, like source cube planes.
        box(m,(s*13,-16.2,124.2),(7,3,6),light,.16)
    ex=8.1 if sela else 8.6
    ey=-17.4
    for s in [-1,1]:
        # Broad whites, narrow brown/teal pupil; no black frame or protruding
        # multi-layer stack. Features sit within 0.8 cm of the clean face plane.
        box(m,(s*ex,ey,133.8),(7.5,.42,5.6 if sela else 7.4),'white',.07)
        box(m,(s*ex+s*.45,ey-.30,133.4),(3.7,.22,5.1 if sela else 6.7),'337574' if sela else '443b2c',.04)
        box(m,(s*ex+s*.45,ey-.46,133.4),(1.45,.16,3.8 if sela else 4.8),'202820',.03)
        box(m,(s*ex-.8,ey-.57,134.7 if sela else 135.2),(1,.12,1.2 if sela else 1.5),'f3e9cc',.03)
        # Source eyebrows angle gently down toward bridge, separate from fringe.
        box(m,(s*ex,ey-.5,140 if sela else 141),(8.5 if sela else 9.2,1.1,1.7 if sela else 2.3),'hair',.13,(0,-s*8,0))
        if sela: box(m,(s*ex,ey-.38,136.6),(7.8,.35,1.4),'252e23',.06)
    box(m,(0,-18.8,128.1),(3.6,3.7,3.6),skin,.22)
    # Smile is a shallow drawn groove on the face, not a giant dark moustache.
    box(m,(0,-17.4,121.9),(8.2,.30,.75),'8c542b',.05)
    for s in [-1,1]:
        m.beam((s*3.7,-17.4,121.9),(s*5.3,-17.4,123.0),.5,'8c542b',.3)


def player_hair(m):
    # R2: higher, rounded asymmetric cap plus individually placed broad locks.
    # No full rectangular volume covers the forehead or the eyebrows.
    vox(m,(0,2,148),(43,35,15),'hair',3.7,3.2,
        palette=['hair','hair_light','hair_dark'])
    vox(m,(0,3,136),(40,32,26),'hair',3.8,4,
        predicate=lambda x,y,z: y>8 or abs(x)>16,
        palette=['hair','hair_dark'])
    for p,size,key in [
        ((-13,-12,147),(12,10,6),'hair'),
        ((-5,-15,148),(11,8,5),'hair_light'),
        ((4,-15,149),(10,8,6),'hair'),
        ((13,-11,147),(10,10,7),'hair'),
        ((-19,-6,139),(6,10,10),'hair_dark'),
        ((18,-5,137),(6,10,11),'hair'),
        ((-3,-17,143.5),(5,5,5),'hair_dark'),
        ((10,-14,146),(7,7,5),'hair'),
        ((-11,-2,153),(13,15,6),'hair_light'),
        ((1,2,155),(13,13,6),'hair'),
        ((8,4,157.5),(8,9,5),'hair'),
        ((-13,6,155),(7,9,5),'hair_dark'),
        ((14,8,151),(11,12,7),'hair_light'),
        ((-17,11,146),(8,10,8),'hair_dark'),
        ((-7,17,137),(12,5,12),'hair'),
        ((7,17,133),(11,5,12),'hair_dark')]:
        box(m,p,size,key,.22)
    # R3 Lit comparison: fuller tousled silhouette, with unequal raised side
    # and crown clusters replacing the low flat upper edge of R2.
    for p,size,key in [
        ((-15,-2,151),(11,12,7),'hair'),
        ((-10,0,155),(12,11,6),'hair_light'),
        ((-7,4,157),(7,8,6),'hair'),
        ((1,-4,156),(9,12,6),'hair'),
        ((12,-2,153),(10,11,7),'hair_light'),
        ((17,4,148),(9,12,7),'hair'),
        ((-20,3,145),(6,10,7),'hair_dark'),
        ((5,12,153),(10,10,8),'hair'),
        ((-10,13,150),(12,10,8),'hair_light')]:
        box(m,p,size,key,.22)


def sela_hair(m):
    # R3: a round bob assembled from rounded upper mass and independent broad
    # tapered locks. No full square slab covers the temples or the forehead.
    vox(m,(0,2,147),(41,34,22),'silver',3.3,2.5,
        palette=['silver','silver_light','silver_dark'])
    vox(m,(0,4,135),(39,30,30),'silver',3.2,2.6,
        predicate=lambda x,y,z: y>4 or abs(x)>13.5,
        palette=['silver','silver_dark'])
    for s in [-1,1]:
        for x,y,z,size,key in [
            (16,-7,138,(7,10,11),'silver'),
            (17,-8,130,(5,9,10),'silver_dark'),
            (16,-10,124,(4,7,8),'silver'),
            (13,-12,143,(7,8,7),'silver_light'),
            (9,-13,147,(7,8,7),'silver'),
            (4,-11,151,(8,10,6),'silver_light'),
            (17,5,136,(6,10,12),'silver'),
            (13,12,129,(7,7,9),'silver_dark'),
            (7,15,127,(7,5,9),'silver')]:
            box(m,(s*x,y,z),size,key,.20)
    box(m,(-4,2,156),(12,14,8),'silver_light',.23)
    box(m,(7,4,154.5),(10,12,7),'silver',.23)
    box(m,(-12,5,150),(9,12,7),'silver',.23)
    box(m,(0,16,130),(8,5,12),'silver_dark',.20)


def transform_group(m, vertex_start, part_start, fn, volume_scale=1):
    """Transform a newly appended component group and its validation centers."""
    m.vertices[vertex_start:]=[fn(v) for v in m.vertices[vertex_start:]]
    for part in m.parts[part_start:]:
        part['center']=fn(part['center'])
        part['volume']*=abs(volume_scale)


def mirror_x(m):
    """Reflect handed pose while preserving outward winding and part centers."""
    m.vertices=[(-x,y,z) for x,y,z in m.vertices]
    m.triangles=[(a,c,b) for a,b,c in m.triangles]
    for part in m.parts:
        x,y,z=part['center'];part['center']=(-x,y,z)
    return m


def sela_coat(m):
    # Sela's long fitted coat is deliberately a different pattern/pose from
    # the explorer: narrow waist, flared split hem, turned-out lapels.
    vox(m,(0,1,91),(34,27,37),'teal',2.9,5,
        predicate=lambda x,y,z: not (y<-8 and abs(x)<9.5),
        palette=['teal','teal_light','teal_dark'])
    vox(m,(0,-12,89),(21,6,34),'pants_dark',2.8,6)
    # Back skirt widens toward knee, with proper side and rear coverage.
    for z,w in [(72,36),(64,38),(56,40),(48,43)]:
        vox(m,(0,5,z),(w,22,9),'teal',2.9,6,
            predicate=lambda x,y,dz: y>1 or abs(x)>12,
            palette=['teal','teal_light','teal_dark'])
    for s in [-1,1]:
        for z,x,w in [(98,13,9),(88,14,9),(78,14,9),(68,15,10),(58,17,11),(48,18.5,12)]:
            vox(m,(s*x,-11,z),(w,7,11),'teal',2.9,5,palette=['teal','teal_light'])
        # Vertical opening piping and slightly angled lapel folds.
        ribbon(m,[(s*9,-16,76),(s*10,-16,65),(s*12,-16,52),(s*14,-16,44)],2.5,2.2,'teal_light',2.5)
        ribbon(m,[(s*10,-16,89),(s*7,-17,99),(s*15,-12,109)],4,3,'teal_light',2.6)
        vox(m,(s*16,-16,68),(9,2.5,4),'teal_light',2.5,5,rot=(0,s*14,0))
        for z in [80,88,101]: box(m,(s*10.5,-17.4,z),(1.8,1.2,2),'brass',.15)
    # Hem border and central back seam, both visible behind the figure.
    vox(m,(0,16.2,62),(2,2.3,34),'teal_dark',2.5)
    for s in [-1,1]: vox(m,(s*16,4,44),(13,27,4),'teal_dark',2.8)
    belt(m,74,30,-15)
    scarf_ring(m,(0,0,113),36,29,6,('cream','cream_light','cream_dark'),2.8)
    scarf_ring(m,(0,-2,109),36,29,6,('cream','cream_light','cream_dark'),2.8)
    vox(m,(0,-18,108),(25,7,6),'cream',2.8,5,palette=['cream','cream_light'])
    vox(m,(5,-17,96),(8,5,20),'cream',2.8,6,palette=['cream','cream_light'])
    for x in [2,5,8]: vox(m,(x,-17,84),(2.2,4,5),'cream_dark',2.2)
    # Padded raised back collar; scarf remains separately wrapped inside it.
    ribbon(m,[(-18,0,109),(-15,11,114),(0,15,115),(15,11,114),(18,0,109)],5,6,'teal_light',2.9)


def sela_arms(m):
    # Anatomical left arm relaxed, right elbow bends to hand at scarf/strap.
    tube(m,(-20,0,102),(-25,-1,84),(15,17),'teal',2.9,['teal','teal_light'])
    tube(m,(-25,-1,84),(-27,-4,68),(14,15),'teal',2.9,['teal','teal_dark'])
    tube(m,(-26.6,-3.4,72),(-27.4,-4.6,66),(17,18),'teal_light',2.9)
    hand(m,(-27,-4,59),True,False,-1)
    tube(m,(20,0,102),(26,-1,85),(15,17),'teal',2.9,['teal','teal_light'])
    tube(m,(26,-1,85),(17,-17,92),(14,16),'teal',2.9,['teal','teal_light'])
    tube(m,(20,-14,90),(15,-19,94),(16,18),'teal_light',2.7)
    hand(m,(13,-23,96),True,True,1)
    # Upper sleeve square ranger badge, geometric inset motif, cuff studs.
    vox(m,(-27,-7,99),(3,11,12),'brass',2.7,5)
    box(m,(-28.8,-8,101),(1.5,6,2),'teal',.15)
    box(m,(-28.8,-6,98),(1.5,2,4),'teal',.15)
    box(m,(-28.8,-8,95),(1.5,6,2),'teal',.15)
    box(m,(-27,-13.3,69),(2.5,1.5,3),'brass',.18)


def sela_satchel(m):
    # Shoulder strap down to opposite hip, matching source diagonal flow.
    ribbon(m,[(-15,-12,106),(-8,-18,98),(1,-19,86),(13,-18,74),(24,-10,68)],4,2.5,'boot_light',2.7)
    ribbon(m,[(-15,-12,106),(-15,6,109),(-10,16,98),(4,18,83),(24,4,68)],4,2.5,'boot_light',2.7)
    vox(m,(25,-4,64),(17,13,20),'satchel',2.7,5,palette=['satchel','satchel_light','satchel_dark'])
    vox(m,(25,-10.2,69),(18,5,12),'satchel_light',2.7,5)
    vox(m,(25,-12.5,63),(5,2.5,8),'satchel_dark',2.5)
    for x in [22.5,27.5]: box(m,(x,-14,64),(1.3,1.6,5),'cream',.16)
    for z in [61.8,66.2]: box(m,(25,-14,z),(6.3,1.6,1.2),'cream',.16)


def player_front():
    m=Mesh('SM_Recon_Player',9821)
    boots(m,[(-16,-1,-5),(17,4,5)])
    legs(m)
    player_torso(m)
    player_backpack(m)
    player_arms(m)
    player_scarf(m)
    face(m)
    player_hair(m)
    m.source_images=['player_front.png','player_back.png']
    m.refinement_pass=3
    return mirror_x(m)


def ranger_sela():
    m=Mesh('SM_Recon_RangerSela',9822)
    boots(m,[(-12,1,-2),(14,-1,3)],True)
    legs(m,True)
    sela_coat(m)
    sela_satchel(m)
    sela_arms(m)
    # Source Sela is an adult with a smaller head-to-body ratio than explorer.
    # Lengthen the body by 7.7%; shrink the entire head/face/hair group to 82%
    # about its neck. Both operations preserve the 160 cm overall height.
    body_scale=(160-.82*(160-112))/112
    transform_group(m,0,0,lambda v:(v[0],v[1],v[2]*body_scale),body_scale)
    head_vertex=len(m.vertices);head_part=len(m.parts)
    face_vertex=len(m.vertices);face_part=len(m.parts)
    face(m,True)
    # Positive affine taper by individual closed component keeps each little
    # block convex. Lower cheeks/chin are slimmer than the upper temples.
    for part in m.parts[face_part:]:
        z=part['center'][2]
        taper=.78+.22*max(0,min(1,(z-115)/15))
        ids=set(k for tri in m.triangles[part['first']:part['end']] for k in tri)
        for k in ids:
            x,y,vz=m.vertices[k];m.vertices[k]=(x*taper,y,vz)
        x,y,vz=part['center'];part['center']=(x*taper,y,vz)
        part['volume']*=taper
    sela_hair(m)
    transform_group(m,head_vertex,head_part,
        lambda v:(v[0]*.82,v[1]*.82,112*body_scale+(v[2]-112)*.82),.82**3)
    m.source_images=['ranger_sela.png']
    m.refinement_pass=3
    return mirror_x(m)


BUILDERS={'player_front':player_front,'ranger_sela':ranger_sela}
