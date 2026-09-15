"""Reference-placed vegetation groups with open clearings and layered shore plants."""
import math
import reference as ref
from placement import place,place_xyz,rng
from vegetation import ground_at_pixel,occupied as previous_occupied

def occupied(px,py,h):
    if h==560 and 160<px<192 and 367<py<408:return True
    return previous_occupied(px,py,h)

# Pixel-space centers and radii traced from visible reference plant groupings.
GROUPS=[
 (13,23,19,10),(42,50,17,8),(93,64,12,6),(157,37,18,9),(210,32,15,6),
 (245,23,15,8),(359,22,19,8),(405,35,22,12),(458,29,22,12),(24,111,20,12),
 (83,92,11,6),(141,103,15,9),(163,136,14,7),(208,94,15,10),(239,72,11,7),
 (342,71,12,5),(376,95,10,5),(465,190,18,9),(439,209,15,6),
 (9,193,16,10),(42,236,17,11),(90,185,15,8),(112,201,14,6),(138,233,18,11),
 (170,192,15,7),(184,227,15,8),(164,267,16,9),(147,295,12,6),(188,299,12,7),
 (347,266,19,10),(396,275,17,9),(453,283,24,14),(476,323,19,10),
 (14,314,17,10),(34,288,16,8),(80,290,13,8),(93,317,12,7),(166,354,13,8),
 (208,406,12,7),(238,412,10,5),(264,414,12,7),(78,406,18,9),(27,397,18,10),
 (298,421,19,11),(350,407,16,8),(389,388,15,9),(453,363,18,10),
 (128,474,12,8),(111,491,13,8),(202,479,13,9),(226,504,12,7),(285,458,22,12),
 (327,435,22,12),(381,454,24,12),(425,428,23,14),(472,466,19,10),
 (290,516,16,9),(244,536,15,9),(189,534,13,8),(338,505,17,10),(456,501,15,8),
 (26,612,20,12),(69,633,20,11),(117,649,17,10),(162,653,14,8),(197,644,15,8),
 (257,643,20,11),(302,623,15,8),(398,610,19,10),(447,594,23,12),
 (467,648,24,16),(412,679,18,10),(366,706,19,11),(447,735,28,16),
 (331,765,22,13),(289,778,20,10),(397,795,24,13),(36,785,25,12),(116,811,23,12)
]

def build(cells):
    for px,py,s in ref.TREES:
        h=ground_at_pixel(px,py)
        if h is not None:place('OrchardTree_v2',px,py,h+5,s*1.12,rng.uniform(0,360),'Trees')
    for index,(cx,cy,radius,n) in enumerate(GROUPS):
        for k in range(n):
            a=rng.uniform(0,math.tau);r=radius*math.sqrt(rng.random())
            px=cx+math.cos(a)*r;py=cy+math.sin(a)*r*.62
            h=ground_at_pixel(px,py)
            if h is None or occupied(px,py,h):continue
            size=rng.uniform(.7,1.4)*(1.15 if k<2 else 1)
            place('Bush_v2',px,py,h+4,size,rng.uniform(0,360),'ClusteredUnderstory')
            if k%3==0:place('Wildflowers',px+3,py+3,h+5,rng.uniform(.65,1.05),rng.uniform(0,360),'Flowers')
    # Sparse low plants connect groups, without a uniform field of isolated bushes.
    for _ in range(250):
        px=rng.uniform(-30,515);py=rng.uniform(-40,865);h=ground_at_pixel(px,py)
        if h is None or occupied(px,py,h):continue
        place('Bush_v2',px,py,h+3,rng.uniform(.23,.46),rng.uniform(0,360),'LowPlants')
    for px,py,s in [(161,338,1.1),(322,282,.9),(379,487,1.65),(421,515,.8),(95,469,.7),(245,172,.65),(31,198,.7),(450,768,1.1),(183,277,.55),(462,184,.6)]:
        h=ground_at_pixel(px,py)
        if h is not None:place('RockCluster',px,py,h+1,s,rng.uniform(0,360),'FeatureStones')
    # Inspect the actual exposed banks in world XY, then layer shallow stones/reeds.
    for (x,y),h in cells.items():
        if h not in [280,560]:continue
        for dx,dy in [(70,0),(-70,0),(0,70),(0,-70)]:
            if ref.height(x+dx,y+dy) is not None:continue
            px,py=ref.pixel(x+dx,y+dy,0)
            if not (450<py<705) or (246<px<361 and 543<py<621):continue
            if h==280 and rng.random()<.62:
                place_xyz('ShoreOutcrop',(x+dx,y+dy,rng.uniform(-18,24)),rng.uniform(.8,1.25),rng.choice([0,90,180,270]),'BankLedges')
            if rng.random()<.72:
                place_xyz('Reeds',(x+dx,y+dy,0),rng.uniform(.7,1.45),rng.uniform(0,360),'RiverPlants')
            if rng.random()<.4:
                place_xyz('RockCluster',(x+dx,y+dy,-4),rng.uniform(.7,1.6),rng.uniform(0,360),'ShoreStones')
                if rng.random()<.6:place_xyz('Bush_v2',(x+dx,y+dy,13),rng.uniform(.4,.8),rng.uniform(0,360),'ShoreMoss')
