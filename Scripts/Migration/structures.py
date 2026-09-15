"""Reference-led architectural reconstruction of the Godot voxel PNG concepts.

Pure recipe construction is exposed for CPU validation; build_all saves through
the existing, validated Unreal Geometry Script meshkit. Front is negative Y.
"""
import math
import meshkit
from meshkit import Mesh

ROOT = '/Game/Terrarium/Migration'
SPECS = {
    'lodge': {'name': 'SM_Migration_Lodge', 'source': 'lodge.png', 'dimensions_cm': [646, 580.5, 697], 'notes': 'Stepped clay gable, front dormer, stone chimney, teal windows, entry steps.'},
    'civic_hall': {'name': 'SM_Migration_CivicHall', 'source': 'civic_hall.png', 'dimensions_cm': [1126, 725.5, 1257.5], 'notes': 'Two-storey timber hall, central clock and open belfry, golden bell, arched entry.'},
    'market_stall': {'name': 'SM_Migration_MarketStall', 'source': 'market_stall.png', 'dimensions_cm': [556.932, 383.5, 312.5], 'notes': 'Seven teal/cream canopy stripes, paired counters, produce, hanging shop token.'},
    'sign': {'name': 'SM_Migration_Sign', 'source': 'sign.png', 'dimensions_cm': [167, 71.5, 230.5], 'notes': 'Right pointing timber arrow with recessed blank face, iron bands and mossy footing.'},
    'lantern': {'name': 'SM_Migration_Lantern', 'source': 'lantern.png', 'dimensions_cm': [145, 68, 315.5], 'notes': 'Hanging lantern on timber bracket, linked chain, stepped iron cap, amber panes.'},
}

CLAY = ('ad552a', 'b75d2e', 'bf6835', 'a14b24')
STONE = ('858473', '979482', 'aaa48f', '79796b')
WOOD = '624022'
TRIM = '49311b'
CREAM = 'e0cc9f'
TEAL = '087f79'


def block(m, pos, size, color, bevel=1.1):
    m.box(pos, size, color, bevel, variation=.025)


def brick_foundation(m, width, depth, height, cell=40):
    block(m, (0, 0, height / 2), (width-4, depth-4, height), STONE[0], 1.5)
    rows = max(1, round(height / 24))
    dz = height / rows
    nx, ny = max(1, round(width/cell)), max(1, round(depth/cell))
    for row in range(rows):
        z = (row+.5)*dz
        for side in (-1, 1):
            for i in range(nx):
                x = -width/2+(i+.5)*width/nx
                block(m, (x, side*(depth/2-7), z), (width/nx-1.5, 16, dz-1.5), m.rng.choice(STONE))
            for i in range(ny):
                y = -depth/2+(i+.5)*depth/ny
                block(m, (side*(width/2-7), y, z), (16, depth/ny-1.5, dz-1.5), m.rng.choice(STONE))


def window(m, x, y, z, width=75, height=118):
    block(m, (x, y, z), (width, 9, height), '074c4b')
    for xx in (-1, 1):
        for zz in (-1, 1):
            block(m, (x+xx*width*.235, y-5, z+zz*height*.23), (width*.40, 5, height*.41), '08726e')
    block(m, (x, y-9, z), (7, 7, height), TEAL)
    block(m, (x, y-9, z), (width, 7, 8), TEAL)
    for xx in (-1, 1):
        block(m, (x+xx*(width/2+7), y-7, z), (15, 18, height+22), WOOD)
    for zz in (-1, 1):
        block(m, (x, y-11, z+zz*(height/2+9)), (width+36, 25, 18), WOOD)
    block(m, (x, y-20, z-height/2-13), (width+43, 39, 15), '79502a')


