"""Individually authored voxel architecture from six source PNG concepts.

Builders return UNSAVED meshkit.Mesh values. All dimensions are centimeters;
front is negative Y, roof ridges run X. No editor mutations occur in this module.
"""
import math
from meshkit import Mesh, add, sub, cross, dot, rotate

CLAY=('b66333','bd6b39','b35c2f','c27340','ab552d')
STONE=('8e907d','9d9e89','a6a48d','848873','969781')
PLASTER=('e2d1a8','decea5','e5d5ae','dfd0aa')
TIMBER=('704b2b','79522f','684726','74502c')
MOSS=('7d8e30','839733','6f8227','617426','93a43a')
TEAL=('087d74','0c897e','117e76','087269')

SPECS={
    'lodge':{'name':'SM_Recon_Lodge','source':'lodge.png','features':'Tall lodge; centered raised dormer and teal window; clay roof; left stone chimney; substantial corner footing moss.'},
    'cottage':{'name':'SM_Recon_Cottage','source':'cottage.png','features':'Compact lower cottage; broad front gable with exposed center timber and no upper window; left chimney.'},
    'civic_hall':{'name':'SM_Recon_CivicHall','source':'civic_hall.png','features':'Two storeys; paired narrow window bays; open belfry, gold bell and clock; stone door arch.'},
    'market_stall':{'name':'SM_Recon_MarketStall','source':'market_stall.png','features':'Seven teal and cream awning stripes; scalloped apron; paired goods counters and recessed central opening.'},
    'lantern':{'name':'SM_Recon_Lantern','source':'lantern.png','features':'Broad amber hanging lamp; iron cage; two chain links; braced timber arm; moss-covered block footing.'},
    'sign':{'name':'SM_Recon_Sign','source':'sign.png','features':'Thick right arrow; recessed blank planks; wood end grain; bolted iron bands; irregular stone and moss mound.'},
}


def box(m,p,s,c,bevel=1.3,rot=(0,0,0)):
    m.box(p,s,c,bevel,rot=rot,variation=.015)


def mesh(name,seed):
    m=Mesh(SPECS[name]['name'],seed)
    m.refinement_pass=4
    return m


def group(m,func,origin=(0,0,0),angle=0):
    """Place a helper's front-facing local geometry, including validation metadata."""
    a=len(m.vertices); p=len(m.parts)
    func()
    for i in range(a,len(m.vertices)):
        m.vertices[i]=add(rotate(m.vertices[i],(0,0,angle)),origin)
    for part in m.parts[p:]:
        part['center']=add(rotate(part['center'],(0,0,angle)),origin)


def front_tiles(m,x,y,z,width,height,palette=PLASTER,cw=36,ch=22,depth=9):
    # Source plaster reads as smooth ivory infill, not exposed brickwork.
    plaster=palette==PLASTER
    if plaster:
        cw=max(cw,72);ch=max(ch,43)
        box(m,(x,y+.5,z),(width,depth,height),PLASTER[0],.12)
    nx=max(1,round(width/cw));ny=max(1,round(height/ch))
    for row in range(ny):
        # Alternating half tiles keep mortar courses believable at panel edges.
        edges=[-width/2]
        if row%2:
            edges += [-width/2+width/nx*(i+.5) for i in range(nx)]
        else:edges += [-width/2+width/nx*i for i in range(1,nx)]
        edges += [width/2]
        for left,right in zip(edges,edges[1:]):
            gap=.035 if plaster else .65
            color=m.rng.choice(('e2d1a8','e1d0a7','e3d2aa')) if plaster else m.rng.choice(palette)
            box(m,(x+(left+right)/2,y,z-height/2+(row+.5)*height/ny),
                (right-left-gap,depth,height/ny-gap),color,.08 if plaster else .7)


def timber(m,p,s):
    """Visible join lines and shallow wood strips on rectangular timber."""
    box(m,p,s,m.rng.choice(TIMBER),1.8)
    x,y,z=p; w,d,h=s
    if h>55 and w<55:
        for zz in range(0,max(1,int(h/33))):
            hh=min(28,h-zz*33)
            if hh>0:box(m,(x-w*.21,y-d/2-.3,z-h/2+zz*33+hh/2),(w*.18,1.1,hh),'805a33',.3)
    elif w>60:
        for i in range(max(1,int(w/34))):
            xx=x-w/2+(i+.5)*34
            if xx<x+w/2-4:box(m,(xx,y-d/2-.35,z),(1.1,1,h*.76),'5d4025',.25)


def footing(m,width,depth,height,cell=31):
    # Tight house-shaped stone perimeter, never a broad independent platform.
    box(m,(0,0,height/2),(width-10,depth-10,height),STONE[0],1)
    for y,a in [(-depth/2,0),(depth/2,180)]:
        group(m,lambda:front_tiles(m,0,0,height/2,width,height,STONE,cell,23,17),(0,y,0),a)
    for x,a in [(-width/2,-90),(width/2,90)]:
        group(m,lambda:front_tiles(m,0,0,height/2,depth,height,STONE,cell,23,17),(x,0,0),a)


