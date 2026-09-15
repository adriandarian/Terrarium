"""Eleven source-observed, volumetric voxel reconstructions. Front is -Y, units cm.

All BUILDERS return unsaved meshkit.Mesh instances; no editor calls occur here.
Rounded creatures use dense three-dimensional boundary cells, not image planes.
Emblems have solid backing, a modeled rim and separately raised relief geometry.
"""
import math
from meshkit import Mesh


# Opt-in by mesh/source key, never a global near-white material test. These exact
# sRGB colors are reserved for modeled energy cores, not skin, cork or labels.
EMISSIVE_COLORS = {
    'kindlehorn': ['ffd73b', 'ffe66a', 'ffdb43', 'ffc72b'],
    'trail_prism': ['fff1ad', 'ffe681', 'fff4b5', 'fff0a1'],
    'ember': ['ffedc2', 'ffe9b4', 'ffc448'],
    'storm': ['ffe6a1', 'ffe078'],
    'ember_crest': ['ffea83', 'ffe480', 'ffcb32'],
}


SPECS = {
    'brambit': {'name': 'SM_Recon_Brambit', 'source': 'brambit.png', 'dimensions_cm': [105.8, 81.5, 174.485], 'features': ['rounded dense bark body', 'tan face and belly', 'four stump feet', 'moss crown', 'three asymmetric stepped leaf shoots']},
    'kindlehorn': {'name': 'SM_Recon_Kindlehorn', 'source': 'kindlehorn.png', 'dimensions_cm': [107.18, 129.088, 167.356], 'features': ['rounded orange body and broad head', 'two large recessed stepped ears', 'projecting cream muzzle', 'gold crystal horn', 'four charcoal toes', 'stepped tail']},
    'rillip': {'name': 'SM_Recon_Rillip', 'source': 'rillip.png', 'dimensions_cm': [149.245, 78.74, 141.0], 'features': ['dense rounded blue volume', 'separate teal and aqua fin lobes', 'coral cheeks', 'raised U smile', 'two flipper feet', 'small pale-topped crown']},
    'moss_tonic': {'name': 'SM_Recon_MossTonic', 'source': 'moss_tonic.png', 'dimensions_cm': [57.323, 46.4, 89.444], 'features': ['square stepped bottle', 'thick raised glass rim', 'neck and cork', 'blank cream label', 'neck cord', 'hanging veined leaf']},
    'trail_prism': {'name': 'SM_Recon_TrailPrism', 'source': 'trail_prism.png', 'dimensions_cm': [73.0, 77.0, 114.18], 'features': ['bipyramidal stepped gold crystal', 'four-sided brass equatorial cage', 'four corner clamps', 'raised luminous-color inner core']},
    'grove': {'name': 'SM_Recon_Grove', 'source': 'grove.png', 'dimensions_cm': [104.04, 48.08, 104.035], 'features': ['irregular coarse soil and moss mound', 'forked stem', 'layered block relief on both leaf faces', 'projecting pale vein cubes']},
    'ember': {'name': 'SM_Recon_Ember', 'source': 'ember.png', 'dimensions_cm': [91.196, 29.568, 127.098], 'features': ['tall asymmetric stepped flame', 'coral outer cells', 'gold inner flame', 'cream relief core', 'separate spark cubes']},
    'tide': {'name': 'SM_Recon_Tide', 'source': 'tide.png', 'dimensions_cm': [91.196, 29.568, 119.196], 'features': ['curled water droplet', 'real central open hole', 'blue depth', 'aqua front rim', 'stepped high tail']},
    'storm': {'name': 'SM_Recon_Storm', 'source': 'storm.png', 'dimensions_cm': [93.0, 36.5, 136.0], 'features': ['slanted gold lightning silhouette', 'projecting cream lightning face', 'slate voxel clusters', 'floating gold sparks']},
    'ember_crest': {'name': 'SM_Recon_EmberCrest', 'source': 'ember_crest.png', 'dimensions_cm': [112.0, 34.89, 136.5], 'features': ['dark inset bronze reverse with raised stepped rim and four caps', 'stepped patinated brass front rim', 'four red gems', 'recessed charcoal tile field', 'layered crimson orange amber and gold flame relief']},
    'deep_delver_mark': {'name': 'SM_Recon_DeepDelverMark', 'source': 'deep_delver_mark.png', 'dimensions_cm': [108.0, 31.69, 125.02], 'features': ['continuous bronze reverse', 'aged gold rim and six joints', 'recessed charcoal cave', 'teal inward descending terraces', 'diamond-faceted pale crystal motif', 'top and bottom teal jewels']},
}


def cube(m, pos, size, color, bevel=None):
    if isinstance(size, (float, int)):
        size = (size, size, size)
    variation=0 if color in getattr(m,'emissive_colors',()) else .012
    m.box(pos, size, color, min(size)*.015 if bevel is None else bevel, variation=variation)


def new(key):
    m=Mesh(SPECS[key]['name'], 1900 + list(SPECS).index(key))
    m.emissive_colors=tuple(EMISSIVE_COLORS.get(key,()))
    m.refinement_pass=2
    return m


def volume(m, center, radius, cell, palette, power=3.3, color_fn=None):
    """Dense closed boundary cubes of a superellipsoid, covering all six sides.

    Neighbor-culling omits only fully hidden interior cells. Every retained voxel
    is a closed beveled solid. The silhouette is a true 3D stepped volume.
    """
    ranges = [range(-math.ceil(r/cell), math.ceil(r/cell)+1) for r in radius]
    occupied = set()
    for i in ranges[0]:
        for j in ranges[1]:
            for k in ranges[2]:
                if sum(abs(v*cell/r)**power for v, r in zip((i, j, k), radius)) <= 1:
                    occupied.add((i, j, k))
    for i, j, k in sorted(occupied):
        if all((i+a,j+b,k+c) in occupied for a,b,c in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]):
            continue
        pos = tuple(c+v*cell for c,v in zip(center,(i,j,k)))
        key = color_fn(i,j,k,pos) if color_fn else palette[(i*7+j*3+k*11) % len(palette)]
        cube(m, pos, cell*1.035, key)


