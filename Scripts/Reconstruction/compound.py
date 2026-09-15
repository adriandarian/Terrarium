"""Independent reconstruction of homestead_compound.png; returns an unsaved mesh."""
import math
from meshkit import Mesh, rotate, add
import architecture as a

SPECS={'homestead_compound':{'name':'SM_Recon_HomesteadCompound','source':'homestead_compound.png',
    'features':'Narrow-front cottage, teal roof shed, fenced kitchen garden, stone lamp tower, standing lantern and flower row; open ground between assets.'}}


def group(m,fn,p=(0,0,0),angle=0):
    a.group(m,fn,p,angle)


def house(m):
    w,d=254,302;bottom,top=45,248
    a.footing(m,w+20,d+20,bottom,25)
    # Narrow entrance elevation, two long-wall window bays, consistent rear.
    a.facade(m,w,bottom,top,-d/2,[],150,door=True)
    a.door(m,-d/2-14,bottom+1,165,91)
    for sx in (-1,1):
        group(m,lambda:a.facade(m,d,bottom,top,0,[-83,83],152,54,91),
              (sx*w/2,0,0),-90 if sx<0 else 90)
    group(m,lambda:a.facade(m,w,bottom,top,0,[-65,65],155,51,91),(0,d/2,0),180)
    for sx in (-1,1):
        for yy in (-d/2,0,d/2):a.timber(m,(sx*(w/2+2),yy,(top+bottom)/2),(25,26,top-bottom+10))
        for zz in (bottom+3,top):a.timber(m,(sx*(w/2+2),0,zz),(27,d+33,23))
    for yy in (-d/2-4,d/2+4):
        for xx in (-w/2,w/2):a.timber(m,(xx,yy,(top+bottom)/2),(28,28,top-bottom+12))
        for zz in (bottom+3,top):a.timber(m,(0,yy,zz),(w+35,28,23))
    # Ridge runs along the long Y axis, in contrast with the independent cottage.
    group(m,lambda:a.tiled_roof(m,374,319,274,138,6),(0,0,0),90)
    for yy,ang in [(-159,0),(159,180)]:
        def end_face():
            m.gable((0,0,253),250,10,135,a.PLASTER[0])
            for row in range(5):
                zz=267+row*22;ww=246*(1-(zz-253)/139)
                if ww>10:a.front_tiles(m,0,-7,zz,ww,21,a.PLASTER,26,21,5)
            a.timber(m,(0,-13,303),(18,17,92))
            for side in (-1,1):m.beam((side*123,-14,253),(0,-14,390),15,'5d4328')
        group(m,end_face,(0,yy,0),ang)
    # Small forward projection on the long right roof, as in the compound source.
    def dormer():
        a.front_tiles(m,0,-180,298,75,52)
        a.window(m,0,-189,299,36,45)
        a.forward_gable(m,-158,325,132,91,62,3)
    group(m,dormer,(0,-31,0),90)
    # Open stone chimney, not the capped chimney of the standalone PNG houses.
    for row in range(4):
        for sx in (-1,1):
            for sy in (-1,1):a.box(m,(-74+sx*12,45+sy*13,377+row*21),(23,25,20),a.STONE[row%5],1.3)
    for sx in (-1,1):a.box(m,(-74+sx*26,45,469),(13,67,16),a.STONE[2],1.1)
    for sy in (-1,1):a.box(m,(-74,45+sy*26,469),(43,13,16),a.STONE[2],1.1)
    a.box(m,(-74,45,452),(37,39,7),'332e21',.8)
    # Wooden entry landing and short steps; stone blocks touch the wall corners.
    for row in range(3):
        z=43-row*12
        for col in range(4):a.box(m,(-54+(col+.5)*27,-186-row*25,z),(26.3,29,16),'9b632d',1.2)
    for sx in (-1,1):
        a.timber(m,(sx*79,-186,37),(24,61,74))
        a.growth(m,sx*107,-151,19,54,False)
        for yy in (-139,137):
            for row in range(3):a.box(m,(sx*129,yy,14+row*20),(42,42,20),a.STONE[(row+2)%5],1.5)
        for yy in (-67,79):a.growth(m,sx*136,yy,8,41,False)
    # Small stacked firewood / storage detail under the side windows.
    for i in range(3):a.timber(m,(145,24+i*24,37),(27,23,59))