def window_local(m,width=72,height=111):
    # Local zero is the center of the opening. Glass is recessed behind frame.
    box(m,(0,3,0),(width,8,height),'174b40',.7)
    for sx in (-1,1):
        for sz in (-1,1):
            box(m,(sx*width*.237,-2,sz*height*.233),(width*.405,7,height*.413),m.rng.choice(TEAL),1.2)
            box(m,(sx*width*.237-4,-6,sz*height*.233),(width*.15,1.6,height*.36),'148f83',.5)
    box(m,(0,-10,0),(7,12,height),TEAL[1],1)
    box(m,(0,-10,0),(width,12,8),TEAL[1],1)
    for sx in (-1,1):timber(m,(sx*(width/2+6),-6,0),(13,28,height+24))
    timber(m,(0,-8,height/2+12),(width+31,31,18))
    timber(m,(0,-18,-height/2-10),(width+42,49,19))
    # Stone/plaster reveal directly around jambs.
    for sx in (-1,1):box(m,(sx*(width/2+15),5,0),(7,13,height+10),PLASTER[1],.8)


def window(m,x,y,z,w=72,h=111,angle=0):
    group(m,lambda:window_local(m,w,h),(x,y,z),angle)


def facade(m,width,bottom,top,y,window_x,window_z,window_w=72,window_h=111,door=False):
    # Separate plaster panels fit around openings: no opaque wall behind panes.
    openings=[(x-window_w/2-15,x+window_w/2+15,window_z-window_h/2-17,window_z+window_h/2+21) for x in window_x]
    if door:openings.append((-61,61,bottom,bottom+184))
    xs=sorted(set([-width/2,width/2]+[a for op in openings for a in op[:2]]))
    zs=sorted(set([bottom,top]+[max(bottom,min(top,a)) for op in openings for a in op[2:]]))
    for left,right in zip(xs,xs[1:]):
        for low,high in zip(zs,zs[1:]):
            if right-left<1 or high-low<1:continue
            cx=(left+right)/2;cz=(low+high)/2
            if any(a<cx<b and c<cz<d for a,b,c,d in openings):continue
            front_tiles(m,cx,y,cz,right-left,high-low)
    for x in window_x:window(m,x,y-3,window_z,window_w,window_h)


def door(m,y,bottom,height=176,width=96,teal=False):
    for i in range(5):
        box(m,(-width/2+(i+.5)*width/5,y,bottom+height/2),(width/5-.8,16,height),TEAL[0] if teal else ('995725','9c5c29','a3632c')[i%3],1.5)
        box(m,(-width/2+(i+.3)*width/5,y-9,bottom+height/2),(1.4,1.6,height-17),'78431e',.4)
    for sx in (-1,1):timber(m,(sx*(width/2+10),y-7,bottom+height/2),(20,36,height+15))
    timber(m,(0,y-6,bottom+height+9),(width+56,37,23))
    box(m,(width*.30,y-21,bottom+height*.49),(16,14,18),'dca02f',1.7)


def stairs(m,y,height,width,count=3):
    for row in range(count):
        z=height*(count-row)/count
        for col in range(max(1,round(width/29))):
            n=max(1,round(width/29))
            box(m,(-width/2+(col+.5)*width/n,y-row*26,z/2),(width/n-.7,29,z),STONE[(col+row)%len(STONE)],1.1)
        for sx in (-1,1):
            timber(m,(sx*(width/2+16),y-row*26,z/2+15),(32,31,z+30))


def growth(m,x,y,ground=0,spread=64,flowers=True):
    # Authored stepped clusters anchored to corners, with stems embedded in moss.
    for dx,dy,w,h in [(-22,0,27,29),(0,-12,27,41),(22,0,25,26),(-10,16,25,53),(13,18,22,42),(-29,-16,20,17),(29,-15,19,14)]:
        factor=spread/64
        xx=x+dx*factor; yy=y+dy*factor
        for row in range(max(1,round(h/14))):
            box(m,(xx,yy,ground+7+row*14),(w*factor,22*factor,14),m.rng.choice(MOSS),1.25)
    if flowers:
        for dx,dy,c in [(-11,-17,'f2d79a'),(19,1,'cb742d')]:
            zz=ground+46
            box(m,(x+dx,y+dy,zz),(9,8,13),'8b973b',.8)
            for ox,oz in [(-6,0),(0,0),(6,0),(0,8)]:
                box(m,(x+dx+ox,y+dy-2,zz+8+oz),(8,8,9),c,.8)


