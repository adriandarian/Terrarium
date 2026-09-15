"""Small reference-scale clustered planting, with clear architectural silhouettes."""
import reference as ref
from placement import place,place_xyz,rng

def ground_at_pixel(px,py):
    for h,poly in ref.PLATES:
        if ref.inside((px,py),poly):
            x,y,_=ref.world(px,py,h)
            if ref.height(x,y)==h:return h
    return None

def occupied(px,py,h):
    if h==880 and ref.inside((px,py),ref.WHEAT):return True
    if h==560:
        if 206<px<310 and 279<py<342:return True
        if 102<px<160 and 326<py<364:return True
        if ref.inside((px,py),ref.GARDEN):return True
    if 150<px<200 and 423<py<479:return True
    return ref.path_distance(px,py,h)<12

def build(cells):
    for px,py,s in ref.TREES:
        h=ground_at_pixel(px,py)
        if h is not None:place('OrchardTree_v2',px,py,h+5,s*1.18,rng.uniform(0,360),'Trees')
    # Dense small plants make the ground read as meadow rather than paving.
    for i in range(1650):
        px=rng.uniform(-60,545);py=rng.uniform(-80,910);h=ground_at_pixel(px,py)
        if h is None or occupied(px,py,h):continue
        s=rng.uniform(.33,.85)
        if rng.random()<.55:
            # Match the original reference's clumps instead of uniform scatter.
            if int(px/35+py/47)%3==0:continue
        place('Bush_v2',px,py,h+5,s*1.18,rng.uniform(0,360),'Meadow')
        if i%5==0:place('Wildflowers',px+3,py+1,h+6,rng.uniform(.35,.65),rng.uniform(0,360),'Flowers')
    for px,py,s in [(91,310,.85),(160,362,.55),(203,385,.90),(258,419,.72),(361,278,.63),(428,285,.93),(311,452,.78),(140,490,.77),(202,573,.9),(452,653,.85)]:
        h=ground_at_pixel(px,py)
        if h is not None:place('Bush_v2',px,py,h+5,s*1.18,rng.uniform(0,360),'FeatureShrubs')
    for i in range(150):
        px=rng.uniform(-10,500);py=rng.uniform(20,850);h=ground_at_pixel(px,py)
        if h is None or occupied(px,py,h):continue
        place('RockCluster',px,py,h+1,rng.uniform(.3,.9),rng.uniform(0,360),'Stones')
    # Reeds are placed immediately outside physical banks, checked in world XY.
    shore=[]
    for (x,y),h in cells.items():
        if h!=280:continue
        for dx,dy in [(72,0),(-72,0),(0,72),(0,-72)]:
            if ref.height(x+dx,y+dy) is None and rng.random()<.42:
                px,py=ref.pixel(x+dx,y+dy,0)
                if 253<px<372 and 541<py<623:continue
                shore.append((x+dx,y+dy))
    for i,(x,y) in enumerate(shore):
        place_xyz('Reeds',(x,y,0),rng.uniform(.43,.9),rng.uniform(0,360),'RiverPlants')
        if i%3==0:place_xyz('RockCluster',(x+12,y-7,-3),rng.uniform(.5,1.15),rng.uniform(0,360),'RiverStones')
