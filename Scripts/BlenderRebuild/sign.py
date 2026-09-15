"""Blank stepped arrow sign from sign.png: inset planks, banded post, moss rocks."""
import sys
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
palette=[('775022','wood'),('89602b','wood'),('5e401f','wood'),('b38339','wood'),('c89b49','endgrain'),('b99240','wood'),
         ('464c42','metal'),('636b5c','metal'),('9b9e83','stone'),('7e8470','stone'),('5e7162','stone'),
         ('81882a','moss'),('a1a443','moss'),('636f24','moss')]
a=Asset('Sign','sign.png',palette);b=a.box
px=-.35
# Uneven stone mound with visible moss between specific upper rocks.
rocks=[(-2,-1,0),(-1,-2,0),(0,-2,0),(1,-2,0),(2,-1,0),(-2,0,0),(-1,0,0),(0,0,0),(1,0,0),(2,0,0),(-1,1,0),(0,1,0),(1,1,0),
       (-1,-1,1),(0,-1,1),(1,-1,1),(-1,0,1),(0,0,1),(1,0,1),(0,1,1),(-1,0,2),(1,0,2)]
for x,y,z in rocks:b('Individual footing stone',(px+x*.18,y*.18,.09+z*.16),(.177,.179,.177),[8,9,10][(x+y+z)%3],.006)
for x,y,z in [(-2,-1,0),(2,0,0),(-1,-1,1),(-1,0,2),(1,0,2),(1,-1,1),(1,1,1),(0,1,2)]:
    b('Moss clump',(px+x*.17,y*.18-.015,.19+z*.16),(.15,.16,.16),[11,12,13][(x+z)%3],.004)
b('Square timber post',(px,.02,1.48),(.43,.39,2.30),0,.007,top_index=4)
for x in [-.12,.01,.135]:b('Post vertical grain',(px+x,-.179,1.1),(.056,.012,.92),1,.002)
for z in [1.12,2.30]:
    b('Iron post band',(px,.015,z),(.50,.45,.22),6,.007)
    b('Square front bolt',(px,-.238,z),(.09,.062,.092),7,.005)
b('Golden endgrain cap',(px,.02,2.57),(.455,.42,.23),3,.006,top_index=4)
for x,y,z in [(-1,-1,2.435),(0,-1,2.435),(1,-1,2.435),(-1,0,2.42),(1,0,2.42),(0,-1,2.37)]:
    b('Moss under head cap',(px+x*.14,y*.14-.055,z),(.14,.13,.066),11 if x else 12,.003)
# Thick sign blank. Individual rails stand forward of the inset writing planks.
y=-.32;z=1.68
b('Arrow board core',(-.22,y,z),(1.67,.17,.68),2,.004)
for j in range(3):
    zz=z+(j-1)*.183
    b('Blank inset horizontal plank',(-.20,y-.104,zz),(1.58,.055,.176),[0,2,0][j],.004)
    b('Left projecting plank tab',(-1.065,y-.103,zz),(.14,.155,.145),3,.004)
for side in [-1,1]:
    b('Golden raised long rail',(-.22,y-.145,z+side*.355),(1.78,.145,.13),3,.006)
    # Back rails finish the hidden elevation with the same construction.
    b('Rear long rail',(-.22,y+.09,z+side*.30),(1.76,.095,.10),1,.005)
# Stepped arrowhead: solid backing and physical raised rim, with a recessed center.
for j in range(5):
    x=.60+j*.12;half=.49-j*.095
    b('Arrowhead solid', (x,y,z),(.123,.17,half*2),0,.004)
    for side in [-1,1]:b('Stepped gold arrow edge',(x,y-.145,z+side*(half-.052)),(.125,.145,.112),3 if j%2 else 5,.004)
    if half>.13:b('Arrowhead inset',(x,y-.104,z),(.12,.05,(half-.112)*2),2,.003)
b('Arrow tip',(1.145,y-.10,z),(.115,.23,.12),3,.004)
a.studio(focus=(-.05,-.02,1.36),location=(-5,-8,5.4),scale=3.46)
a.scene.render.resolution_x=1100;a.scene.render.resolution_y=1100
result=a.save()