def planted_corners(m,w,d,h):
    # Broken extensions exactly adjacent to the wall footing, as in the PNGs.
    for sx in (-1,1):
        for sy in (-1,1):
            x=sx*(w/2-13);y=sy*(d/2-8)
            for dx,dy,z in [(0,0,10),(sx*21,0,10),(0,sy*22,10),(sx*21,sy*22,10),(sx*6,sy*8,32)]:
                box(m,(x+dx,y+dy,z),(31,31,22),m.rng.choice(STONE),1.5)
            growth(m,x,y,h*.49,72,sy<0)
    # Low moss runs wrap corners rather than scatter unrelated green cubes.
    for sx in (-1,1):
        for yy in (-d*.28,d*.30):growth(m,sx*(w/2+1),yy,8,40,False)


def tiled_roof(m,w,d,eaves,rise,rows=7,origin=(0,0)):
    ox,oy=origin
    # Solid core follows stepped tile profile but stays hidden under top courses.
    v=[(-w/2,-d/2,0),(-w/2,d/2,0),(-w/2,0,rise-12),(w/2,-d/2,0),(w/2,d/2,0),(w/2,0,rise-12)]
    m.solid(v,[[0,2,1],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],CLAY[4],pos=(ox,oy,eaves-9))
    run=d/2/rows;dz=rise/rows; nx=round(w/60)
    for side in (-1,1):
        for row in range(rows):
            yy=oy+side*(d/2-(row+.5)*run);zz=eaves+(row+.5)*dz
            for col in range(nx):
                xx=ox-w/2+(col+.5)*w/nx
                box(m,(xx,yy,zz),(w/nx-.55,run+2.5,dz+3),m.rng.choice(CLAY),1.25)
                # The render reference has fine block subdivisions on broad tiles.
                if col%3==row%3:box(m,(xx+6,yy,zz+(dz+3)/2+.15),(.65,run-1,.35),'bd7140',.08)
        for col in range(nx):
            if col%2==0:box(m,(ox-w/2+(col+.5)*w/nx,oy+side*(d/2-5),eaves-9),(15,25,16),'9a4b27',1.1)
    for col in range(nx):box(m,(ox-w/2+(col+.5)*w/nx,oy,eaves+rise+3),(w/nx-.8,run+11,23),CLAY[col%5],1.4)
    # Visible end triangles carry coursed blocks too; no broad flat roof ends.
    for sx in (-1,1):
        for row in range(rows):
            zz=eaves+(row+.45)*dz
            ww=d*(1-(row+.45)/rows)
            group(m,lambda ww=ww,zz=zz:front_tiles(m,0,0,zz,ww,dz-.8,CLAY,30,dz,5),
                  (ox+sx*w/2,oy,0),-90 if sx<0 else 90)
    # Dark timber stepped verge caps at both ends of the main roof.
    for sx in (-1,1):
        xx=ox+sx*(w/2-8)
        for side in (-1,1):
            for row in range(rows):
                if row in (0,rows-2,rows-1):
                    box(m,(xx,oy+side*(d/2-(row+.5)*run),eaves+(row+.5)*dz+6),(26,run+7,dz+13),'563c22',1.5)


def forward_gable(m,y,base,w,d,rise,rows=5,center_post=False):
    m.gable((0,y,base),w-22,d,rise-8,PLASTER[0])
    # Triangular face has actual mortar-seamed plaster blocks.
    for row in range(max(1,int(rise/21))):
        z=base+10+row*21;width=(w-28)*(1-(z-base)/rise)
        if width>15:front_tiles(m,0,y-d/2-2,z,width,20,PLASTER,35,20,6)
    if center_post:timber(m,(0,y-d/2-9,base+rise*.40),(20,17,rise*.8))
    step=w/2/rows; dz=rise/rows
    for side in (-1,1):
        for row in range(rows):
            xx=side*(w/2-(row+.5)*step);zz=base+(row+.5)*dz
            for col in range(max(2,round(d/29))):
                n=max(2,round(d/29));yy=y-d/2+(col+.5)*d/n
                box(m,(xx,yy,zz),(step+7,d/n-.8,dz+9),m.rng.choice(CLAY),1.45)
            timber(m,(xx,y-d/2-8,zz-22),(step+3,27,27))
    for col in range(max(2,round(d/29))):
        n=max(2,round(d/29))
        box(m,(0,y-d/2+(col+.5)*d/n,base+rise+6),(28,d/n-.8,25),CLAY[1],1.3)


def chimney(m,x,y,bottom,height):
    for row in range(round(height/23)):
        z=bottom+(row+.5)*height/round(height/23)
        for side in (-1,1):
            for col in (-1,1):
                box(m,(x+col*15,y+side*19,z),(29,24,height/round(height/23)-.8),STONE[(row+int(col))%5],1.3)
    for ix in (-1,1):
        for iy in (-1,1):box(m,(x+ix*21,y+iy*23,bottom+height+12),(41,45,26),STONE[2],1.4)
    for ix in (-1,1):
        for iy in (-1,1):box(m,(x+ix*11,y+iy*11,bottom+height+39),(21,21,29),CLAY[1],1.2)