def filled_volume(m,center,radius,cell,palette,power=3.3):
    """Keep the exact exterior cells, fill their hidden interior with joined runs.

    Only Rillip and Moss Tonic use this repair. Each X run stays inside its
    occupied row of the original superellipsoid lattice, inset from the visible
    skin. Adjacent runs overlap inside the skin, so cracks cannot expose an empty
    shell. This is shaped internal support, not a new outside bounding box.
    """
    volume(m,center,radius,cell,palette,power)
    # Preserve the exterior detail's RNG sequence for subsequent modeled parts.
    rng_state=m.rng.getstate()
    for j in range(-math.ceil(radius[1]/cell),math.ceil(radius[1]/cell)+1):
        for k in range(-math.ceil(radius[2]/cell),math.ceil(radius[2]/cell)+1):
            xs=[i for i in range(-math.ceil(radius[0]/cell),math.ceil(radius[0]/cell)+1)
                if sum(abs(v*cell/r)**power for v,r in zip((i,j,k),radius))<=1]
            if not xs:continue
            left,right=min(xs)*cell-cell*.502,max(xs)*cell+cell*.502
            pos=(center[0]+(left+right)/2,center[1]+j*cell,center[2]+k*cell)
            # 1.004-cell internal courses bridge their neighbors but remain
            # inside the existing 1.035-cell outer surface.
            cube(m,pos,(right-left,cell*1.004,cell*1.004),palette[0],.012)
    m.rng.setstate(rng_state)


def plate_cells(m, center, width, height, cell, colors, depth=3, rounded=True):
    nx, nz = max(1,round(width/cell)), max(1,round(height/cell))
    for i in range(nx):
        for k in range(nz):
            x=(i-(nx-1)/2)*cell;z=(k-(nz-1)/2)*cell
            if rounded and abs(x)/(width/2)+abs(z)/(height/2)>1.62:
                continue
            cube(m,(center[0]+x,center[1],center[2]+z),(cell*1.002,depth,cell*1.002),colors[(i+3*k)%len(colors)])


def clean_plate(m,center,width,height,depth,color,corner=6):
    """One uninterrupted planar face with stepped corners and a solid reverse."""
    w,h=width/2,height/2;c=min(corner,w*.45,h*.45)
    outline=[(-w+c,-h),(w-c,-h),(w-c,-h+c),(w,-h+c),(w,h-c),
             (w-c,h-c),(w-c,h),(-w+c,h),(-w+c,h-c),(-w,h-c),
             (-w,-h+c),(-w+c,-h+c)]
    extrusion(m,[(center[0]+x,center[2]+z) for x,z in outline],center[1]-depth/2,depth,color)


def widen(m,factor):
    m.vertices=[(x*factor,y,z) for x,y,z in m.vertices]
    for part in m.parts:
        x,y,z=part['center'];part['center']=(x*factor,y,z)
        part['volume']*=factor
    return m


def eye(m,x,y,z,width=7,height=11):
    cube(m,(x,y,z),(width,3,height),'15252a',.4)
    cube(m,(x-width*.12,y-1.9,z+height*.25),(width*.52,1.2,height*.38),'fbefcf',.2)


def ground(m):
    low=min(v[2] for v in m.vertices)
    if abs(low)>.000001:
        m.vertices=[(x,y,z-low) for x,y,z in m.vertices]
        for part in m.parts:
            x,y,z=part['center'];part['center']=(x,y,z-low)
    m.source_reconstruction=True
    m.reference_view='front negative Y; back geometry is authored interpretation'
    return m


def leafy_shoot(m,x,y,base,height,width,lean=0):
    step=9
    for k in range(math.ceil(height*.38/step)):
        cube(m,(x+k*lean*.15,y,base+k*step),(7,9,step*1.01),'8b8530')
    start=base+height*.25
    rows=max(3,round(height*.75/step))
    for k in range(rows):
        t=k/(rows-1)
        span=width*(1-abs(t-.37)/.76)
        count=max(1,round(span/step))
        for i in range(count):
            xx=x+(i-(count-1)/2)*step+t*lean
            key='969d34' if abs(xx-x-t*lean)<4.6 else ('7c8929','899331')[(i+k)%2]
            cube(m,(xx,y,start+k*step),(step*1.04,10,step*1.04),key)


def brambit():
    m=new('brambit')
    bark=('995b25','a4682a','ae7030','895423','98602a')
    for x in (-26,26):
        for y in (-22,22):
            plate_cells(m,(x,y,6),16,12,5.3,['303c24'],depth=16,rounded=False)
            plate_cells(m,(x,y,17),16,17,5.3,['9b672d','a37231'],depth=16,rounded=False)
    volume(m,(0,0,62),(43,34,43),8,bark,power=3.65)
    # Broad inset face panel; stepped dark-bark rim remains visible around it.
    clean_plate(m,(0,-33.5,61),68,48,10,'dfb87d',corner=6)
    clean_plate(m,(0,-33.5,36),42,21,10,'c99754',corner=6)
    for x in (-18,18):cube(m,(x,-38,65),(7,2.5,11),'322f20',.3)
    cube(m,(0,-40,59),(10,8,6),'352e1d',.5)
    cube(m,(0,-38.8,46),(17,1,1.8),'bf9252',.08)
    # Bark chips cover flank and back as well as the source-visible face edge.
    for side in (-1,1):
        for y,z,s in [(-19,53,9),(4,71,11),(20,49,8),(-11,32,7),(8,92,8)]:
            cube(m,(side*42,y,z),(8,s,s),bark[(int(z)+side)%len(bark)])
    for x,z in [(-24,45),(21,77),(0,33),(-14,88)]:cube(m,(x,35,z),(9,5,10),'a36b2d')
    volume(m,(0,0,98),(40,32,13),9,['798526','82902a','89922d'],power=3)
    for x,y,z in [(-29,-22,95),(-18,-31,97),(27,-24,96),(36,8,98),(-35,10,98)]:
        cube(m,(x,y,z),(13,13,12),'7d8926')
    leafy_shoot(m,-28,0,107,43,27,-5)
    leafy_shoot(m,0,10,109,66,35,2)
    leafy_shoot(m,31,9,105,39,22,7)
    return ground(widen(m,1.15))