def shed(m):
    w,d=154,130
    a.footing(m,w+20,d+18,25,24)
    for y in (-d/2,d/2):
        for col in range(7):a.box(m,(-w/2+(col+.5)*w/7,y,83),(w/7-.7,11,116),a.TIMBER[col%4],1.1)
    for x in (-w/2,w/2):
        for col in range(6):a.box(m,(x,-d/2+(col+.5)*d/6,83),(11,d/6-.7,116),a.TIMBER[(col+1)%4],1.1)
    for x in (-w/2,w/2):
        for y in (-d/2,d/2):a.timber(m,(x,y,84),(17,17,124))
    a.timber(m,(0,-73,140),(167,18,18))
    for xx in (-30,30):a.timber(m,(xx,-76,77),(10,13,87))
    for z in (36,121):a.timber(m,(0,-77,z),(72,13,10))
    a.box(m,(18,-88,78),(7,6,9),'c79838',1)
    # Distinct turquoise block roof: 4 visible courses and a raised center ridge.
    for side in (-1,1):
        for row in range(4):
            for col in range(6):
                a.box(m,(-87+(col+.5)*29,side*(80-(row+.5)*20),148+(row+.5)*13),
                      (28.2,24,17),a.TEAL[(row+col)%4],1.3)
    for col in range(6):a.box(m,(-87+(col+.5)*29,0,205),(28.2,29,20),a.TEAL[col%4],1.3)
    for sx in (-1,1):
        for row in range(4):
            a.box(m,(sx*79,0,145+row*13),(8,141-row*36,13),a.TEAL[row%4],1)
    for col in range(4):a.box(m,(-55+(col+.5)*27.5,-88,25),(26.8,27,13),'896332',1)
    for sx in (-1,1):a.growth(m,sx*66,-60,7,39,False)


def fence(m,start,end):
    dx=end[0]-start[0];dy=end[1]-start[1];length=math.hypot(dx,dy)
    angle=math.degrees(math.atan2(dy,dx))
    n=max(1,round(length/83));step=length/n
    def local():
        for i in range(n+1):
            x=i*step
            a.timber(m,(x,0,49),(15,17,96))
            a.box(m,(x,0,96),(19,21,12),'9d742f',1.2)
        for i in range(n):
            for z in (30,68):a.timber(m,((i+.5)*step,0,z),(step+2,10,13))
    group(m,local,(start[0],start[1],0),angle)


def garden(m):
    w,d=244,199
    # Soil belongs only to the garden bed; the rest of the compound stays open.
    for ix in range(10):
        for iy in range(8):a.box(m,(-w/2+(ix+.5)*w/10,-d/2+(iy+.5)*d/8,9),(w/10-.7,d/8-.7,18),'6d4a28',1)
    for x in (-w/2,w/2):
        for i in range(7):a.timber(m,(x,-d/2+(i+.5)*d/7,25),(11,d/7-.8,26))
    for y in (-d/2,d/2):
        for i in range(8):a.timber(m,(-w/2+(i+.5)*w/8,y,25),(w/8-.8,11,26))
    for x in (-w/2,w/2):
        for y in (-d/2,d/2):a.timber(m,(x,y,29),(18,18,56))
    for ix in range(5):
        for iy in range(4):
            xx=-91+ix*45;yy=-71+iy*46
            a.box(m,(xx,yy,22),(6,6,18),'64712b',.7)
            for k,(dx,dy,z,sz) in enumerate([(-10,0,25,17),(9,-2,25,17),(0,8,30,20),(0,-7,37,17)]):
                a.box(m,(xx+dx,yy+dy,z),(sz,sz*.85,11),['4d6d2c','66873a','789840','5c8034'][k],1.5,rot=(0,0,k*17))
            if (ix+iy)%3==0:a.box(m,(xx+12,yy-8,28),(9,9,12),'bd7930',1)


def small_lantern(m):
    a.box(m,(0,0,12),(41,41,24),a.STONE[1],1.5)
    a.timber(m,(0,0,82),(11,11,127))
    a.iron_band(m,0,40,17,17,15)
    a.box(m,(0,0,140),(25,25,32),'e7b048',1)
    for x in (-15,15):
        for y in (-15,15):a.box(m,(x,y,140),(5,5,40),'46483b',.7)
    for z in (119,161):a.box(m,(0,0,z),(38,38,8),'464a3d',1)
    a.box(m,(0,0,170),(27,27,10),'505142',1)
    a.box(m,(0,0,179),(11,11,12),'555743',1)
    a.box(m,(0,-14,140),(11,3,22),'ffe094',.4)