def house_shell(m,w,d,bottom,top,front_windows,window_z):
    facade(m,w,bottom,top,-d/2,front_windows,window_z,door=True)
    # Continuous, fully authored rear wall and both side elevations.
    group(m,lambda:facade(m,w,bottom,top,0,front_windows,window_z),(0,d/2,0),180)
    for sx in (-1,1):
        a=-90 if sx<0 else 90
        group(m,lambda:facade(m,d,bottom,top,0,[-d*.23,d*.23],window_z,58,94), (sx*w/2,0,0),a)
        for yy in (-d/2,0,d/2):timber(m,(sx*(w/2+2),yy,(bottom+top)/2),(26,24,top-bottom+12))
    for y in (-d/2-4,d/2+4):
        for x in (-w/2,w/2):timber(m,(x,y,(bottom+top)/2),(31,29,top-bottom+14))
        for z in (bottom+4,top):timber(m,(0,y,z),(w+38,28,25))
        for x in range(-int(w/2)+12,int(w/2),49):
            timber(m,(x,y-5,top-25),(25,30,25))
    for sx in (-1,1):
        for z in (bottom+4,top):timber(m,(sx*(w/2+3),0,z),(27,d+25,25))


def lodge():
    m=mesh('lodge',1201)
    w,d=498,298;bottom,top=70,316
    footing(m,w+32,d+27,bottom)
    house_shell(m,w,d,bottom,top,[-159,159],180)
    door(m,-d/2-15,bottom+3,177)
    stairs(m,-d/2-41,bottom,125,3)
    tiled_roof(m,583,382,342,192,7)
    # Lodge dormer is a tall upper bay; unlike cottage it carries a teal window.
    front_tiles(m,0,-186,376,161,119)
    for x in (-92,92):timber(m,(x,-197,378),(28,28,134))
    # Continuous dormer cheeks meet the rising main roof and stop the side voids.
    for sx in (-1,1):
        for yy in (-186,-164,-142,-120):
            low=342+(1-abs(yy)/191)*192
            high=440
            if high>low:
                box(m,(sx*79,yy,(low+high)/2),(11,23,high-low),PLASTER[0],.4)
    window(m,0,-198,378,61,76)
    forward_gable(m,-142,439,252,165,115,4)
    chimney(m,-195,-68,409,177)
    planted_corners(m,w+30,d+26,bottom)
    return finish(m,'lodge')


def cottage():
    m=mesh('cottage',1202)
    w,d=466,272;bottom,top=64,260
    footing(m,w+29,d+25,bottom)
    house_shell(m,w,d,bottom,top,[-150,150],162)
    door(m,-d/2-15,bottom+1,161,89)
    stairs(m,-d/2-40,bottom,120,3)
    tiled_roof(m,548,357,286,147,6)
    # Broad lower front gable crosses the roof; exposed timber, no dormer window.
    forward_gable(m,-121,281,375,188,151,5,True)
    timber(m,(0,-221,283),(375,25,24))
    chimney(m,-183,-57,337,161)
    planted_corners(m,w+29,d+24,bottom)
    return finish(m,'cottage')


