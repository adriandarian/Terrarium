"""Structural terrace revision: recessed lips, broad ledges and stepped banks.

Unlike the previous decorative ledges, this pass lowers selected boundary cells
and exposes a true intermediate walking-height shelf. Landmarks and paths keep
their exact original ground support. reference.height is updated at runtime for
altered cells so downstream planting cannot float over a removed upper lip.
"""
import math
import random
from placement import place_xyz
import reference as ref

CELL=72
ORIGIN=(-3900,-4400)
DIRECTIONS=((CELL,0),(-CELL,0),(0,CELL),(0,-CELL))
CLIFF_HEIGHT=323.5
BASE_HEIGHT=getattr(ref, 'fidelity_base_height', ref.height)
ref.fidelity_base_height=BASE_HEIGHT
EDITS={}
LAST_REPORT={}


def protected(x,y,h,margin=24):
    for level in (280,560,880):
        px,py=ref.pixel(x,y,level)
        if ref.path_distance(px,py,level)<margin:return True
    for px,py,z in ref.BUILDINGS.values():
        a,b,_=ref.world(px,py,z)
        if math.hypot(x-a,y-b)<215:return True
    px,py=ref.pixel(x,y,h)
    if h==880 and ref.inside((px,py),ref.WHEAT):return True
    if h==560 and ref.inside((px,py),ref.GARDEN):return True
    return False


def cell_key(x,y):
    return tuple(origin+round((v-origin)/CELL)*CELL for origin,v in zip(ORIGIN,(x,y)))


def height_at(x,y):
    return EDITS.get(cell_key(x,y),BASE_HEIGHT(x,y))


def sample_cells():
    cells={}
    for x in range(-3900,3901,CELL):
        for y in range(-4400,4401,CELL):
            h=BASE_HEIGHT(x,y)
            if h is None:continue
            px,py=ref.pixel(x,y,h)
            if -150<px<630 and -150<py<960:cells[x,y]=h
    return cells


def edge_info(x,y,h,cells):
    options=[(cells.get((x+dx,y+dy),0),dx,dy) for dx,dy in DIRECTIONS]
    lower,dx,dy=min(options)
    return lower,dx/CELL,dy/CELL


def terrain_specs():
    original=sample_cells()
    cells=dict(original)
    cuts=[]
    lips=[]
    for (x,y),h in original.items():
        lower,dx,dy=edge_info(x,y,h,original)
        if lower>=h-120 or protected(x,y,h):continue
        # Coherent runs several cells wide, not random individual crenellations.
        wave=math.sin(x/275+y/310)+.48*math.sin(x/133-y/231)
        if wave>-.32:
            top=lower+(h-lower)*(.46+.07*math.sin((x+y)/390))
            top=round(top/8)*8
            cells[x,y]=top
            cuts.append((x,y,h,top))
        else:
            offset=round(15*math.sin(x/165+y/209))
            cells[x,y]=h+offset
            lips.append((x,y,h,h+offset))
    shelves=[]
    # Additional 100-220 cm shelves project well beyond a single-grid lip.
    for index,((x,y),h) in enumerate(original.items()):
        lower,dx,dy=edge_info(x,y,h,original)
        if lower>=h-160 or protected(x,y,h):continue
        if math.sin(x/237-y/283)<-.45 or index%3:continue
        width=120+88*(.5+.5*math.sin(x/173+y/227))
        cx,cy=x+dx*width*.40,y+dy*width*.40
        if protected(cx,cy,lower,30):continue
        # Keep the center channel and bridge approaches open.
        px,py=ref.pixel(cx,cy,0)
        if lower==0 and not (-40<px<525 and 460<py<740):continue
        top=lower+(h-lower)*(.30+.17*(.5+.5*math.sin(x/195+y/162)))
        # Check the full footprint, not just its center, against path support.
        if any(protected(cx+ox*width*.48,cy+oy*width*.48,lower,22)
               for ox,oy in ((-1,-1),(-1,1),(1,-1),(1,1))):continue
        shelves.append((cx,cy,top,width,lower))
    return original,cells,cuts,lips,shelves


def rock(x,y,top,bottom,width,rng,group):
    span=top-bottom
    assert span>0
    if width > 100:
        # Broad ledges are groups of ordinary stone columns, never a single
        # column stretched sideways into enormous flat horizontal slabs.
        divisions=max(2,round(width/70))
        step=width/divisions
        for ix in range(divisions):
            for iy in range(divisions):
                cx=x+(ix-(divisions-1)/2)*step
                cy=y+(iy-(divisions-1)/2)*step
                rock(cx,cy,top+rng.uniform(-2,2),bottom,step*1.04,rng,group)
        return
    place_xyz(rng.choice(('CliffColumn_v6A','CliffColumn_v6B','CliffColumn_v6C')),
              (x,y,bottom),(width/84*1.025,width/84*1.025,span/CLIFF_HEIGHT),
              rng.choice((0,90,180,270)),group)


def build():
    rng=random.Random(80519)
    original,cells,cuts,lips,shelves=terrain_specs()
    EDITS.clear()
    EDITS.update({xy:h for xy,h in cells.items() if original[xy]!=h})
    # The existing vegetation ground resolver rejects altered old elevations.
    # New detail can sample height_at directly; no floating old-height plants.
    ref.height=height_at
    for (x,y),h in cells.items():
        lower,dx,dy=edge_info(x,y,h,cells)
        edge=lower<h-10
        place_xyz('MeadowTile_Edge_v6' if edge else 'MeadowTile_v5',(x,y,h),
                  (CELL/200*1.025,CELL/200*1.025,1),rng.choice((0,90,180,270)),'Terrain')
        if not edge:continue
        if h-lower>205 and not protected(x,y,original[x,y]):
            # Broad supporting base projects sideways; narrow top sits within
            # it. This changes the cliff cross-section, not only its texture.
            split=lower+(h-lower)*rng.uniform(.36,.56)
            width=CELL*rng.uniform(1.28,1.75)
            offset=(width-CELL)*.30
            rock(x+dx*offset,y+dy*offset,split,lower-10,width,rng,'SteppedCliffBase')
            rock(x,y,h+5,split-5,CELL,rng,'CliffUpper')
        else:
            rock(x,y,h+5,lower-10,CELL,rng,'Terrain')
    for x,y,top,width,lower in shelves:
        rock(x,y,top,lower-12,width,rng,'BroadRockShelves')
    LAST_REPORT.clear()
    LAST_REPORT.update(cells=len(cells),lowered_boundary_cells=len(cuts),
                       varied_lips=len(lips),broad_shelves=len(shelves),
                       bank_shelves=sum(lower==0 for *_,lower in shelves))
    import water_v7
    water_v7.build(cells)
    return cells