def roof_xridge(m, width, depth, eaves, rise, rows=8, origin=(0, 0)):
    """Ridge runs X; individual flat clay blocks produce a stepped slope."""
    ox, oy = origin
    dz = rise/rows
    run = depth/2/rows
    nx = max(2, round(width/44))
    # A solid triangular core ensures roof tiles cannot reveal the interior.
    # Construct the X-aligned prism directly so component metadata is exact.
    v = [(-width/2,-depth/2,0),(-width/2,depth/2,0),(-width/2,0,rise-8),
         (width/2,-depth/2,0),(width/2,depth/2,0),(width/2,0,rise-8)]
    m.solid(v, [[0,2,1],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]], '7e3e22', pos=(ox,oy,eaves-8))
    for side in (-1, 1):
        for row in range(rows):
            y = oy+side*(depth/2-(row+.5)*run)
            z = eaves+(row+.5)*dz
            for i in range(nx):
                x = ox-width/2+(i+.5)*width/nx
                block(m, (x, y, z), (width/nx-.8, run+5, dz+5), m.rng.choice(CLAY), 1.3)
    for i in range(nx):
        block(m, (ox-width/2+(i+.5)*width/nx, oy, eaves+rise+5), (width/nx-.8, run+10, 24), m.rng.choice(CLAY))
    for side in (-1, 1):
        block(m, (ox+side*(width/2-10), oy, eaves+rise+25), (32, 45, 36), TRIM)
        for yy in (-1, 1):
            block(m, (ox+side*(width/2-10), oy+yy*(depth/2-10), eaves-6), (36, 38, 40), TRIM)


def front_gable(m, x, y, base, width, depth, rise, rows=5):
    m.gable((x, y, base), width, depth, rise, CREAM)
    for side in (-1, 1):
        for row in range(rows):
            xx = x+side*(width/2-(row+.5)*width/2/rows)
            z = base+(row+.5)*rise/rows
            block(m, (xx, y-10, z), (width/2/rows+9, depth+40, rise/rows+12), m.rng.choice(CLAY))
            block(m, (xx, y-depth/2-22, z-24), (width/2/rows+3, 19, 26), TRIM)
    block(m, (x, y, base+rise+7), (32, depth+45, 23), CLAY[1])


def steps(m, y, height, width, count):
    for i in range(count):
        h = height*(count-i)/count
        yy = y-i*27
        block(m, (0, yy, h/2), (width, 37, h), STONE[2])
        for side in (-1,1):
            block(m, (side*(width/2+16), yy, h/2+14), (32, 36, h+28), WOOD)


def moss_and_flowers(m, x, y, size=65):
    for i in range(10):
        xx=x+m.rng.uniform(-size/2,size/2); yy=y+m.rng.uniform(-size/3,size/3)
        h=m.rng.choice([14,22,31])
        block(m,(xx,yy,h/2),(22,21,h),m.rng.choice(['687c27','82972f','4d661f']))
    for i in range(3):
        xx=x-16+i*14
        block(m,(xx,y-8,32+i%2*9),(9,9,11),'ead399')
    block(m,(x+17,y+8,40),(13,12,15),'c8712c')


def lodge_mesh():
    m=Mesh(SPECS['lodge']['name'],841)
    brick_foundation(m,570,430,64)
    block(m,(0,0,226),(524,384,324),CREAM,2)
    for x in (-255,255):
        for y in (-200,200): block(m,(x,y,234),(35,33,340),WOOD)
    for y in (-201,201):
        block(m,(0,y,391),(568,36,35),TRIM)
        block(m,(0,y,71),(535,25,21),WOOD)
    # Timber corbels under the roof overhang.
    for x in range(-250,251,62):
        block(m,(x,-218,366),(24,43,28),WOOD)
    roof_xridge(m,630,490,413,203,7)
    # Central forward gable is the source's defining front silhouette.
    block(m,(0,-180,461),(178,74,136),CREAM)
    for x in (-101,101): block(m,(x,-235,466),(29,28,151),WOOD)
    front_gable(m,0,-210,535,248,170,119,4)
    window(m,0,-243,468,60,83)
    for x in (-163,163): window(m,x,-206,220,77,119)
    # Planked door with raised jambs and a gold square latch.
    for x in (-40,-20,0,20,40): block(m,(x,-210,163),(19,21,187),'945222')
    for x in (-64,64): block(m,(x,-224,170),(23,35,211),WOOD)
    block(m,(0,-222,281),(154,35,23),WOOD)
    block(m,(32,-230,161),(16,12,17),'d89620')
    steps(m,-244,64,133,3)
    # Tall stone chimney, offset left and toward the back as in the image.
    for row in range(8):
        for col in (-1,1):
            block(m,(-191+col*19,76,445+row*27),(37,64,26),m.rng.choice(STONE))
    block(m,(-191,76,658),(95,91,30),STONE[2])
    block(m,(-191,76,685),(46,44,24),CLAY[1])
    for x in (-251,251): moss_and_flowers(m,x,-206)
    return m


