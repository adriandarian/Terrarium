"""Seeded, path-aware orchard and low shrubs; no gameplay or runtime scatter."""
from placement import place,rng,distance_to_path
from terrain import height,river
from paths import UPPER,LOWER,SOUTH,DOOR

def excluded(u,v,h):
    if -670<u<240 and -150<v<640:return True
    if 130<u<810 and -205<v<520:return True
    if -170<u<1180 and 850<v<1830:return True
    if -440<u<-160 and -700<v<-270:return True
    if 365<u<670 and -1530<v<-880:return True
    return any(distance_to_path(u,v,p)<145 for p in [UPPER,LOWER,SOUTH,DOOR])

def build():
    trees=[]
    for i in range(220):
        u=rng.uniform(-2200,2200);v=rng.uniform(-3000,3000);h=height(u,v)
        if h is None or excluded(u,v,h) or any((u-x)**2+(v-y)**2<240**2 for x,y in trees):continue
        if -900<u<950 and -900<v<750:continue
        if -100<u<1100 and -1870<v<-730:continue
        if -300<u<1300 and 600<v<1900:continue
        trees.append((u,v));s=rng.uniform(.72,1.20)
        place('OrchardTree',u,v,h+5,(s,s,s*rng.uniform(.87,1.12)),rng.uniform(0,360),'Vegetation/Trees')
    for i in range(900):
        u=rng.uniform(-2100,2100);v=rng.uniform(-3000,3000);h=height(u,v)
        if h is None or excluded(u,v,h):continue
        s=rng.uniform(.23,.72)
        place('Bush',u,v,h+7,(s,s*rng.uniform(.8,1.3),s),rng.uniform(0,360),'Vegetation/Shrubs')
    # Broad shrubs anchor the building cluster without hiding doors or crops.
    for u,v,s in [(-740,-130,.9),(-630,120,.75),(180,570,.9),(880,370,.9),(800,-80,.65),(-80,-260,.65),(-600,-710,.7),(70,-900,.6)]:
        h=height(u,v)
        if h is not None:place('Bush',u,v,h+8,s,rng.uniform(0,360),'Vegetation/FeatureShrubs')
    for i in range(450):
        u=rng.uniform(-2100,2100);v=rng.uniform(-2800,2800);h=height(u,v)
        if h is None or excluded(u,v,h):continue
        mesh='Wildflowers' if i%4 else 'RockCluster'
        s=rng.uniform(.65,1.35)
        place(mesh,u,v,h+7,s,rng.uniform(0,360),'Vegetation/MeadowDetails')
    for u in range(-1800,1801,85):
        if 360<u<700:continue
        for side in [-1,1]:
            v=river(u)+side*210+rng.uniform(-25,25)
            if height(u,v) is None:
                place('Reeds',u,v,5,rng.uniform(.8,1.25),rng.uniform(0,360),'River/Reeds')
                if u%3==0:place('RockCluster',u+35,v-10,1,rng.uniform(.8,1.8),rng.uniform(0,360),'River/Stones')
