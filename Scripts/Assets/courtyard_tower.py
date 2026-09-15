"""Stone-footed timber lantern tower traced from the courtyard concept."""
from meshkit import Mesh
import math

def build():
    m=Mesh('SM_CourtyardTower_Reference',12931)
    m.box((0,0,8),(139,129,16),'666b58',4)
    for row,(span,z) in enumerate([(120,29),(105,56),(91,82)]):
        for side in (-1,1):
            for k in (-1,1):
                m.box((k*span/4,side*(span/2-13),z),(span/2-3,27,25),m.rng.choice(['81836d','92927c','727965']),3)
            m.box((side*(span/2-13),0,z),(27,span-51,25),'787d69',3)
    m.box((0,0,103),(93,88,16),'575945',3)
    # A solid timber lantern housing above the masonry, not an open well.
    m.box((0,0,160),(61,59,100),'6d552e',3)
    for z in (116,183,223):m.box((0,0,z),(77,75,12),'4e4931',2.5)
    for x in (-35,35):
        for y in (-34,34):
            m.box((x,y,181),(13,13,156),'594c2e',2.5)
            m.box((x,y,255),(17,17,11),'8b7948',2)
    # Warm inset panes, narrow vertical bars, and darker side returns.
    for side in (-1,1):
        m.box((0,side*31,204),(48,4,34),'bc9a45',1)
        m.box((side*32,0,204),(4,44,34),'9e823a',1)
        for q in (-16,0,16):
            m.box((q,side*35,204),(3,5,38),'4b4b32',.6)
            m.box((side*36,q,204),(5,3,38),'4b4b32',.6)
        for x in (-25,25):m.beam((x,side*36,128),(-x,side*36,171),5,'wood_dark')
    m.box((0,0,263),(84,79,10),'696b4e',2.5)
    for x in (-35,35):
        for y in (-31,31):m.beam((x,y,269),(x*.55,y*.55,307),7,'50563f')
    m.box((0,0,310),(54,47,12),'74785a',3)
    m.box((0,0,326),(21,19,22),'545b40',3)
    for x,y in [(-57,29),(31,57),(54,-39)]:
        m.box((x,y,13),(23,24,13),'687a38',3)
    return m.save()
