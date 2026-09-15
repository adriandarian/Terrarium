"""Reference-pixel landmarks and an invertible orthographic projection.

Pixels describe visible ground/contact points at explicit elevations. This is
placement evidence, not a claim that rendered image pixels match the reference.
"""
import math
WIDTH,HEIGHT=481,809
CM_PER_PIXEL=5.5
YAW=135;PITCH=-45
R=(-math.sin(math.radians(YAW)),math.cos(math.radians(YAW)))
F=(math.cos(math.radians(YAW)),math.sin(math.radians(YAW)))
UP_H=-math.sin(math.radians(PITCH));UP_Z=math.cos(math.radians(PITCH))

def world(px,py,z):
    right=(px-WIDTH/2)*CM_PER_PIXEL
    forward=((HEIGHT/2-py)*CM_PER_PIXEL-UP_Z*z)/UP_H
    return (R[0]*right+F[0]*forward,R[1]*right+F[1]*forward,z)

def pixel(x,y,z):
    return (WIDTH/2+(R[0]*x+R[1]*y)/CM_PER_PIXEL,HEIGHT/2-(UP_H*(F[0]*x+F[1]*y)+UP_Z*z)/CM_PER_PIXEL)

def inside(point,polygon):
    x,y=point;yes=False
    for (a,b),(c,d) in zip(polygon,polygon[1:]+polygon[:1]):
        if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:yes=not yes
    return yes

UPPER_EDGE=[(187,140),(208,146),(225,158),(239,166),(242,181),(265,187),(279,200),(302,204),(317,207),(332,218),(356,218),(373,229),(399,230),(418,242),(441,247),(482,256),(680,280)]
UPPER=[(165,-300),(700,-300),(700,280)]+list(reversed(UPPER_EDGE))
MAIN_EDGE=[(-180,410),(0,416),(25,420),(45,431),(72,440),(97,438),(125,429),(147,434),(169,428),(190,408),(212,408),(234,417),(257,425),(279,420),(305,406),(337,395),(361,389),(388,374),(420,361),(456,350),(482,337),(700,300)]
MAIN=[(-300,-300),(800,-300),(800,300)]+list(reversed(MAIN_EDGE))+[(-300,410)]
LANDING=[(119,474),(175,455),(219,458),(266,447),(318,427),(371,410),(428,383),(485,367),(650,340),(650,475),(481,495),(443,501),(410,512),(377,509),(346,526),(312,546),(285,555),(265,560),(242,552),(216,558),(193,544),(165,533),(148,516),(122,509)]
SOUTH_EDGE=[(-200,563),(0,606),(30,613),(64,632),(95,648),(126,660),(151,670),(179,665),(207,665),(230,657),(254,648),(283,640),(305,627),(330,611),(355,612),(382,612),(408,593),(436,587),(480,579),(700,537)]
SOUTH=SOUTH_EDGE+[(800,1100),(-300,1100)]
PLATES=[(880,UPPER),(560,MAIN),(280,LANDING),(280,SOUTH)]

def height(x,y):
    for h,poly in PLATES:
        if inside(pixel(x,y,h),poly):return h
    return None

PATH_MAIN=[(60,-30),(88,9),(107,36),(145,70),(128,92),(83,121),(48,157),(35,182),(59,203),(102,222),(126,247),(117,276),(77,316),(46,346),(59,372),(111,404),(157,427)]
PATH_COTTAGE=[(107,393),(149,376),(185,356),(222,339),(231,324)]
PATH_GARDEN=[(222,347),(266,368),(305,392),(349,373),(395,349)]
PATH_LOWER=[(187,474),(214,492),(239,518),(267,549)]
PATH_SOUTH=[(349,612),(383,637),(352,661),(312,687),(266,719),(233,752),(213,788),(202,849)]
PATHS=[(560,PATH_MAIN,128),(560,PATH_COTTAGE,103),(560,PATH_GARDEN,92),(280,PATH_LOWER,131),(280,PATH_SOUTH,130)]
BUILDINGS={'cottage':(260,308,560),'shed':(132,351,560),'well':(351,352,560),'lantern':(273,369,560),'stair_top':(157,429,560),'bridge_deck':(307,579,280)}
WHEAT=[(234,107),(291,78),(508,157),(453,190)]
GARDEN=[(263,351),(330,313),(412,339),(349,382)]
TREES=[(29,91,.72),(68,75,.85),(215,83,.62),(295,63,1.1),(355,67,.65),(465,84,.95),(452,307,.72),(464,442,.85),(421,464,.57),(22,634,.65),(31,682,.75),(448,720,1.0),(340,788,.93),(23,817,.75)]

def distance_segment(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1]
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def path_distance(px,py,h):
    return min([distance_segment((px,py),a,b) for hh,path,_ in PATHS if hh==h for a,b in zip(path,path[1:])]+[1000])
