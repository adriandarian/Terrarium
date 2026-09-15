"""Ten broad planks, four pairs of banded posts, double rails and four stone risers."""
import sys,random,math
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
P=[('836022','bridgewood'),('976c25','bridgewood'),('6f4e1f','bridgewood'),('a8782b','bridgewood'),
   ('66694f','metal'),('858873','metal'),('90937b','mineral'),('82896d','mineral'),('9fa087','mineral'),
   ('77825b','mineral'),('707e33','mineral'),('89913b','mineral'),('956c2b','bridgewood')]
a=Asset('RiverCrossing','river_crossing.png',P);rng=random.Random(130913)
def box(label,p,size,index,bevel=.004,group='Bridge',**kw):
    o=a.box(label,p,size,index,bevel,**kw);o['module']=group;return o
# Long axis is Y. Near bridge end is -Y; the stone stair rises away at +Y.
deck_z=.62;length=3.12;width=1.12
for x in [-.46,.46]:box('Under-deck beam',(x,0,.47),(.13,3.20,.19),2,.005)
for i in range(10):
    y=-1.42+i*.315
    box('Broad deck plank',(0,y,deck_z-.055),(width,.292,.11),[0,1,0,3,1,0,1,3,0,1][i],.007)
    # Pair of short square nails sit flush in the plank at the supporting beams.
    for x in [-.44,.44]:box('Deck fastening',(x,y+.075,deck_z+.003),(.036,.065,.008),4,.001)
post_ys=[-1.56,-.52,.52,1.56]
for x in [-.61,.61]:
    for i,y in enumerate(post_ys):
        height=1.20
        box('Square bridge post',(x,y,height/2),(.16,.18,height),0,.006,top_index=12)
        box('Post crown cap',(x,y,1.22),(.19,.21,.14),1,.006,top_index=12)
        # Separate bands wrap all four post faces instead of coloring the timber surface.
        for z in [.25,1.03]:
            box('Post iron band X',(x,y-.093,z),(.172,.014,.035),4,.001)
            box('Post iron band X',(x,y+.093,z),(.172,.014,.035),4,.001)
            box('Post iron band Y',(x-.086,y,z),(.014,.18,.035),4,.001)
            box('Post iron band Y',(x+.086,y,z),(.014,.18,.035),4,.001)
        if i in [1,2]:box('Pile foot',(x,y,.065),(.21,.23,.13),2,.004)
    for j in range(3):
        y=(post_ys[j]+post_ys[j+1])/2
        for z in [.89,1.14]:box('Long side rail',(x,y,z),(.082,1.055,.085),1,.005)
        # Small side blocks seat the rails against each square post.
        for yy in [post_ys[j]+.08,post_ys[j+1]-.08]:box('Rail seat',(x,yy,.86),(.11,.12,.10),2,.003)
# Ground supports under the two interior post pairs are structural, not floating trim.
for y in [-.52,.52]:box('Cross bearer',(0,y,.36),(1.32,.15,.15),2,.004)
# Four physically solid stone tiers. Tiny facets carry the source's muted stone mosaic.
for step in range(4):
    front=1.70+step*.29;top=deck_z+.17*(step+1);w=1.20;d=.29
    nx,ny,nz=12,3,max(1,round(top/.10))
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                # Interior blocks are omitted, while each remaining solid voxel stays closed.
                if 0<ix<nx-1 and 0<iy<ny-1 and 0<iz<nz-1:continue
                x=-w/2+(ix+.5)*w/nx;y=front+(iy+.5)*d/ny;z=(iz+.5)*top/nz
                moss=(ix in [0,3,10] and (iy+step)%3==0) or (iz<3 and (ix*7+iy+step)%5==0)
                color=rng.choice([10,11]) if moss else rng.choice([6,6,7,8,9])
                box('Mossy stone tier',(x,y,z),(w/nx-.0006,d/ny-.0006,top/nz-.0006),color,.001,group='StoneApproach')
a.scene['modules']='Bridge,StoneApproach'
a.scene['deck_top_m']=deck_z
a.scene['bridge_length_m']=3.12
a.studio(focus=(0,.58,.62),location=(-4,-9,12),scale=5.40)
a.scene.render.resolution_x=1000;a.scene.render.resolution_y=1400
a.scene.view_settings.exposure=-.30
result=a.save()
