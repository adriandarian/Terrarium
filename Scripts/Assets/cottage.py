"""Compact stone-and-timber cottage with individually shaped terracotta tiles."""
from meshkit import Mesh

def build():
    m=Mesh('SM_Cottage',17)
    # Warm irregular masonry plinth and plaster shell.
    for side in [-1,1]:
        for i in range(6):m.box((-175+i*70,side*162,29),(68,52,55),m.rng.choice(['stone','stone_light']),7)
        for i in range(4):m.box((side*192,-110+i*74,29),(48,72,55),'stone',6)
    m.box((0,0,185),(364,294,272),'plaster',10)
    m.gable((0,0,317),364,294,153,'plaster')
    # Timber uprights, sill and lintels front and back.
    for y in [-154,154]:
        for x in [-180,180]:m.box((x,y,187),(21,22,275),'wood',3)
        m.box((0,y,70),(377,22,19),'wood_dark',3)
        m.box((0,y,310),(378,24,22),'wood',3)
        m.beam((-188,y,317),(0,y,476),17,'wood')
        m.beam((0,y,476),(188,y,317),17,'wood')
        m.box((0,y,376),(16,21,108),'wood',2)
    for x in [-186,186]:
        m.box((x,0,308),(20,312,22),'wood',3)
        m.box((x,0,80),(20,312,18),'wood_dark',2)
        m.box((x,8,189),(20,17,231),'wood',2)
    # A recessed dark doorway with six thick original oak planks.
    m.box((-58,-158,153),(96,15,170),'wood_dark',4)
    for i in range(6):m.box((-97+i*15.5,-169,153),(14,13,163),'wood_light',2)
    for x in [-110,-8]:m.box((x,-172,158),(16,23,183),'wood',3)
    m.box((-59,-173,251),(120,27,20),'wood',3)
    for z in [110,210]:m.box((-59,-179,z),(80,8,9),'wood_dark',1)
    m.ellipsoid((-29,-188,158),(9,8,9),'metal',6,3)
    for step in range(2):m.box((-59,-208-step*29,35-step*15),(131+step*14,60,32),'stone_light',5)
    # Shuttered front window and two side windows. The dark panes are modeled.
    for x in [93]:
        m.box((x,-158,203),(72,12,88),'dark',2)
        for xx in [x-43,x+43]:m.box((xx,-170,204),(17,23,104),'wood',2)
        for zz in [153,251]:m.box((x,-170,zz),(98,25,13),'wood_light',2)
        m.box((x,-177,203),(7,9,84),'wood_light',1)
        m.box((x,-177,201),(74,9,7),'wood_light',1)
        for xx in [x-66,x+66]:
            m.box((xx,-168,202),(28,12,81),'teal_dark',3)
            for z in [175,201,228]:m.box((xx,-176,z),(27,6,6),'teal',1)
    for y in [-79,84]:
        m.box((191,y,208),(13,68,78),'dark',2)
        for yy in [y-42,y+42]:m.box((201,yy,208),(21,15,94),'wood',2)
        for zz in [162,253]:m.box((201,y,zz),(21,96,13),'wood_light',2)
        m.box((209,y,208),(8,7,77),'wood_light',1)
        m.box((209,y,208),(8,69,7),'wood_light',1)
        m.box((209,y,155),(37,103,15),'wood',3)
    # Oversized roof, five courses per slope; every tile is a chamfered solid.
    for side in [-1,1]:
        m.box((side*116,0,428),(304,419,21),'roof_dark',4,rot=(0,side*39,0))
        for course in range(5):
            x=side*(27+course*48)
            for tile in range(8):
                y=-187+tile*53+(4 if course%2 else -2)
                z=526-abs(x)*.81+m.rng.uniform(-2,2)
                m.box((x,y,z),(70,56,18),m.rng.choice(['roof','roof','roof_light']),4,rot=(0,side*39,m.rng.uniform(-1.4,1.4)))
    for i in range(9):m.box((0,-200+i*49,535),(42,53,26),m.rng.choice(['roof','roof_light']),7)
    # Stone chimney, dark open throat, four separate cap stones.
    for row in range(5):
        z=433+row*36
        m.box((-105,82,z),(69,61,34),m.rng.choice(['stone','stone_light']),5)
        m.box((-105,49,z+7),(61,5,4),'stone_dark',1)
    m.box((-105,82,604),(47,40,5),'dark',1)
    for x in [-141,-69]:m.box((x,82,616),(20,83,23),'stone_light',4)
    for y in [46,118]:m.box((-105,y,616),(56,20,23),'stone_light',4)
    # Ground contact moss stays small and is part of the cottage asset.
    for x,y in [(-188,-148),(169,-151),(193,118),(-145,158)]:m.ellipsoid((x,y,17),(47,31,19),'moss',6,3)
    return m.save()

if __name__=='__main__':build()