def tower(m):
    # Stacked dry stone pedestal around a timber beacon with uneven stone cap.
    for row in range(4):
        width=101-row*12
        for ix in range(4):
            for iy in range(4):
                a.box(m,(-width/2+(ix+.5)*width/4,-width/2+(iy+.5)*width/4,12+row*22),
                      (width/4-.8,width/4-.8,24),a.STONE[(ix+iy+row)%5],1.6)
    for x in (-23,23):
        for y in (-23,23):a.timber(m,(x,y,126),(13,13,87))
    for side in (-1,1):
        for row in range(3):a.box(m,(side*26,0,103+row*17),(15,54,15),'836332',1)
    a.box(m,(0,0,154),(43,42,42),'e5a538',1)
    for x in (-24,24):
        for y in (-24,24):a.box(m,(x,y,155),(6,6,51),'57492e',.8)
    for z in (130,180):a.timber(m,(0,0,z),(63,62,12))
    for side in (-1,1):a.box(m,(0,side*24,155),(22,3,29),'ffd779',.5)
    # Irregular jagged grey crest visible in the reference.
    for dx,dy,z,w,h in [(-25,0,191,28,18),(0,0,199,30,25),(24,8,189,27,19),
                         (-18,4,220,18,38),(8,-10,215,21,29),(18,8,239,20,32),(-17,2,253,22,21)]:
        a.box(m,(dx,dy,z),(w,23,h),a.STONE[(int(z)//10)%5],1.3)
    a.box(m,(-30,-15,205),(19,16,11),'a49760',1)
    a.growth(m,-37,-27,5,36,False)


def flower_row(m):
    for i in range(8):
        x=-106+i*30;z=12+(i%3)*3
        a.box(m,(x,0,z),(30,34,24),'46622c',1.8)
        for xx,yy in [(-6,-9),(8,8)]:a.box(m,(x+xx,yy,z+15),(17,17,19),'5d7a2f',1.5)
        if i%2==0:
            a.box(m,(x,0,42),(7,7,42),'6c8130',.8)
            for dx,dz in [(-8,0),(0,8),(8,0),(0,0)]:a.box(m,(x+dx,-1,62+dz),(11,10,12),'c27928',1)
    # Tall sunflower at the row's end, echoing the fence-side source flower.
    a.box(m,(110,3,61),(6,6,102),'607832',.8)
    for i in range(8):
        angle=i*math.pi/4
        a.box(m,(110+math.cos(angle)*13,3,109+math.sin(angle)*13),(11,7,12),'d6942d',1)
    a.box(m,(110,-2,109),(13,8,14),'674626',1)


def build():
    m=Mesh('SM_Recon_HomesteadCompound',1321)
    m.refinement_pass=3
    group(m,lambda:house(m),(-154,100,0),0)
    group(m,lambda:shed(m),(-535,-179,0),0)
    group(m,lambda:garden(m),(153,-234,0),0)
    group(m,lambda:tower(m),(349,34,0),0)
    group(m,lambda:small_lantern(m),(-61,-238,0),0)
    group(m,lambda:flower_row(m),(380,-88,0),0)
    fence(m,(-562,339),(528,339))
    fence(m,(528,339),(528,-420))
    fence(m,(528,-420),(204,-420))
    a.reflect_source_handedness(m)
    # Preserve the source's open foreground access: no enclosure across the shed.
    low=min(v[2] for v in m.vertices)
    if low:
        m.vertices=[(x,y,z-low) for x,y,z in m.vertices]
        for p in m.parts:p['center']=(p['center'][0],p['center'][1],p['center'][2]-low)
    bounds=[[min(v[k] for v in m.vertices),max(v[k] for v in m.vertices)] for k in range(3)]
    spec=SPECS['homestead_compound'];spec['dimensions_cm']=[round(b-a,3) for a,b in bounds]
    spec['bounds_cm']=bounds;spec['triangles']=len(m.triangles)
    spec['source_x_reflected']=True
    return m


BUILDERS={'homestead_compound':build}
