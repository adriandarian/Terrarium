"""Reference-traced terraced land with actual 3D cliffs and irregular shore edges."""
from placement import place_xyz,place,rng
import reference as ref
CELL=90
def build():
    cells={}
    for x in range(-3900,3901,CELL):
        for y in range(-4400,4401,CELL):
            h=ref.height(x,y)
            if h is None:continue
            px,py=ref.pixel(x,y,h)
            if not (-150<px<630 and -150<py<960):continue
            cells[x,y]=h
    for (x,y),h in cells.items():
        exterior=any(cells.get((x+dx,y+dy),-500)<h for dx,dy in [(CELL,0),(-CELL,0),(0,CELL),(0,-CELL)])
        place_xyz('MeadowTile_v4',(x,y,h),(CELL/200*1.02,CELL/200*1.02,1),rng.choice([0,90,180,270]),'Terrain')
        if exterior:
            # The core is hidden by a weathered, moss-capped boundary column.
            neighbor=min(cells.get((x+dx,y+dy),0) for dx,dy in [(CELL,0),(-CELL,0),(0,CELL),(0,-CELL)])
            for bottom in range(h-320,neighbor-320,-320):
                place_xyz('CliffColumn_v2',(x,y,bottom),(CELL/100*1.23,CELL/100*1.23,1),rng.choice([0,90,180,270]),'Terrain')
            if rng.random()<.43:
                dx,dy=rng.choice([(CELL*.53,0),(-CELL*.53,0),(0,CELL*.53),(0,-CELL*.53)])
                place_xyz('Bush_v2',(x+dx,y+dy,h-rng.uniform(10,150)),rng.uniform(.22,.42),rng.uniform(0,360),'CliffMoss')
    for x in range(-3900,3901,300):
        for y in range(-4400,4401,300):
            px,py=ref.pixel(x,y,0)
            if -150<px<650 and 340<py<850:place_xyz('WaterTile_v3',(x,y,0),1,0,'River')
    return cells
