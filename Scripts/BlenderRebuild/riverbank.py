"""Stepped green bank, individual cattails and scattered cubic stones from the reference."""
import sys,random,math
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import bpy,importlib,assetkit
importlib.reload(assetkit)
from assetkit import Asset
P=[('929824','bankleaf'),('a0a827','bankleaf'),('7f8b1d','bankleaf'),('adb02b','bankleaf'),
   ('72821d','bankleaf'),('bfa21d','mineral'),('d4bd23','mineral'),('ac961b','mineral'),
   ('8f9388','mineral'),('7e857b','mineral'),('a0a396','mineral'),('788a18','bankleaf')]
a=Asset('Riverbank','homestead_riverbank_v2.png',P)
rng=random.Random(91421);cell=.09
def block(label,pos,size,index,top=None,bevel=.0008):
    return a.box(label,pos,size,index,bevel,top_index=top)
# An open apron in front of a left-hand clump, rather than a rectangular planter.
ground={}
for ix in range(-13,14):
    for iy in range(-7,8):
        edge=(ix/12.6)**2+(iy/6.4)**2
        if edge>1+.07*math.sin(ix*7+iy*3):continue
        ground[ix,iy]=True
        block('Bank ground voxel',(ix*cell,iy*cell,cell/2),(cell,cell,cell),rng.choice([0,1,2,4]),top=1)
# Explicit irregular columns keep the tall mass on the source's left side.
columns=[(-9,1,5),(-8,2,6),(-7,3,9),(-6,3,8),(-5,3,5),(-4,3,6),(-3,3,4),
         (-9,0,4),(-8,1,6),(-7,2,5),(-6,2,6),(-5,2,3),(-4,2,5),(-3,2,3),
         (-10,-1,2),(-9,-1,3),(-8,0,4),(-7,1,4),(-6,1,3),(-5,1,2),(-4,1,3),
         (-8,-1,2),(-7,-1,4),(-6,0,5),(-5,0,3),(-4,-1,4),(-3,-1,5),
         (-2,0,3),(-2,1,2),(-2,3,3),(-1,2,2),(-10,2,3),(-11,0,3),
         (-11,-2,1),(-10,-3,2),(-9,-3,1),(-7,-4,2),(-5,-4,2),(-3,-4,3),(-1,-4,2),
         (4,2,3),(6,3,2),(8,3,4),(10,2,3),(11,0,2),(12,-1,1),(9,-2,2),(7,-3,1)]
heights={(x,y):n for x,y,n in columns}
for (x,y),n in list(heights.items()):
    if x<-2 and n>3:
        for dx,dy in [(1,0),(0,1),(-1,0)]:
            if (x+dx,y+dy) in ground:
                heights.setdefault((x+dx,y+dy),rng.choice([1,2,3]))
for (ix,iy),n in heights.items():
    if (ix,iy) not in ground:continue
    for layer in range(n):
        block('Stepped bank vegetation',(ix*cell,iy*cell,cell*(layer+1.5)),(cell,cell,cell),rng.choice([0,1,2,3,4]),top=3)
# x/y locations are laid out across the open center and right, preserving the front apron.
reeds=[(-.16,.28,1.16),(.02,.25,.99),(.17,.29,1.07),(.32,.31,1.13),
       (-.24,.04,.81),(-.10,.00,.67),(.43,.12,.93),(.58,.27,1.08),
       (.73,.12,.91),(.88,.26,1.03),(.45,-.04,.83),(.10,-.19,.64),
       (.25,-.19,.66),(.75,-.11,.70),(.89,-.31,.52),(.66,-.35,.46),
       (.44,-.36,.40),(.30,.43,.77)]
for i,(x,y,top) in enumerate(reeds):
    base=cell;head=.145 if top>.8 else .11
    stem=top-head-.018-base
    for j in range(5):
        block('Cattail stem',(x,y,base+(j+.5)*stem/5),(.018,.018,stem/5),[4,11,0,2,11][(i+j)%5],bevel=0)
    for j in range(3):
        block('Cattail seed head',(x,y,top-.018-head+(j+.5)*head/3),(.065,.062,head/3),[5,6,7][i%3],top=6,bevel=.001)
    block('Cattail tip',(x,y,top-.009),(.020,.019,.018),5,top=6,bevel=.0005)
    for side in [-1,1]:
        h=(top-base)*rng.uniform(.25,.55)
        # Upright blades use stepped offsets in the reference's square-block vocabulary.
        xx=x+side*.029;yy=y+side*.025
        block('Upright reed blade',(xx,yy,base+h/2),(.024,.025,h),rng.choice([0,1,2,4]),top=3,bevel=0)
stones=[(-.83,-.31,.085),(-.76,-.31,.07),(-.57,-.48,.085),(-.35,-.50,.09),
        (-.08,-.35,.10),(.08,-.32,.08),(.04,-.18,.13),(.14,-.13,.15),
        (-.03,.02,.12),(.33,-.47,.09),(.83,-.40,.11),(.96,-.23,.12),(.95,-.12,.10)]
for i,(x,y,w) in enumerate(stones):
    block('Scattered bank stone',(x,y,cell+w/2),(w,w,w),[8,9,10][i%3],top=10,bevel=.0016)
block('Stacked bank stone',(.14,-.13,cell+.15+.045),(.10,.10,.09),8,top=10,bevel=.0016)
# Store display palette values with the correct linear transfer in Blender-generated images.
for node in a.material.node_tree.nodes:
    if node.type!='TEX_IMAGE':continue
    node.interpolation='Closest'
    if 'BaseColor' not in node.image.name:continue
    im=node.image;v=list(im.pixels)
    for i in range(0,len(v),4):
        for j in range(3):
            c=v[i+j];v[i+j]=c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
    im.pixels.foreach_set(v);im.save();im.pack()
a.scene['cattails']=len(reeds)
a.scene['ground_cells']=len(ground)
a.studio(focus=(0,0,.47),location=(3.5,-6,4.5),scale=2.95)
a.scene.view_settings.exposure=.25
a.scene.render.resolution_x=1200;a.scene.render.resolution_y=1100
for ob in a.scene.objects:
    if ob.type=='LIGHT' and ob.data.name.startswith('Key'):
        ob.data.color=(1,.98,.90);ob.data.energy=1000;ob.data.size=5
result=a.save()
