"""A winding approach, stair flight, lower landing, and river crossing."""
from placement import place,segment

UPPER=[(-950,3400),(-830,2500),(-690,2110),(-700,1740),(-920,1350),(-890,1050),(-760,740),(-850,400),(-810,90),(-650,-120),(-300,-245)]
LOWER=[(-300,-650),(-270,-760),(20,-810),(300,-830),(520,-935)]
SOUTH=[(520,-1495),(690,-1620),(640,-1820),(330,-2110),(150,-2450),(250,-3400)]
DOOR=[(-300,-245),(-310,-35),(-160,90)]

def ribbon(points,z,width=1):
    for a,b in zip(points,points[1:]):segment('PathTile',a,b,z,width)
    for u,v in points:place('PathTile',u,v,z,(width,width,1),-135,'Paths')

def build():
    ribbon(UPPER,383,.82)
    ribbon(LOWER,71,.82)
    ribbon(SOUTH,71,.86)
    ribbon(DOOR,383,.68)
    ribbon([(-580,-155),(-525,-45)],383,.60)
    ribbon([(-170,-90),(150,-115),(440,-150)],383,.60)
    place('StoneStairs',-300,-460,60,(1,1,1.253),45,'Paths/Stairs')
    place('PlankBridge',520,-1210,0,1,45,'River/Bridge')
    # Low coping along the plateau, with an opening above the stair flight.
    for a,b in [((-1010,-260),(-460,-260)),((-140,-260),(140,-260)),((270,-260),(900,-60)),((980,100),(980,690)),((-1020,100),(-1020,630))]:
        length=((b[0]-a[0])**2+(b[1]-a[1])**2)**.5
        n=max(1,round(length/200))
        for i in range(n):
            p=(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n)
            q=(a[0]+(b[0]-a[0])*(i+1)/n,a[1]+(b[1]-a[1])*(i+1)/n)
            segment('PerimeterWall',p,q,377,.72,'Walls')
    for a,b in [((-570,-850),(-190,-850)),((10,-1000),(320,-1000)),((820,-900),(820,-660))]:
        segment('PerimeterWall',a,b,64,.72,'Walls/Retaining')
