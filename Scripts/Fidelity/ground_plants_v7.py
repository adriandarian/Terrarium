"""Layered meadow patches and stone accents with irregular density and clear routes."""
import math
import random
from placement import place
from vegetation_v7 import occupied, ground_at_pixel
from vegetation_v7 import GROUPS

SEED = 12091711
# Reference-pixel accents beside terrace lips, feature stones and open meadow.
# Architecture, crops, the traveler and walking routes are masked below.
PATCHES = [
 (27,68,15),(131,99,12),(178,128,11),(226,76,13),(362,62,13),
 (448,190,15),(112,177,15),(170,225,12),(25,256,16),(76,280,12),
 (184,291,11),(344,272,14),(417,289,15),(457,326,12),
 (86,391,13),(211,402,12),(251,409,13),(369,391,13),(437,365,14),
 (129,488,12),(221,474,14),(285,460,14),(371,480,15),(429,481,14),
 (241,538,11),(323,508,13),(31,622,13),(113,647,15),(184,653,13),
 (283,638,12),(409,620,15),(456,663,14),(367,712,15),(298,775,15),
 (103,759,16),(422,779,16),
]


def placements():
    rng = random.Random(SEED)
    results = []
    buckets = {}

    def add(kind, px, py, size):
        h = ground_at_pixel(px, py)
        if h is None or occupied(px,py,h):
            return False
        key = (int(px//4), int(py//4))
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if any(math.hypot(px-x,py-y)<2.6 for x,y in buckets.get((key[0]+dx,key[1]+dy),())):
                    return False
        results.append((kind,px,py,h,size,rng.uniform(0,360)))
        buckets.setdefault(key,[]).append((px,py))
        return True

    # Existing landmarks retain richer plant halos, with mixed-height tufts
    # extending beyond crowns instead of all detail hiding underneath bushes.
    for cx, cy, radius in PATCHES + [(x,y,r*1.4) for x,y,r,_ in GROUPS]:
        budget = rng.randint(7,12)
        accepted = 0
        for _ in range(100):
            if accepted >= budget:
                break
            a = rng.uniform(0, math.tau)
            r = radius * math.sqrt(rng.random())
            px, py = cx+math.cos(a)*r, cy+math.sin(a)*r*.65
            kind = rng.choices(['GroundPlants_v2','MeadowGrass_v2','MeadowFlowers_v2'],[5,4,2])[0]
            if add(kind,px,py,rng.uniform(.95,1.65)):
                accepted += 1

    # Broad formerly empty meadows get disconnected patches, each with an
    # internally coherent mix and its own density. Jitter removes grid rhythm;
    # the slowly varying field leaves some areas open and others richly planted.
    for gy in range(-8,834,29):
        for gx in range(-8,510,31):
            cx,cy = gx+rng.uniform(-13,13),gy+rng.uniform(-12,12)
            field = .5+.25*math.sin(cx/43+cy/67)+.25*math.sin(cx/79-cy/39)
            if field < .25 or rng.random() > .40+field*.55:
                continue
            h = ground_at_pixel(cx,cy)
            if h is None or occupied(cx,cy,h):
                continue
            budget = int(4+field*13)
            fern_patch = rng.random()<.52
            radius = rng.uniform(10,20)
            for _ in range(budget*2):
                if budget <= 0:
                    break
                angle = rng.uniform(0,math.tau)
                distance = radius*math.sqrt(rng.random())
                px,py = cx+math.cos(angle)*distance,cy+math.sin(angle)*distance*.72
                kind = rng.choices(['GroundPlants_v2','MeadowGrass_v2','MeadowFlowers_v2'],
                                   [7,3,1] if fern_patch else [2,8,1])[0]
                if add(kind,px,py,rng.uniform(.85,1.75)):
                    budget -= 1
            # Occasional little exposed stones provide a different shape and
            # value at patch edges. They stay much smaller than landmark rocks.
            if rng.random()<.40:
                add('RockCluster',cx+rng.uniform(-15,15),cy+rng.uniform(-10,10),rng.uniform(.17,.40))
    return results


def build(cells):
    for kind, px, py, h, size, yaw in placements():
        place(kind,px,py,h+1,size,yaw,'GroundPlantAccents')