def civic_hall_mesh():
    m=Mesh(SPECS['civic_hall']['name'],842)
    brick_foundation(m,1080,465,104)
    block(m,(0,0,363),(1024,420,518),CREAM,2)
    for y in (-220,220):
        for x in (-510,-389,-264,-144,144,264,389,510):
            block(m,(x,y,365),(30,31,534),WOOD)
            for z in (338,617): block(m,(x,y-4,z-15),(43,43,45),TRIM)
        for z in (109,349,616): block(m,(0,y,z),(1060,33,28),WOOD)
    for x in (-445,-319,319,445):
        for z in (222,479): window(m,x,-228,z,64,119)
    roof_xridge(m,1110,520,646,190,7)
    # Central front bay and lower projecting gable.
    block(m,(0,-246,455),(290,96,306),CREAM)
    for x in (-153,153): block(m,(x,-297,418),(32,32,399),WOOD)
    block(m,(0,-293,366),(334,31,27),WOOD)
    front_gable(m,0,-268,569,366,182,165,6)
    window(m,0,-301,482,72,111)
    # Clock tower's upper chamber rises clear of the ridge.
    block(m,(0,0,802),(232,224,331),CREAM)
    for x in (-118,118):
        for y in (-115,115): block(m,(x,y,806),(24,25,338),WOOD)
    for z in (704,963): block(m,(0,-119,z),(265,30,28),WOOD)
    # A 16-block teal clock surround and dark hands; geometry is readable at distance.
    for i in range(16):
        a=2*math.pi*i/16
        block(m,(math.sin(a)*70,-136,825+math.cos(a)*70),(18,12,18),TEAL if i%2==0 else WOOD)
    block(m,(0,-144,842),(10,11,49),TRIM)
    block(m,(12,-145,819),(34,11,10),TRIM)
    block(m,(0,-150,825),(15,10,15),'9b6522')
    # Open belfry: four piers and ceiling, with no opaque center block.
    block(m,(0,0,980),(275,272,22),STONE[2])
    for x in (-103,103):
        for y in (-102,102):
            for row in range(4): block(m,(x,y,1004+row*26),(40,40,25),STONE[2])
    block(m,(0,0,1115),(297,292,31),STONE[2])
    # Bell, clapper and short suspension peg inside the chamber.
    m.ellipsoid((0,0,1035),(63,63,72),'c4891c',8,4)
    block(m,(0,0,1074),(12,12,34),TRIM)
    block(m,(0,0,1008),(77,73,13),'d89922')
    block(m,(0,0,994),(12,12,17),WOOD)
    for row in range(4):
        width=230-row*46
        for ix in range(max(1,round(width/35))):
            n=max(1,round(width/35))
            block(m,(-width/2+(ix+.5)*width/n,0,1141+row*24),(width/n-.7,width,25),m.rng.choice(CLAY))
    block(m,(0,0,1236),(44,44,43),TRIM)
    # Door follows a stepped stone arch, rather than a square doorway.
    block(m,(0,-299,210),(117,22,211),'075d59')
    for x in (-39,0,39): block(m,(x,-314,209),(6,7,193),TEAL)
    for z in (166,226,279): block(m,(0,-314,z),(114,8,7),TEAL)
    for x in (-76,76):
        for row in range(6): block(m,(x,-314,121+row*26),(23,31,25),CREAM)
    for side in (-1,1):
        for i in range(4): block(m,(side*(67-i*18),-314,277+i*17),(27,32,25),CREAM)
    block(m,(0,-314,337),(28,33,26),'eee0b6')
    steps(m,-330,104,188,5)
    for x in (-155,155):
        block(m,(x,-321,256),(34,29,50),'eeb53f')
        for xx in (-17,17): block(m,(x+xx,-339,256),(5,7,62),'403a27')
        for z in (226,287): block(m,(x,-326,z),(46,41,9),'403a27')
    for x in (-306,306): moss_and_flowers(m,x,-243,77)
    return m