def bell(m,z):
    # A real flared bell profile, rather than the old ellipsoid blob.
    rings=[(z,28),(z+7,29),(z+11,23),(z+37,17),(z+43,10)]
    n=12;verts=[]
    for zz,r in rings:
        for i in range(n):verts.append((r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),zz))
    # Each frustum is convex and closed, preserving meshkit validation semantics.
    for k in range(len(rings)-1):
        vs=verts[k*n:(k+2)*n];faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]
        faces += [[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
        m.solid(vs,faces,'c89425')
    box(m,(0,0,z+54),(8,8,23),'634720',.8)
    box(m,(0,0,z-4),(8,8,12),'78501e',1)


def civic_hall(rear_center_windows=True, entrance_details=True):
    m=mesh('civic_hall',1203)
    w,d=824,326;bottom,mid,top=104,327,553
    detail_sections=[]
    section_start=len(m.parts)
    footing(m,w+32,d+26,bottom,27)
    detail_sections.append((section_start,len(m.parts)))
    # Front facade: paired windows around a broad central door bay.
    for y,a in [(-d/2,0),(d/2,180)]:
        for lo,hi,zc in [(bottom,mid,206),(mid,top,443)]:
            def story():
                bays=[-345,-237,237,345]
                door_opening=lo==bottom and a==0
                if a==180 and rear_center_windows:
                    # Keep downstream roof/front/plant color choices stable.
                    # The scratch facade consumes the original random sequence.
                    original=Mesh('CivicHallOriginalRearStory')
                    original.rng.setstate(m.rng.getstate())
                    facade(original,w,lo,hi,0,bays,zc,58,105,False)
                    facade(m,w,lo,hi,0,[-345,-237,-65,65,237,345],zc,58,105,False)
                    m.rng.setstate(original.rng.getstate())
                else:
                    facade(m,w,lo,hi,0,bays,zc,58,105,door_opening)
            group(m,story,(0,y,0),a)
    for sx in (-1,1):
        for lo,hi,zc in [(bottom,mid,206),(mid,top,443)]:
            group(m,lambda lo=lo,hi=hi,zc=zc:facade(m,d,lo,hi,0,[-91,91],zc,57,105),(sx*w/2,0,0),-90 if sx<0 else 90)
    for y in (-d/2-3,d/2+3):
        for x in (-w/2,-290,-175,175,290,w/2):
            timber(m,(x,y,(bottom+top)/2),(25,29,top-bottom+15))
            for z in (mid,top):timber(m,(x,y-5,z-17),(38,41,41))
        for z in (bottom,mid,top):timber(m,(0,y,z),(w+31,29,23))
    for sx in (-1,1):
        for yy in (-d/2,0,d/2):timber(m,(sx*w/2,yy,(top+bottom)/2),(27,25,top-bottom+10))
        for z in (bottom,mid,top):timber(m,(sx*w/2,0,z),(27,d+20,23))
    tiled_roof(m,920,405,579,149,7)
    # Central projecting bay is proportionate to the source's narrow entrance.
    front_tiles(m,0,-190,399,250,205)
    for x in (-134,134):timber(m,(x,-201,322),(27,29,426))
    timber(m,(0,-207,329),(295,29,24))
    window(m,0,-207,424,66,98)
    forward_gable(m,-162,500,315,160,138,6)
    # Door is stepped to match the arch, with dark inset tympanum.
    section_start=len(m.parts)
    for row in range(8):
        width=108 if row<6 else (84 if row==6 else 59)
        for col in range(max(1,round(width/20))):
            n=max(1,round(width/20))
            box(m,(-width/2+(col+.5)*width/n,-203,116+row*22),(width/n-.8,17,23),TEAL[col%4],1)
    for x in (-30,0,30):box(m,(x,-214,197),(5,7,171),TEAL[1],.7)
    for z in (160,221,270):box(m,(0,-214,z),(106,8,6),TEAL[1],.7)
    for sx in (-1,1):
        for row in range(6):box(m,(sx*66,-219,115+row*22),(22,31,21),PLASTER[row%4],1)
        for i in range(4):box(m,(sx*(64-i*17),-219,251+i*16),(25,31,22),PLASTER[(i+1)%4],1)
    box(m,(0,-220,310),(25,31,25),PLASTER[2],1)
    stairs(m,-231,104,168,5)
    detail_sections.append((section_start,len(m.parts)))
    # Tower clock body has masonry at all four faces and timber corners.
    for y,a in [(-86,0),(86,180)]:
        group(m,lambda:front_tiles(m,0,0,721,193,223,PLASTER,28,23),(0,y,0),a)
    for x,a in [(-94,-90),(94,90)]:group(m,lambda:front_tiles(m,0,0,721,169,223,PLASTER,28,23),(x,0,0),a)
    for x in (-96,96):
        for y in (-88,88):timber(m,(x,y,721),(23,23,246))
    for y in (-96,96):timber(m,(0,y,838),(220,26,26))
    for x in (-105,105):timber(m,(x,0,838),(22,192,26))
    for i in range(16):
        a=i*2*math.pi/16
        box(m,(math.sin(a)*56,-103,731+math.cos(a)*56),(16,13,16),TEAL[0] if i%2==0 else '766544',1)
    # Reference clock hands vertical, short dark upper and lower hands.
    for zz,h in [(744,27),(719,22)]:box(m,(0,-115,zz),(9,9,h),'594224',.6)
    box(m,(0,-120,732),(13,8,13),'6c4b21',.8)
    # Tall open chamber. The source bell sits behind the clear front opening.
    for ix in range(8):
        for iy in range(7):box(m,(-105+(ix+.5)*26.25,-94.5+(iy+.5)*27,860),(25.5,26.2,21),STONE[(ix+iy)%5],1)
    for x in (-83,83):
        for y in (-74,74):
            for row in range(4):box(m,(x,y,884+row*24),(39,39,23),PLASTER[row%4],1.1)
    bell(m,890)
    for ix in range(9):
        for iy in range(8):box(m,(-123+(ix+.5)*27.33,-108+(iy+.5)*27,978),(26.5,26.2,26),STONE[(ix+iy)%5],1.2)
    # Four terracotta square tiers, individually jointed all the way around.
    for row,width in enumerate((191,145,99,54)):
        n=max(2,round(width/25))
        for ix in range(n):
            for iy in range(n):box(m,(-width/2+(ix+.5)*width/n,-width/2+(iy+.5)*width/n,1000+row*23),(width/n-.8,width/n-.8,24),CLAY[(ix+iy)%5],1.1)
    timber(m,(0,0,1101),(37,37,38))
    for x in (-113,113):
        group(m,lambda:wall_lamp(m),(x,-232,226),0)
    section_start=len(m.parts)
    planted_corners(m,w+30,d+25,bottom)
    detail_sections.append((section_start,len(m.parts)))
    for x in (-250,250):
        for ix in (-1,1):
            for iy in (-1,1):box(m,(x+ix*16,-217+iy*14,12),(31,27,24),STONE[2],1.1)
        growth(m,x,-219,24,56,True)
    if entrance_details:
        import civic_hall_details
        civic_hall_details.refine(m,detail_sections)
    # The reference hall has a broad, near-square overall silhouette.
    # Widen the long elevation while retaining floor and tower height.
    m.vertices=[(x*1.1,y,z) for x,y,z in m.vertices]
    for part in m.parts:
        x,y,z=part['center'];part['center']=(x*1.1,y,z);part['volume']*=1.1
    return finish(m,'civic_hall')


def wall_lamp(m):
    box(m,(0,7,0),(25,17,36),'e6aa38',1)
    for x in (-14,14):box(m,(x,-4,0),(4,7,41),'454236',.6)
    for z in (-22,22):box(m,(0,0,z),(34,26,7),'454236',.8)
    box(m,(0,0,29),(17,16,9),'51452f',.8)
    box(m,(0,-2,0),(12,2,22),'ffdc83',.5)


def market_stall():
    m=mesh('market_stall',1204)
    w,d=456,286
    footing(m,w+24,d+20,38,29)
    for ix in range(14):
        for iy in range(9):box(m,(-w/2+(ix+.5)*w/14,-d/2+(iy+.5)*d/9,42),(w/14-.7,d/9-.7,12),'a16c34',1)
    for x in (-207,207):
        for y in (-119,119):
            timber(m,(x,y,169),(30,30,255))
            for z in (65,284):timber(m,(x,y,z),(42,42,36))
    # Shallow descending canopy, seven stripes, a 2x7 quilt grid per stripe.
    for stripe in range(7):
        key=TEAL[1] if stripe%2==0 else 'edd49a'
        for ix in range(2):
            x=-231+(stripe*2+ix+.5)*33
            for iy in range(8):
                y=-153+(iy+.5)*39;z=279+iy*4.2
                box(m,(x,y,z),(32.4,39.5,10),key,.8)
        x=-231+(stripe+.5)*66
        for ix in range(2):box(m,(x-16.5+ix*33,-164,266),(32.4,13,23),key,1)
        box(m,(x,-164,249),(29,13,12),key,1)
    for y in (-122,122):
        timber(m,(0,y,263),(455,26,25))
        for sx in (-1,1):
            m.beam((sx*205,y,227),(sx*166,y,264),17,'694525')
            timber(m,(sx*182,y,247),(26,23,19))
    for side in (-1,1):
        x=side*137
        for xx in (-71,71):timber(m,(x+xx,-88,84),(21,30,84))
        for zz in (62,83,104):
            for col in range(4):box(m,(x-66+(col+.5)*33,-99,zz),(32.4,17,20),TIMBER[col%4],1)
        for col in range(5):box(m,(x-79+(col+.5)*31.6,-84,130),(31,106,17),'a36c32',1.4)
        for slot in range(3):
            xx=x-45+slot*45; zz=151+(slot==2)*19
            crate(m,xx,-77,zz,39,34,23)
            for j,(dx,dy,dz) in enumerate([(-9,-7,0),(7,-5,0),(0,8,0),(1,0,13)]):
                box(m,(xx+dx,-77+dy,zz+20+dz),(14,14,14),['dcb139','819337','ce6228'][slot],1.2)
        crate(m,x,11,163,66,56,43,True)
        crate(m,x+36,56,179,46,46,47,True)
    # Blue stoppered bottle and turquoise draped cloth on left counter.
    box(m,(-194,-84,155),(21,22,36),'727d98',1.8)
    box(m,(-194,-84,179),(9,10,13),'b6a88b',1)
    for row in range(3):
        for col in range(2):box(m,(-144+col*17,-140,129-row*16),(16.5,7,16),TEAL[1],.8)
    # Hanging token on the right, a shaped border around the teal center.
    # Extend from the front upright beyond the awning front edge. The token must
    # stay outside the canopy silhouette after final source-handedness reflection.
    timber(m,(207,-157,259),(18,94,18))
    timber(m,(250,-195,259),(91,18,18))
    for x in (257,278):box(m,(x,-195,246),(9,12,29),'a37233',.8)
    for dx,zz,ww in [(0,221,49),(-25,221,14),(25,221,14),(0,198,31),(0,244,31)]:
        timber(m,(269+dx,-195,zz),(ww,20,zz==221 and 32 or 14))
    box(m,(269,-209,221),(23,11,23),TEAL[1],1.5)
    stairs(m,-178,38,106,2)
    planted_corners(m,w+22,d+19,38)
    return finish(m,'market_stall')


def crate(m,x,y,z,w,d,h,open_top=False):
    for row in range(max(2,round(h/12))):
        n=max(2,round(h/12));zz=z-h/2+(row+.5)*h/n
        for sy in (-1,1):
            for col in range(max(2,round(w/20))):
                nx=max(2,round(w/20))
                box(m,(x-w/2+(col+.5)*w/nx,y+sy*d/2,zz),(w/nx-.65,8,h/n-.65),'93602b',.8)
        for sx in (-1,1):box(m,(x+sx*w/2,y,zz),(8,d,h/n-.65),'795026',.8)
    box(m,(x,y,z-h/2+3),(w,d,6),'5f4021',.8)
    if not open_top:box(m,(x,y,z+h/2-3),(w-6,d-6,5),'795024',.7)


def rock_mound(m,center=(0,0),radius=40):
    x,y=center
    # Irregular stepped edge follows the source's rocky stump, no full square slab.
    layout=[(-24,-20,14,26),(0,-28,12,25),(24,-17,14,25),(-30,5,11,25),(27,10,13,23),
            (-16,24,13,24),(9,25,12,24),(0,0,19,34),(-10,-6,37,25),(14,5,35,24)]
    for i,(dx,dy,z,w) in enumerate(layout):
        box(m,(x+dx*radius/40,y+dy*radius/40,z),(w,w,22),STONE[i%5],1.6)
    for dx,dy,z in [(-23,3,29),(19,-16,27),(-12,18,34),(5,5,51),(-17,-22,15),(29,7,22)]:
        for col in range(2):box(m,(x+dx+col*10,y+dy,z),(11,13,13),MOSS[col+1],1)


def iron_band(m,x,z,width=36,depth=35,height=18):
    box(m,(x,0,z),(width,depth,height),'4a4e43',1)
    for sx in (-1,1):box(m,(x+sx*(width/2+2),0,z),(6,9,9),'707466',.7)
    for sy in (-1,1):box(m,(x,sy*(depth/2+2),z),(9,6,9),'707466',.7)


def sign():
    m=mesh('sign',1205)
    rock_mound(m,(0,0),43)
    # Four adjacent long grain pieces give depth relief without painted textures.
    for i in range(4):box(m,(-19+(i+.5)*9.5,0,129),(9.2,37,183),TIMBER[(i+1)%4],.7)
    for z in (109,202):iron_band(m,0,z,46,44,19)
    box(m,(0,0,223),(44,44,18),'bd9143',1)
    for i,width in enumerate((42,31,21,10)):
        box(m,(0,0,232.15+i*.16),(width,width,.3),['d2aa59','a97e36','cea452','ae8139'][i],.05)
    # Recessed blank face is three independent dark timber planks.
    for row in range(3):
        box(m,(26,-24,146+row*12),(125,14,11.4),['795827','805c29','735025'][row],.65)
    for z in (133,185):
        for i in range(5):box(m,(-48+(i+.5)*27,-33,z),(26.7,19,13),['b9883b','c0903f','b18035'][i%3],.85)
    for zz in (144,158,172):box(m,(-42,-33,zz),(14,19,13.4),'b98736',1)
    # Solid tapered arrow center and bevelled stepped outline.
    for i in range(5):
        x=88+i*8
        box(m,(x,-25,159),(9,15,51-i*10),'8d662d',.8)
        for side in (-1,1):box(m,(x,-34,159+side*(28-i*6)),(12,19,13),'bd8b3a',1)
    for dx,dy,z in [(-13,-17,214),(12,-17,212),(-18,4,216)]:box(m,(dx,dy,z),(13,11,9),MOSS[1],1)
    # Source moss rises around the stump and spills over the outer stones.
    for dx,dy,z,w,h in [(-24,-14,24,15,15),(-21,3,40,15,24),(-18,11,52,14,19),
                         (21,-11,26,17,17),(23,4,39,15,15),(13,15,49,14,14),
                         (-31,-17,15,13,13),(30,15,20,14,14),(0,-26,21,14,12),
                         (-9,28,25,13,14),(18,-22,16,13,12)]:
        box(m,(dx,dy,z),(w,13,h),MOSS[(int(z)//7)%5],1.1)
    return finish(m,'sign')


def lantern():
    m=mesh('lantern',1206)
    # The source has a squat, stepped stone plinth covered in moss, not a few
    # loose pale rocks. Three individually jointed tiers wrap the post base.
    for row,(width,depth,height,z) in enumerate([(92,86,23,11.5),(77,72,22,33),(61,59,22,54)]):
        nx,ny=4 if row==0 else 3,4 if row==0 else 3
        for ix in range(nx):
            for iy in range(ny):
                # Slightly offset corner blocks retain the worn source silhouette.
                xx=21-width/2+(ix+.5)*width/nx
                yy=-depth/2+(iy+.5)*depth/ny
                if row==0 and ix in (0,nx-1) and iy in (0,ny-1):yy+=(-2 if iy==0 else 2)
                box(m,(xx,yy,z),(width/nx-.7,depth/ny-.7,height),STONE[(ix+iy+row)%5],1.2)
    for dx,dy,z,w,h in [(-29,-18,29,18,15),(-24,13,34,17,17),(21,-20,31,18,15),
                         (29,9,27,16,14),(-12,-27,38,18,13),(10,25,37,18,14),
                         (-15,-14,62,16,12),(14,-14,62,17,12),(-17,13,61,15,12),
                         (13,14,62,17,12),(-35,8,13,16,12),(31,-12,15,15,12)]:
        box(m,(21+dx,dy,z),(w,16,h),MOSS[(int(z)//7)%5],1.1)
    for i in range(4):box(m,(7+(i+.5)*7,0,171),(6.8,29,244),TIMBER[i%4],.8)
    for z in (65,139,279):iron_band(m,21,z,39,39,24)
    timber(m,(21,0,301),(37,37,31))
    timber(m,(-24,0,292),(112,29,29))
    for i in range(6):box(m,(-75+(i+.5)*17,0,307),(16.4,29,1.4),'806039',.3)
    m.beam((20,0,246),(-39,0,285),17,'624726')
    iron_band(m,-70,292,18,37,37)
    # Alternating rectangular chain links have actual empty openings.
    for j in range(2):
        z=269-j*17
        if j==0:
            for x in (-77,-63):box(m,(x,0,z),(4,6,18),'464c41',.7)
            for dz in (-9,9):box(m,(-70,0,z+dz),(17,6,4),'464c41',.7)
        else:
            for y in (-7,7):box(m,(-70,y,z),(6,4,18),'464c41',.7)
            for dz in (-9,9):box(m,(-70,0,z+dz),(6,17,4),'464c41',.7)
    for z,w in [(235,30),(226,45),(216,63)]:
        n=max(2,round(w/18))
        for ix in range(n):
            for iy in range(n):box(m,(-70-w/2+(ix+.5)*w/n,-w/2+(iy+.5)*w/n,z),(w/n-.6,w/n-.6,12),'505548',.8)
    # Four amber pane faces have a blockwise warm-to-cream luminous color gradient.
    for angle in (0,90,180,270):
        def panes():
            for ix in range(4):
                for iz in range(6):
                    center=abs(ix-1.5)+abs(iz-2.5)*.6
                    c='ffe09a' if center<1.5 else ('f4bf55' if center<2.5 else 'eaa331')
                    # Overlapping planar cells carry color without dark lattice gaps.
                    box(m,(-20+(ix+.5)*10,-24,164+(iz+.5)*8),(10.2,5,8.2),c,.025)
        group(m,panes,(-70,0,0),angle)
    # Blackened internal core creates the same framing separation as the PNG.
    box(m,(-70,0,187),(42,42,62),'c98a2c',1)
    for x in (-97,-43):
        for y in (-27,27):
            box(m,(x,y,186),(8,8,69),'474c40',1)
            for z in (151,218):box(m,(x,y,z),(13,13,13),'4e5447',1)
    for z in (149,217):
        for sy in (-1,1):
            for col in range(3):box(m,(-94+(col+.5)*16,sy*27,z),(15.5,11,11),'4d5346',.8)
        for sx in (-1,1):box(m,(-70+sx*27,0,z),(11,51,11),'4d5346',.8)
    return finish(m,'lantern')


def reflect_source_handedness(m):
    """Reflect X once and reverse winding so every component stays outward."""
    assert not getattr(m,'source_x_reflected',False),'Source handedness already applied'
    m.vertices=[(-x,y,z) for x,y,z in m.vertices]
    m.triangles=[(v0,v2,v1) for v0,v1,v2 in m.triangles]
    for part in m.parts:
        x,y,z=part['center'];part['center']=(-x,y,z)
    m.source_x_reflected=True


def finish(m,key):
    reflect_source_handedness(m)
    # Source position is at footing ground, and all metadata stays exact.
    low=min(v[2] for v in m.vertices)
    if low!=0:
        m.vertices=[(x,y,z-low) for x,y,z in m.vertices]
        for part in m.parts:part['center']=(part['center'][0],part['center'][1],part['center'][2]-low)
    bounds=[[min(v[a] for v in m.vertices),max(v[a] for v in m.vertices)] for a in range(3)]
    SPECS[key]['dimensions_cm']=[round(b-a,3) for a,b in bounds]
    SPECS[key]['bounds_cm']=bounds
    SPECS[key]['triangles']=len(m.triangles)
    SPECS[key]['source_x_reflected']=True
    m.source_reference=SPECS[key]['source']
    return m


BUILDERS={'lodge':lodge,'cottage':cottage,'civic_hall':civic_hall,
          'market_stall':market_stall,'lantern':lantern,'sign':sign}
