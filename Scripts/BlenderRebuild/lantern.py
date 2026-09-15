"""Reference-specific suspended lantern, forged cage and timber post."""
import sys,math,random
from pathlib import Path
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset
PALETTE=[('5b3f1e','wood'),('6a4926','wood'),('503921','wood'),('6b4d2d','endgrain'),
         ('383b35','metal'),('454a43','metal'),('59615a','metal'),
         ('777d64','stone'),('5c6354','stone'),('8a8d73','stone'),
         ('747f24','moss'),('88932b','moss'),('596a22','moss'),
         ('ffbc35','pane'),('ef9820','pane'),('ffe17a','pane')]
a=Asset('Lantern','lantern.png',PALETTE);b=a.box
post=.36;lamp=-.40
# Ground-contact stone cluster, built in offset rows rather than a plain cube.
for row,coords in enumerate([
    [(-2,-1),(-1,-2),(-1,-1),(0,-2),(0,-1),(1,-2),(1,-1),(2,-1),(-2,0),(-1,0),(0,0),(1,0),(2,0),(-1,1),(0,1),(1,1)],
    [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)],
    [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)] ]):
    for x,y in coords:b('Footing stone',(post+x*.155,y*.155,.075+row*.14),(.151,.151,.146),[8,7,9][(x+y+row)%3],.006)
for x,y,z in [(-1,-1,2),(0,-1,2),(1,0,2),(1,1,2),(-1,0,2),(-1,1,2),(0,1,2),(1,-1,1),(-2,0,0),(2,-1,0)]:
    b('Moss facing',(post+x*.155,y*.155,.125+z*.14),(.154,.157,.145),[10,11,12][(x+y)%3],.004)
# Continuous square post, extended above its upper iron collar.
b('Oak upright',(post,0,1.78),(.30,.30,2.65),0,.007,top_index=3)
for x in [-.105,.03,.10]:b('Raised oak grain',(post+x,-.151,1.55),(.022,.008,1.8),1,.002)
for z in [.61,1.29,2.79]:
    b('Forged post collar',(post,0,z),(.365,.365,.23),4,.007)
    b('Front square rivet',(post,-.205,z),(.086,.059,.083),6,.005)
    b('Left square rivet',(post-.205,0,z),(.060,.084,.083),5,.005)
# Arm and its diagonal supporting brace carry the hanging mass.
b('Cross arm',(-.06,0,2.89),(1.18,.265,.25),0,.007,top_index=1)
b('Arm end iron strap',(-.50,0,2.89),(.145,.315,.305),5,.006)
b('Arm projecting end',(-.64,0,2.89),(.135,.252,.225),0,.005,top_index=3)
b('Diagonal timber brace',(.075,0,2.59),(.65,.19,.16),2,.007,rotation=(0,43,0))
for z in [3.07,3.145]:b('Post cap end grain',(post,0,z),(.31,.31,.073),0,.004,top_index=2)
# Two interlocking square links, with empty centers and perpendicular planes.
lamp=-.505
for axis,z in [('x',2.64),('y',2.47)]:
    w=.13;h=.20;t=.045
    for sign in [-1,1]:
        if axis=='x':b('Chain vertical',(lamp+sign*(w-t)/2,0,z),(t,t,h),4,.003)
        else:b('Chain vertical',(lamp,sign*(w-t)/2,z),(t,t,h),4,.003)
        if axis=='x':b('Chain crossbar',(lamp,0,z+sign*(h-t)/2),(w,t,t),5,.003)
        else:b('Chain crossbar',(lamp,0,z+sign*(h-t)/2),(t,w,t),5,.003)
# Broad stepped cap and corner blocks frame the luminous inner glass volume.
for z,w,h in [(2.31,.25,.085),(2.235,.39,.10),(2.15,.53,.09),(2.075,.61,.07)]:
    b('Stepped iron canopy',(lamp,0,z),(w,w,h),4,.007)
for x in [-1,1]:
    for y in [-1,1]:
        b('Canopy corner fitting',(lamp+x*.27,y*.27,2.055),(.13,.13,.13),5,.006)
        b('Cage corner upright',(lamp+x*.228,y*.228,1.80),(.066,.066,.54),4,.005)
        b('Base corner fitting',(lamp+x*.27,y*.27,1.52),(.13,.13,.13),5,.006)
for z in [1.50,2.04]:b('Cage square rim',(lamp,0,z),(.55,.55,.075),4,.006)
b('Lamp bottom plate',(lamp,0,1.465),(.46,.46,.046),2,.005)
# Four separately modeled inset amber panels. Palette gradients are unlit emission.
for side in [-1,1]:
    b('Amber front glass',(lamp,side*.214,1.775),(.395,.022,.48),13,.004)
    b('Amber side glass',(lamp+side*.214,0,1.775),(.022,.395,.48),14 if side>0 else 13,.004)
b('Lamp glowing inner core',(lamp,0,1.775),(.30,.30,.42),15,.008)
a.studio(focus=(-.10,0,1.57),location=(-5,-8,5.6),scale=3.92)
result=a.save()