def market_stall_mesh():
    m=Mesh(SPECS['market_stall']['name'],843)
    brick_foundation(m,490,320,34)
    for i in range(12): block(m,(-220+i*40,0,41),(39,285,14),'98612c')
    for x in (-216,216):
        for y in (-124,124):
            block(m,(x,y,170),(29,29,276),WOOD)
            for z in (55,293): block(m,(x,y,z),(43,43,39),WOOD)
    # Main cloth is seven stripes with a downward slope toward the counter.
    for stripe in range(7):
        x=-210+stripe*70; key=TEAL if stripe%2==0 else 'efd59b'
        for row in range(7):
            y=-146+row*46;z=276+row*5
            block(m,(x,y,z),(69,49,12),key)
        block(m,(x,-168,262),(69,12,26),key)
        block(m,(x,-169,247),(29,12,11),key)
    for y in (-133,133):
        block(m,(0,y,268),(465,28,25),WOOD)
        for x in (-194,194): m.beam((x,y,220),(x*.76,y,266),18,WOOD)
    # Two separately supported counters retain the walk-through center opening.
    for side in (-1,1):
        x=side*142
        for xx in (-76,76): block(m,(x+xx,-96,85),(20,29,92),WOOD)
        for z in (65,90): block(m,(x,-87,z),(161,18,23),'855022')
        for i in range(5): block(m,(x-72+i*36,-84,132),(35,117,17),'9f662e')
        for slot in range(3):
            xx=x-47+slot*46; zz=155+(slot==2)*21
            block(m,(xx,-73,zz),(43,43,27),'aa7232')
            for row in range(2): block(m,(xx,-96,zz-7+row*13),(43,3,10),'7d4b21')
            fruit=['d59f2b','759236','ba5022'][slot]
            for j in range(3): block(m,(xx-11+j*11,-76+(j%2)*12,zz+22+(j%2)*8),(15,15,16),fruit)
        # Open square bin behind the produce.
        for xx in (-30,30): block(m,(x+xx,8,172),(12,69,45),WOOD)
        for yy in (-22,38): block(m,(x,yy,172),(69,12,45),WOOD)
        block(m,(x,8,150),(66,65,7),TRIM)
    # Front cloth and a blue bottle.
    block(m,(-145,-147,107),(37,7,46),TEAL)
    block(m,(-196,-86,157),(20,19,39),'637493')
    block(m,(-196,-86,181),(8,8,14),'a29f8a')
    # Hanging shop token fixed to the right upright.
    block(m,(260,-119,264),(89,18,18),WOOD)
    for x in (267,287): block(m,(x,-119,247),(8,8,35),'9e7436')
    block(m,(277,-119,215),(51,19,47),'9b622b')
    block(m,(277,-133,215),(22,9,23),TEAL)
    steps(m,-177,34,112,2)
    for x in (-220,220): moss_and_flowers(m,x,-145,47)
    return m