def kindlehorn():
    m=new('kindlehorn')
    orange=('c75816','d46117','cd5a16','b84c12','cf5d18')
    for x in (-25,25):
        for y in (-24,27):
            plate_cells(m,(x,y,5),19,10,6.3,['302a20','3b3022'],depth=25,rounded=False)
            volume(m,(x,y,22),(11,14,16),5,orange,power=4)
    volume(m,(0,8,53),(37,40,40),8,orange,power=3.3)
    # Overlapping fur courses: wide below the muzzle, tapered into the chest.
    for row,(z,span) in enumerate([(61,5),(53,5),(45,5),(37,3),(29,1)]):
        for col in range(span):
            x=(col-(span-1)/2)*7.7
            y=-40+row*1.8+abs(x)*.13-((col+row)%2)*1.2
            cube(m,(x,y,z),(8,13,9),('c19a60','d2ab70','dfbc83','cda36a')[(col+row)%4],.18)
    volume(m,(0,-5,87),(42,35,34),8,orange,power=3.6)
    clean_plate(m,(0,-35,86),69,42,9,'d66522',corner=7)
    for x in (-26,26):
        eye(m,x,-41,86,6,9)
        plate_cells(m,(x,-41,72),24,13,6,['cb5817','d35e19'],depth=5)
    clean_plate(m,(0,-42,70),49,24,15,'ead09b',corner=5)
    cube(m,(0,-51.5,75),(12,6,7),'594022',.45)
    cube(m,(0,-50,64),(7,1.1,1.4),'b89b68',.08)
    # Stepped pointed ears have a deep charcoal inner panel, cream low lobe,
    # orange rim and a fully modeled orange back wall.
    for side in (-1,1):
        ex=side*29
        for row in range(8):
            span=[5,5,5,5,4,3,2,1][row]
            for col in range(span):
                x=ex+(col-(span-1)/2)*7
                z=111+row*7
                for layer,y in enumerate((0,7,14)):
                    rim=col in (0,span-1) or row<1 or row>5
                    color=orange[(col+row)%len(orange)] if layer>0 or rim else '58331b'
                    cube(m,(x,y,z),(7.2,7.2,7.2),color)
        clean_plate(m,(ex,-3.2,124),15,19,5,'e0c18a',corner=4)
    # Rectangular faceted taper atop a strongly projecting golden collar.
    cube(m,(0,-31,116),(23,24,7),'b3650b',.3)
    cube(m,(0,-31,121),(26,26,5),'e99510',.2)
    horn_start=len(m.colors)
    # Broad luminous crystal body and a sharply tapered amber tip.
    for z0,z1,w0,w1,col in [(123,140,22,20,'ffc72b'),(140,144,24,16,'ffb619'),(144,165,15,6,'faaa0b')]:
        vs=[(x*w/2,-31+y*w/2,z) for z,w in [(z0,w0),(z1,w1)] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        m.solid(vs,[[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],col,variation=0)
    horn_end=len(m.colors)
    # Bushy upright tail sweeps to the creature's left, clear of the rump.
    for row,(x,y,z,span) in enumerate([(12,40,35,3),(24,48,43,4),(34,55,51,5),(40,59,59,5),(43,60,67,4),(42,59,75,3),(39,57,83,2),(35,55,91,1)]):
        for col in range(span):
            for layer in range(3):
                xx=-x+(col-(span-1)/2)*7
                yy=y+(layer-1)*7
                palette=('aa330b','c9400c','e4580b','ed7110','ff971b')
                index=min(4,(col+row+layer)%4+(1 if layer==0 and row>2 else 0))
                cube(m,(xx,yy,z),(7.2,7.2,8.2),palette[index],.18)
    for x,y,z in [(41,-3,81),(-41,-6,65),(36,17,51),(-33,27,77)]:cube(m,(x,y,z),(9,9,13),'c85b18')
    m.vertex_alphas=[1.0 if horn_start<=i<horn_end else 0.0 for i in range(len(m.colors))]
    for i in range(horn_start,horn_end):
        m.vertex_alphas[i]=1.0 if m.vertices[i][2]<=140 else .2
    return ground(widen(m,1.15))


def rillip():
    m=new('rillip')
    blue=('4899b5','4b9db9','519fb9','4894b1','529eb8')
    # Body is a rounded box with a smooth change in voxel layer extents,
    # not a triangular pyramid. Most of the front remains broad and readable.
    filled_volume(m,(0,0,65),(44,36,51),8,blue,power=3.35)
    clean_plate(m,(0,-34,62),75,65,11,'529db8',corner=8)
    for x in (-23,23):
        eye(m,x,-40,72,8,14)
        cube(m,(x*1.53,-40,58),(13,5,13),'ee8366',.22)
    # Smile has an open center, raised tips and a broad lower bar.
    cube(m,(0,-40.8,50),(26,3.6,6),'b7ded8',.15)
    for x in (-15,15):cube(m,(x,-40.8,56),(6,3.6,12),'b7ded8',.15)
    for x in (-22,22):
        cube(m,(x,-10,5),(22,34,8),'4a9f9d',.4)
        for xx in (-5.5,5.5):cube(m,(x+xx,-27,5),(10.9,7,8),'8accc0',.2)
    for side in (-1,1):
        filled_volume(m,(side*57,1,56),(17,15,20),7,['19858b','21878b','168185'],power=3.1)
        clean_plate(m,(side*58,-12.6,56),24,28,9,'b0d8c8',corner=5)
        cube(m,(side*69,-13,54),(11,7,10),'b6dbc3',.45)
    # Pale lower rim and sparse authentic surface patches, both sides.
    for x,z in [(-29,31),(-23,26),(-12,21),(0,19),(12,21),(23,26),(29,31)]:
        cube(m,(x,-31,z),(10,4,6),'86c4b2',.3)
    for x,y,z in [(-30,-21,99),(26,-19,103),(-36,0,84),(39,4,84),(22,25,99),(-20,28,101)]:
        cube(m,(x,y,z),(10,7,7),'a9d2c5',.3)
    filled_volume(m,(0,1,113),(20,19,8),5,['1b8192','238d99','338c96'],power=3)
    filled_volume(m,(0,0,123),(11,11,8),5,['4ba799','62baaa'],power=4)
    # Both small crown masses are anchored through the top body course.
    cube(m,(0,1,111),(24,22,16),'3b98aa',.04)
    cube(m,(0,0,125),(13,13,20),'55b2a5',.04)
    cube(m,(0,0,136),(12,12,12),'f1df9e',.4)
    m.refinement_pass=3
    return ground(m)


def moss_tonic():
    m=new('moss_tonic')
    teal=('086459','086d60','147e6d','0b7162','107668')
    filled_volume(m,(0,0,27),(22,19,26),4.2,teal,power=7)
    # Square inset panels, structural corner ribs and bright lower glass caps.
    for side in (-1,1):
        for x in (-20,20):
            for z in range(8,47,5):cube(m,(x,side*20,z),(5,5,5.05),'3caa90')
        for z in (5,48):
            for x in range(-17,18,5):cube(m,(x,side*20,z),(5.05,5,5),'48af92')
    clean_plate(m,(0,-20.9,29),30,30,6,'f4dda3',corner=4)
    for z,w in [(53,34),(57,27),(61,22),(66,22)]:
        filled_volume(m,(0,0,z),(w/2,w/2,3),4.2,teal,power=6)
    # Neck lip and individually tiled cork.
    filled_volume(m,(0,0,70),(18,17,5),4.2,['6fb797','5dac90','7dc39e'],power=5)
    filled_volume(m,(0,0,79),(12,12,9),4,['bc8536','c28b3c','c99443'],power=9)
    # Overlapping inner shoulder/neck courses connect the separate exterior
    # collars. Widths stay inside the existing stepped shoulder and lip.
    for z,width,height in [(51,27,10),(56,22,10),(61,18,12),(67,18,10),(71,21,8)]:
        cube(m,(0,0,z),(width,width,height),'14796a',.025)
    for x in (-12,12):
        for y in range(-10,11,4):cube(m,(x,y,62),(3,4.1,3),'c19343')
    for y in (-12,12):
        for x in range(-10,11,4):cube(m,(x,y,62),(4.1,3,3),'c89a4c')
    # Hanging leaf is a diagonal, thick, stepped blade outside the bottle side.
    for row in range(8):
        count=[2,4,5,6,5,4,3,1][row]
        for col in range(count):
            x=20+(col-(count-1)/2)*3.6+row*1.1
            z=61-row*3.5
            cube(m,(x,-13,z),(3.7,4.7,3.7),'879d39' if col!=count//2 else 'c3c766')
    for x in (16,20):cube(m,(x,-12,63),(4,5,8),'c59748',.6)
    m.refinement_pass=3
    return ground(m)


def trail_prism():
    m=new('trail_prism')
    gold=('e9b929','f2c539','e1ab22','f4cd48')
    # Full 3D bipolar crystal built as 18 stepped rings, each filled in XY.
    for row in range(19):
        z=3+row*6
        width=6+((row/7) if row<7 else (18-row)/11)*49
        width=max(6,width)
        n=max(1,round(width/6))
        for i in range(n):
            for j in range(n):
                # Keep exterior cells; a cream core has solid visible relief.
                if i not in (0,n-1) and j not in (0,n-1):continue
                x=(i-(n-1)/2)*6;y=(j-(n-1)/2)*6
                color=gold[(row+i+j)%len(gold)]
                if j==0 and abs(x)<12 and 6<row<12:color='fff0a1'
                cube(m,(x,y,z),(6.18,6.18,6.18),color,.09)
    volume(m,(0,0,57),(17,17,25),6,['fff1ad','ffe681','fff4b5'],power=1.4)
    # Four continuous cage rails, four stepped corner clamps and gold studs.
    for side in (-1,1):
        cube(m,(0,side*29,45),(59,7,9),'746127',.6)
        cube(m,(side*29,0,45),(7,59,9),'52613b',.6)
    for x in (-29,29):
        for y in (-29,29):
            for z,w in [(34,10),(41,15),(48,15),(55,10)]:cube(m,(x,y,z),(w,w,7.1),'6c602e',.5)
            cube(m,(x,y+(-8 if y<0 else 8),45),(7,3,7),'e8bd33',.4)
    return ground(m)


def grove():
    m=new('grove')
    # Coarse, connected soil columns form an irregular mound rather than a slab.
    soil=('694315','79501b','614018','72501e')
    moss=('6b9a21','78a928','618e20','86b62d')
    footprint={-3:range(-1,2),-2:range(-3,4),-1:range(-4,5),0:range(-4,5),1:range(-3,4),2:range(-2,3)}
    for iy,columns in footprint.items():
        for ix in columns:
            x,y=ix*8,iy*8
            layers=2
            for iz in range(layers):
                key=soil[(ix*3+iy+iz)%4]
                # Moss hangs down over selected soil blocks on both faces.
                if iz==1 and iy in (-3,-2,2) and ix in (-2,1,3):key=moss[(ix+iy)%4]
                cube(m,(x,y,4+iz*8),(8.03,8.03,8.03),key,.16)
            cap=layers*8+4
            cube(m,(x,y,cap),(8.08,8.08,8.08),moss[(ix*3+iy*5)%4],.17)
            if abs(ix)+abs(iy)<3 or (ix,iy) in [(1,-3),(-2,-2),(3,0)]:
                cube(m,(x,y,cap+8),(8.05,8.05,8.05),moss[(ix+iy+1)%4],.17)
    # A two-block-wide stem grows directly out of the raised center of the mound.
    for z in (32,40,48):
        for x in (-4,4):cube(m,(x,0,z),(8.05,12,8.05),('788e29','718626')[x>0],.13)
    rows=[' HGG  ','GGHGG ','GGGHGG',' GGGHG',' GGGGG','  GGG ']
    greens=('559922','4b861e','619f26','42791b','589127')
    highlights=('c2df49','b5d73b','a8ce32','9fc32f')
    for side in (-1,1):
        for x,z in [(12,52),(12,60)]:
            cube(m,(side*x,0,z),(8.03,10.5,8.03),'83982c',.14)
        for row,line in enumerate(rows):
            for col,ch in enumerate(line):
                if ch==' ':continue
                x=side*(48-col*8);z=100-row*8
                # Unequal front and reverse relief: every face contains ledges.
                front=-3-((col*2+row)%3)*1.7
                back=3+((col+row*2+1)%3)*1.7
                cube(m,(x,(front+back)/2,z),(8.04,back-front,8.04),greens[(col+row*3)%5],.14)
                if ch=='H':
                    cube(m,(x,front-2.2,z),(8.03,5.8,8.03),highlights[min(row,3)],.16)
                if (col+row)%3==0 or ch=='H':
                    cube(m,(x,back+1.8,z),(8.03,5.0,8.03),greens[(col+row+2)%5] if ch!='H' else '8eb431',.16)
    m.refinement_pass=6
    return ground(m)


def glyph(m, rows, cell, depth, palette, center=(0,0,0), front_relief=None):
    width=max(map(len,rows));height=len(rows)
    for row,line in enumerate(rows):
        for col,ch in enumerate(line):
            if ch==' ':continue
            x=center[0]+(col-(width-1)/2)*cell
            z=center[2]+(height-1-row)*cell+cell/2
            layers=max(2,round(depth/cell))
            for layer in range(layers):
                y=center[1]+(layer-(layers-1)/2)*depth/layers
                cube(m,(x,y,z),(cell*1.028,depth/layers*1.028,cell*1.028),palette[ch],cell*.016)
            if front_relief and ch in front_relief:
                cube(m,(x,center[1]-depth/2-cell*.09,z),(cell*1.014,cell*.24,cell*1.014),front_relief[ch],cell*.014)


FLAME = [
    '       R       ', '      RR       ', '      RRR      ',
    '     RORR      ', '     ROOR      ', '    RROORR     ',
    '    ROGORR     ', ' R  ROGGORG R  ', ' RR ROGGOGR RR ',
    ' RRRROGCGORRR  ', ' RROOGCCGOORR  ', ' RROGCCCGOORR  ',
    '  ROGCCCGGORR  ', '  RROGCGGOOR   ', '   RROGGOORR   ',
    '    RROOORR    ', '     RRRRR     ',
]

CREST_FLAME = [
    '       G       ', '       G       ', '       GG      ',
    '    R  OG  R   ', '    R  GG  R   ', '   RR GGO  RR  ',
    '   R  GOG   R  ', '  RR GOGOG  RR ', '  R  GGCGG   R ',
    '  R GGCCCGG  R ', '  RR GGC GG RR ', '   R GGGGG  R  ',
    '   RR GGG  RR  ', '    RROGORRR   ', '     RORORR    ',
    '      RORR     ', '       RR      ', '       R       ',
]


def ember():
    m=new('ember')
    glyph(m,FLAME,7,28,{'R':'e36538','O':'f28c25','G':'ffbc39','C':'ffe9b4'},front_relief={'O':'ef8c25','G':'ffc448','C':'ffedc2'})
    for x,y,z,s in [(-40,0,91,5),(32,1,116,4),(-28,2,125,4),(42,0,82,7)]:cube(m,(x,y,z),s,'f8853e')
    return ground(m)


def tide():
    m=new('tide')
    rows=[
        '      A        ', '      AB       ', '     AAB       ',
        '    AABB       ', '   AABBB       ', '  AABBB CCA    ',
        '  ABB AACCCA   ', ' ABB AACBBCAA  ', ' ABB AAB  BCAA ',
        ' ABBBAB    BCA ', ' ABBB      BCA ', ' AABB     BBCA ',
        ' BAABB   BBBCA ', ' BBAABBBBBBCAA ', '  BBAABBBBAAA  ',
        '   BBAAAAAAB   ', '    BBBBBBB    ',
    ]
    glyph(m,rows,7,28,{'A':'43bfca','B':'1886b0','C':'b5e6dd'},front_relief={'A':'59c8ce','C':'c6eee5'})
    return ground(m)


def polygon_area(points):
    return sum(x*z2-x2*z for (x,z),(x2,z2) in zip(points,points[1:]+points[:1]))/2


def extrusion(m,points,front,depth,color):
    """Ear-clip a concave XZ profile into closed triangular prisms."""
    p=list(points)
    if polygon_area(p)<0:p.reverse()
    indices=list(range(len(p)))
    def cross2(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    while len(indices)>2:
        clipped=False
        for n in range(len(indices)):
            ids=(indices[n-1],indices[n],indices[(n+1)%len(indices)])
            a,b,c=[p[j] for j in ids]
            if cross2(a,b,c)<=1e-8:continue
            if any(all(v>=-1e-8 for v in (cross2(a,b,p[j]),cross2(b,c,p[j]),cross2(c,a,p[j]))) for j in indices if j not in ids):continue
            vs=[(x,front,z) for x,z in (a,b,c)]+[(x,front+depth,z) for x,z in (a,b,c)]
            m.solid(vs,[[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]],color,variation=0)
            indices.pop(n);clipped=True;break
        assert clipped,'Invalid profile polygon'


def storm():
    m=new('storm')
    bolt=[(-20,0),(11,58),(-21,58),(-12,78),(-12,87),(-5,87),(-5,101),
          (3,101),(3,114),(11,114),(11,136),(23,136),(23,106),(31,106),
          (31,93),(19,93),(12,74),(38,78)]
    extrusion(m,bolt,-7,20,'edb72d')
    face=[(x*.76-1,z*.90+8) for x,z in bolt]
    extrusion(m,face,-11,5,'ffe6a1')
    # Voxel gold mass supports the continuous faceted bolt; slate crystals wrap
    # the actual back, so the reverse is built and has a different silhouette.
    for x,z,w in [(-12,21,13),(-5,40,17),(1,61,22),(11,81,23),(10,104,18),(15,122,12)]:
        for y in (10,16):cube(m,(x,y,z),(w,6.1,11),'efbb2f',.3)
    for x,z in [(-28,34),(-24,71),(-20,92),(30,51),(35,70),(20,113),(10,22)]:
        for i in range(3):cube(m,(x+(i%2)*5,13+(i//2)*7,z+i*6),(11,11,11),['69747e','58636d','7f8790'][i],.4)
    for x,y,z,s in [(-43,0,77,7),(43,0,40,7),(31,-1,108,5),(-32,0,119,5),(-29,0,21,5),(29,0,15,5)]:cube(m,(x,y,z),s,'ffe078',.3)
    return ground(m)


def in_polygon(x,z,polygon):
    inside=False
    for (a,b),(c,d) in zip(polygon,polygon[1:]+polygon[:1]):
        if (b>z)!=(d>z) and x<(c-a)*(z-b)/(d-b)+a:inside=not inside
    return inside


def badge_back(m,polygon,cell,depth,key,rim_key):
    minx,maxx=min(x for x,z in polygon),max(x for x,z in polygon)
    minz,maxz=min(z for x,z in polygon),max(z for x,z in polygon)
    cells=set()
    for i in range(math.floor(minx/cell),math.ceil(maxx/cell)+1):
        for k in range(math.floor(minz/cell),math.ceil(maxz/cell)+1):
            if in_polygon(i*cell,k*cell,polygon):cells.add((i,k))
    for i,k in sorted(cells):
        rim=any((i+a,k+b) not in cells for a,b in [(1,0),(-1,0),(0,1),(0,-1)])
        cube(m,(i*cell,0,k*cell),(cell*1.006,depth,cell*1.006),key,.22)
        if rim:cube(m,(i*cell,-depth*.56,k*cell),(cell*1.02,depth*.65,cell*1.02),rim_key,.4)
        elif (i+k)%4==0:cube(m,(i*cell,depth*.53,k*cell),(cell*.95,1.5,cell*.95),'324b4a',.2)


def gem(m,x,y,z,w,color):
    cube(m,(x,y+1,z),(w,w*.30,w*1.13),'73521e',.7)
    # A raised truncated pyramid with sloped facets, fully closed back.
    h=w*.40;d=w*.21
    vs=[(-h,0,-h),(h,0,-h),(h,0,h),(-h,0,h),(-h*.60,-d,-h*.60),(h*.60,-d,-h*.60),(h*.60,-d,h*.60),(-h*.60,-d,h*.60)]
    m.solid(vs,[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],color,pos=(x,y-1,z))


def ember_crest():
    m=new('ember_crest')
    m.emissive_colors=()  # Preserve saturated amber/gold under Lit shading.
    bronze_ranges=[]
    def bronze(fn,*args,**kwargs):
        start=len(m.vertices);fn(*args,**kwargs)
        bronze_ranges.append((start,len(m.vertices)))
    # Stepped crest outline follows the source; its reverse is a solid minted
    # body, without shield grips, straps or a patchwork backing.
    half=[(0,0),(7,5),(7,12),(14,12),(14,19),(21,19),(21,26),
          (28,26),(28,33),(35,33),(35,42),(42,42),(42,52),(48,52),
          (48,113),(33,113),(33,120),(20,120),(20,127),(0,127)]
    outline=half+[(-x,z) for x,z in reversed(half[1:-1])]
    inner=[(x*.855,(z-65)*.855+65) for x,z in outline]
    bronze(extrusion,m,outline,3.5,5,'745326')
    extrusion(m,inner,1.5,3,'171c1c')
    # Individual rim segments retain the stepped silhouette and a deep inner
    # edge. Adjacent segments close against each other rather than floating.
    for i in range(len(outline)):
        j=(i+1)%len(outline)
        bronze(extrusion,m,[outline[i],outline[j],inner[j],inner[i]],-10,14,'927032')
    # Source-like gold courses on the rim, with narrow visible joints.
    for iz in range(19):
        for ix in range(-7,8):
            x,z=ix*7.0,iz*7.0+3.5
            if not in_polygon(x,z,outline) or in_polygon(x,z,inner):continue
            bronze(cube,m,(x,-10.6,z),(6.90,2.0,6.90),('a67a2e','9b7129','b18737','896025')[(ix*3+iz*5)%4],.14)
    # Recessed dark tile field: subtle charcoal, soot and warm umber variation.
    for iz in range(2,26):
        for ix in range(-9,10):
            x,z=ix*4.6,iz*4.6
            if not in_polygon(x,z,inner):continue
            front=.15+((ix*3+iz*5)%3)*.18
            palette=('232624','282722','302b22','1b2425','222523','332a20')
            cube(m,(x,(front+3.7)/2,z),(4.48,3.7-front,4.48),palette[(ix*5+iz*7)%6],.065)
    # The flame is modeled one colored block at a time, not a bright flat glyph.
    rows=[
        '       Y       ','       Y       ','   R   YY  R   ',
        '   R  OYO  R   ','  RR  YYO  RR  ','  R   YY R  R  ',
        ' RR  OYOYO  RR ',' R   OOYOO   R ',' R  OYYYYYO  R ',
        ' RR OYYYYYO RR ',' RR OOYOOYO RR ',' RRR OYYYO RRR ',
        '  RRR OYO RRR  ','   RRROOORRR   ','    RROORRR    ',
        '     ROORR     ','      ROR      ','       R       ',
    ]
    palettes={'R':('a91c12','c92614','df3218','bc2112','db2913'),
              'O':('c84a08','df6108','ec850a','b93b07','dc6909'),
              'Y':('ed9f09','eab41a','f7bd17','d68906','f5ae08')}
    for row,line in enumerate(rows):
        for col,ch in enumerate(line):
            if ch==' ':continue
            x=(col-7)*4.7;z=24+(17-row)*4.7
            front={'R':-6.2,'O':-9.2,'Y':-12.0}[ch]+((col*7+row*3)%3)*.55
            color=palettes[ch][(col*3+row*7)%5]
            cube(m,(x,(front+2.2)/2,z),(4.62,2.2-front,4.62),color,.13)
    # Small golden center instead of an overexposed cream disk.
    for x,z in [(0,66.3),(-4.7,61.6),(0,61.6),(4.7,61.6),(0,56.9)]:
        cube(m,(x,-13.1,z),(4.60,4.1,4.60),'f3bf22',.12)
    for x,z in [(0,128),(48,69),(-48,69),(0,10)]:
        bronze(cube,m,(x,-5,z),(16,19,17),'9c702d',.5)
        bronze(cube,m,(x,-15,z),(13.8,2.5,14.8),'b68a38',.35)
        gem(m,x,-18,z,9,'cc2c13')
    # A minted reverse: dark inset face, broad raised bronze rim and four caps.
    # Smooth diffuse rear colors match the approved Delver reverse; the existing
    # front bronze retains its patina mask and all original geometry/materials.
    rear_outer=[(x*.97,(z-65)*.97+65) for x,z in outline]
    rear_inner=[(x*.82,(z-65)*.82+65) for x,z in outline]
    rear_bead=[(x*.94,(z-65)*.94+65) for x,z in outline]
    extrusion(m,rear_inner,8.35,1.15,'6b5428')
    for i in range(len(outline)):
        j=(i+1)%len(outline)
        extrusion(m,[rear_outer[i],rear_outer[j],rear_inner[j],rear_inner[i]],8.35,4.3,'917337')
        extrusion(m,[rear_outer[i],rear_outer[j],rear_bead[j],rear_bead[i]],12.6,1.1,'a0843e')
    for x,z in [(0,128),(48,69),(-48,69),(0,10)]:
        cube(m,(x,10.6,z),(12,6.8,13),'a0843e',.45)
    m.vertex_alphas=[0.0]*len(m.vertices)
    for start,end in bronze_ranges:m.vertex_alphas[start:end]=[1.0]*(end-start)
    m.refinement_pass=8
    return ground(m)


def _deep_delver_mark_r8():
    m=new('deep_delver_mark')
    polygon=[(0,0),(48,28),(48,92),(0,120),(-48,92),(-48,28)]
    # A solid minted bronze reverse, with the cave carved into its front face.
    # No exposed teal checkerboard, shield straps, or picture-frame fittings.
    def bronze_plate(outline,front,back,color):
        n=len(outline)
        vertices=[(x,front,z) for x,z in outline]+[(x,back,z) for x,z in outline]
        faces=[list(range(n)),list(range(n,2*n))]
        faces += [[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
        m.solid(vertices,faces,color,variation=0)
    bronze_plate(polygon,5.8,9,'78612d')
    inner=[(x*.89,(z-60)*.89+60) for x,z in polygon]
    extrusion(m,inner,3.8,2,'102326')
    # Continuous aged-gold rim, charcoal inner lip, and matching rear perimeter.
    for (x,z),(xx,zz) in zip(polygon,polygon[1:]+polygon[:1]):
        m.beam((x,-9,z),(xx,-9,zz),8,'9d8039',depth=8)
        m.beam((x,-13.2,z+1),(xx,-13.2,zz+1),1.0,'c5aa5c',depth=1.0)
        m.beam((x*.875,-6,(z-60)*.875+60),(xx*.875,-6,(zz-60)*.875+60),7,'242e30',depth=7)
        m.beam((x*.96,8.3,(z-60)*.96+60),(xx*.96,8.3,(zz-60)*.96+60),3.0,'917337',depth=3.0)
    # Closed side walls join the rim to the backing; the mark is one solid body.
    for i in range(6):
        j=(i+1)%6
        extrusion(m,[polygon[i],polygon[j],inner[j],inner[i]],-8,13,'685629')

    relief_start=(len(m.vertices),len(m.triangles),len(m.parts))
    # The dark rear wall is tiled only on the recessed front. Each column grows
    # toward the perimeter: the middle stays deep instead of bulging forward.
    for ix in range(-7,8):
        for iz in range(3,20):
            x,z=ix*5.4,iz*5.4
            if not in_polygon(x,z,[(a*.83,(b-60)*.83+60) for a,b in polygon]):continue
            palette=('102b2e','102629','122e31','0c2327','173033')
            front=2.6-((ix*7+iz*3)%3)*.5
            cube(m,(x,(front+5)/2,z),(5.43,5-front,5.43),palette[(ix*3+iz*7)%len(palette)],.035)

    # Tall stepped cliff walls lean around the top of the cavity, in charcoal.
    for side in (-1,1):
        for step in range(8):
            x=36 if step%3 else 33.5
            z=33+step*7.7
            m.box((side*x,-5+(step%3)*1.1,z),(6.8,8,8.0),'263536',.14,rot=(0,0,side*20),variation=.025)
        for x,z in [(30,92),(24,97),(18,102)]:
            cube(m,(side*x,-2,z),(7.3,8,8.2),'203033',.12)

    # Diamond-topped voxel columns follow nested V courses into the recess.
    # Rotating real square columns gives the source's two shaded vertical facets.
    for course in range(5):
        bottom=14+course*9.5
        count=[5,5,4,3,2][course]
        for side in (-1,1):
            for step in range(count):
                x=side*(step+1)*7.4
                z=bottom+step*6.1
                if abs(x)>37:continue
                y=-12+(5-step)*2.2+course*1.2
                height=7.2+(step%2)*1.2
                col=('284b50','1e454a','183e43','15363c','123139')[course]
                if course==0 and step>2:col='304b4e'
                m.box((x,y,z),(5.25,5.25,height),col,.08,rot=(0,0,45),variation=.018)
                # Connect each exposed ledge into the rear metal-supported wall.
                cube(m,(x,(y+6)/2,z-height*.18),(7.4,6-y,height*.70),'132e32',.04)
        if course<4:
            m.box((0,3.0,bottom-6),(5.25,5.25,9.0),'1b4348',.08,rot=(0,0,45),variation=0)
    # Suspended central crystal: one tall peak, flanking crystals, branchlets,
    # then a diminishing vertical trail of teal facets into the dark well.
    for x,z,w,h,y,col in [(0,93,6.3,14,-4,'b3d4cc'),
            (-7,86,6.3,13,-2,'7faeaa'),(7,86,6.3,13,-2,'83b3ad'),
            (0,82,6.4,6.8,-7,'b0d0c7'),(0,75,5.5,6,-3,'376c6d'),
            (-14,78,5.6,6.5,-5,'84bcb7'),(14,78,5.6,6.5,-5,'89beb8'),
            (-7,69,5.4,7.0,-6,'81b3ad'),(7,69,5.4,7.0,-6,'7aafa9'),
            (-11,72,4.5,4.5,-2,'326c6c'),(11,72,4.5,4.5,-2,'326c6c'),
            (0,59,5.4,6,-5,'509693'),(0,49,4.8,5.4,-3,'206166'),
            (0,40,4.5,5,-2,'1c585e'),(0,31,4.2,4.8,-1,'205f63')]:
        m.box((x,y,z),(w,w,h),col,.08,rot=(0,0,45),variation=0)
        cube(m,(x,(y+5)/2,z-h*.16),(w*.65,5-y,h*.60),'193c3f',.04)
    relief_end=(len(m.vertices),len(m.triangles),len(m.parts))
    for x,z in polygon:
        cube(m,(x,-4,z),(12,20,13),'a0843e',.55)
    for z in (3,117):
        cube(m,(0,-13,z),(15,9,18),'927236',.5)
        gem(m,0,-19,z,9,'5aaca5')
    # Subtle inset reverse face in the same bronze family, with a solid rim.
    bronze_plate([(x*.88,(z-60)*.88+60) for x,z in polygon],8.8,9.8,'6b5428')
    m.vertices=[(x,y,z*.94) for x,y,z in m.vertices]
    for part in m.parts:
        x,y,z=part['center'];part['center']=(x,y,z*.94);part['volume']*=.94
    m.refinement_pass=8
    m.delver_relief_range=(relief_start,relief_end)
    return ground(m)


def deep_delver_mark():
    # Retain the accepted R8 frame and reverse byte-for-byte in recipe geometry.
    # Replace only its interior, including the disconnected post arrangement.
    m=_deep_delver_mark_r8()
    (v0,t0,p0),(v1,t1,p1)=m.delver_relief_range
    m.vertices=m.vertices[:v0]+m.vertices[v1:]
    m.colors=m.colors[:v0]+m.colors[v1:]
    m.triangles=m.triangles[:t0]+[tuple(i-(v1-v0) if i>=v1 else i for i in tri) for tri in m.triangles[t1:]]
    tail=m.parts[p1:]
    for part in tail:
        part['first']-=t1-t0;part['end']-=t1-t0
    m.parts=m.parts[:p0]+tail
    m.preserved_frame_vertex_count=len(m.vertices)
    # Landmarks use the original 1254px concept. Convert to the existing 20-degree
    # review camera so stepped courses and crystal placement can be audited.
    s=.1132;sn=math.sin(math.radians(20));cs=math.cos(math.radians(20))
    screen_origin=sn*(-6.045)+cs*62.51
    def point(px,py,y):
        return ((px-627)*s,y,(screen_origin+(627-py)*s-sn*y)/cs)
    def block(px,py,width,height,y,color):
        # Real diamond-footprint prisms. A deeper footprint exposes the source's
        # broad diamond top facets at the existing front camera elevation.
        x,_,top=point(px,py,y);side=width*s/math.sqrt(2);h=height*s/cs
        first=len(m.vertices)
        m.box((x,y,top-h/2),(side,side,h),color,.045,rot=(0,0,45),variation=.012)
        m.vertices[first:]=[(a,y+(b-y)*1.60,c) for a,b,c in m.vertices[first:]]
        m.parts[-1]['volume']*=1.60
    def slab(points,y,depth,color):
        extrusion(m,[(point(x,z,y)[0],point(x,z,y)[2]) for x,z in points],y,depth,color)
    # Subdued, nearly flush rear tiles sit behind the multiple physical courses.
    inner=[(x*.81,(z-60)*.81+60) for x,z in [(0,0),(48,28),(48,92),(0,120),(-48,92),(-48,28)]]
    for ix in range(-9,10):
        for iz in range(3,26):
            x,z=ix*4.1,iz*4.1
            if not in_polygon(x,z,inner):continue
            cube(m,(x,3.7,z),(4.12,3.8,4.12),('14373a','143f42','17484b','103035')[(ix*3+iz*5)%4],.025)
    # The charcoal arch is a continuous stepped wall, not sparse upright posts.
    arch=[(279,418),(480,299),(480,374),(447,395),(447,423),(398,448),
          (398,484),(354,510),(354,554),(315,536),(315,482),(279,503)]
    teal_arch=[(627,283),(785,340),(785,414),(824,449),(856,473),(856,545),
               (820,568),(820,490),(777,465),(741,422),(705,400),(627,358),
               (549,400),(513,422),(477,465),(434,490),(434,568),(398,545),
               (398,473),(430,449),(469,414),(469,340)]
    slab(teal_arch,-3.0,8.2,'28555d')
    for side in (-1,1):
        mirrored=[(627+side*(627-x),z) for x,z in arch]
        slab(mirrored,-10.8,15.8,'354549')
        for px in range(292,486,36):
            for py in range(322,552,38):
                corners=[(px+a,py+b) for a,b in [(-17,-18),(17,-18),(17,18),(-17,18)]]
                if all(in_polygon(a,b,arch) for a,b in corners):
                    slab([(627+side*(627-a),b) for a,b in corners],-10.94,.18,('39494d','35464a','3d4c50')[(px+py)%3])
        for px,py,w,h in [(315,734,68,100),(350,766,68,95),(386,801,68,90),(433,848,68,80)]:
            block(627+side*(627-px),py,w,h,-11.3,'3c5055')
    # Adjoining half-cell steps form nested V courses. Every course descends
    # toward the central well; later courses sit physically behind the outer one.
    courses=[
        (-12.0,[932,914,882,863,812,791,779,674,651,614],['47777d','3f7178','3d6871','4a6066']),
        (-7.0,[858,839,811,758,736,701,634,610,548],['32616a','356971','2d5660','304e57']),
        (-3.6,[780,758,724,651,626,576,552],['2c5962','305f67','31636a','274e58']),
        (-1.0,[704,684,650,598,576,535],['24454e','2b535d','2d5961','253f49']),
    ]
    for course,(y,heights,palette) in enumerate(courses):
        for step,py in enumerate(heights):
            for side in ((1,) if step==0 else (-1,1)):
                px=627+side*35*step
                # Solid stepped risers join each visible course into the cavity.
                # Their darker inset faces close gaps without hiding diamond tops.
                floor=min(py+115,974-abs(px-627)*.57)
                for top in range(int(py+18),int(floor),35):
                    bottom=min(top+35,floor)
                    if bottom-top<2:continue
                    slab([(px-18,top),(px+18,top),(px+18,bottom),(px-18,bottom)],
                         y+1.2,5.5-(y+1.2),('294b54','26434c','203e47','1d3841')[course])
                # Taller adjoining risers close each band instead of leaving
                # disconnected tiny pillars against an empty black backdrop.
                for level in range(1):
                    block(px,py+level*41,70,41,y,palette[(step+level)%len(palette)])
    # Pale peak, paired shoulders, central cube, side branches, then teal trail.
    for px,py,w,h,y,col in [
        (627,303,70,75,-13,'c5dfd7'),
        (578,352,56,91,-11,'9ccac6'),(676,352,56,91,-11,'9ccac6'),
        (627,444,70,46,-14,'bce0d9'),(627,493,59,40,-5,'3a747b'),
        (522,475,60,49,-7,'91c6c1'),(732,475,60,49,-7,'95c9c4'),
        (555,527,47,43,-3,'407e81'),(699,527,47,43,-3,'458589'),
        (575,541,45,40,-9,'84bdb9'),(679,541,45,40,-9,'88c2bd'),
        (627,632,61,43,-8,'5aa5a4'),(627,711,52,36,-5,'347f85'),
        (627,774,48,32,-4,'2a7178'),(627,830,43,28,-3,'235e67')]:
        block(px,py,w,h,y,col)
    m.refinement_pass=12
    m.reference_landmarks='1254px source; continuous nested V courses, charcoal stepped arch and pale diamond-faceted motif'
    return m


BUILDERS={
    'brambit':brambit, 'kindlehorn':kindlehorn, 'rillip':rillip,
    'moss_tonic':moss_tonic, 'trail_prism':trail_prism, 'grove':grove,
    'ember':ember, 'tide':tide, 'storm':storm,
    'ember_crest':ember_crest, 'deep_delver_mark':deep_delver_mark,
}