def sign_mesh():
    m=Mesh(SPECS['sign']['name'],844)
    for row,w in enumerate((64,50,37)):
        block(m,(0,0,7+row*12),(w,w,14),STONE[row])
    block(m,(0,0,129),(29,28,202),'8f642d')
    for z in (48,111,201):
        block(m,(0,0,z),(36,35,18),'484b40')
        block(m,(0,-21,z),(9,7,9),'7b7e6a')
    block(m,(0,0,224),(34,33,13),'bf9147')
    # Layered open arrow outline around a recessed wooden panel.
    block(m,(27,-24,155),(126,13,49),'725024')
    for z in (126,184): block(m,(22,-31,z),(142,15,12),'bd8b3c')
    block(m,(-43,-32,155),(12,15,63),'ac7a31')
    for side in (-1,1):
        for i in range(4):
            block(m,(84+i*9,-31,155+side*(28-i*8)),(14,16,13),'bd8b3c')
    for z in (143,155,167): block(m,(25,-32,z),(113,2,2),'614521',.2)
    for x,y,z in [(-21,-17,33),(22,8,29),(-17,17,39),(10,-22,42),(-16,-14,213)]:
        block(m,(x,y,z),(14,13,14),'849133')
    return m


def lantern_mesh():
    m=Mesh(SPECS['lantern']['name'],845)
    for row,w in enumerate((68,55,43)):
        block(m,(20,0,8+row*16),(w,w,16),STONE[3-row])
    block(m,(20,0,176),(26,26,265),WOOD)
    for z in (63,139,278):
        block(m,(20,0,z),(34,34,22),'42483f')
        block(m,(20,-20,z),(9,7,10),'6b7165')
    block(m,(-20,0,289),(109,24,26),WOOD)
    block(m,(20,0,307),(35,35,17),TRIM)
    m.beam((20,0,238),(-30,0,281),16,WOOD)
    block(m,(-62,0,288),(17,31,32),'41473f')
    # Two square chain links; empty centers remain visibly open.
    for j in range(2):
        z=267-j*16
        for x in (-68,-56): block(m,(x,0,z),(4,5,17),'42483e')
        for zz in (-8,8): block(m,(-62,0,z+zz),(15,5,4),'42483e')
    for z,w in [(235,28),(227,40),(218,54)]: block(m,(-62,0,z),(w,w,10),'44483d')
    block(m,(-62,0,180),(41,41,65),'eaa32c')
    # Pale centers communicate the source glow without claiming an emissive light.
    block(m,(-62,-21,177),(27,3,39),'ffe2a0')
    block(m,(-84,0,177),(3,27,39),'ffd478')
    for x in (-86,-38):
        for y in (-24,24): block(m,(x,y,180),(7,7,74),'41473d')
    for z in (142,218): block(m,(-62,0,z),(58,58,11),'444b40')
    for x,y,z in [(-5,-17,25),(41,18,34),(29,-23,47),(1,9,46)]:
        block(m,(x,y,z),(16,17,12),'758329')
    return m


BUILDERS = {'lodge': lodge_mesh, 'civic_hall': civic_hall_mesh,
            'market_stall': market_stall_mesh, 'sign': sign_mesh, 'lantern': lantern_mesh}


def build_all():
    """Create new assets only; leave existing migration assets untouched on rerun."""
    old_root=meshkit.ROOT
    records=[]
    try:
        meshkit.ROOT=ROOT
        for source,builder in BUILDERS.items():
            spec=SPECS[source]
            path=ROOT+'/Meshes/'+spec['name']
            exists=meshkit.unreal.EditorAssetLibrary.does_asset_exist(path)
            mesh=meshkit.unreal.load_asset(path) if exists else builder().save()
            assert mesh, path
            records.append({'source':spec['source'], 'name':spec['name'], 'asset':path,
                            'status':'existing' if exists else 'created', 'category':'structures'})
    finally:
        meshkit.ROOT=old_root
    return records
