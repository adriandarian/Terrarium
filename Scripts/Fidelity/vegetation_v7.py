"""Sparse reference clusters with open clearings and narrower tiered trees.

Ground plants and shoreline dressing are separate pass-seven modules. Pixel
positions remain tied to the reference composition rather than terrain cell order.
"""
import math
import random
import reference as ref
from placement import place
from vegetation import occupied as previous_occupied

SEED = 12091709
GROUND_LEVELS = (880, 560, 280)


def ground_at_pixel(px, py):
    """Resolve the highest visible supported surface, including edited terraces."""
    for h in GROUND_LEVELS:
        x, y, _ = ref.world(px, py, h)
        supported = ref.height(x, y)
        if supported is not None and abs(supported-h) < .001:
            return h
    return None


def occupied(px, py, h):
    """Keep walking routes, architecture, and traveler silhouette visibly clear."""
    if previous_occupied(px, py, h):
        return True
    if h == 560:
        if abs(px-306)/39 + abs(py-356)/29 < 1.1:
            return True
        if abs(px-379)/22 + abs(py-348)/17 < 1.1:
            return True
        # Extend the old foundation-only mask upward across the cottage roof.
        if 200 < px < 316 and 226 < py < 347:
            return True
        if 155 < px < 199 and 361 < py < 409:
            return True
        if 95 < px < 164 and 315 < py < 368:
            return True
    if h not in (280, 560, 880):
        # Arbitrary new ledges still respect routes at the established levels.
        x, y, _ = ref.world(px, py, h)
        for level in (280, 560, 880):
            qx, qy = ref.pixel(x, y, level)
            if ref.path_distance(qx, qy, level) < 15:
                return True
        for qx, qy, level in ref.BUILDINGS.values():
            bx, by, _ = ref.world(qx, qy, level)
            if math.hypot(x-bx, y-by) < 185:
                return True
    return False


# Existing traced group anchors; the final value is the previous candidate
# budget. Dominant, mid-size and tiny patches use distinct densities and scale.
GROUPS=[
 (13,23,19,10),(42,50,17,8),(93,64,12,6),(157,37,18,9),(210,32,15,6),
 (245,23,15,8),(359,22,19,8),(405,35,22,12),(458,29,22,12),(24,111,20,12),
 (83,92,11,6),(141,103,15,9),(163,136,14,7),(208,94,15,10),(239,72,11,7),
 (342,71,12,5),(376,95,10,5),(465,190,18,9),(439,209,15,6),
 (9,193,16,10),(42,236,17,11),(90,185,15,8),(112,201,14,6),(138,233,18,11),
 (170,192,15,7),(184,227,15,8),(164,267,16,9),(147,295,12,6),(188,299,12,7),
 (347,266,19,10),(396,275,17,9),(453,283,24,14),(476,323,19,10),
 (14,314,17,10),(34,288,16,8),(80,290,13,8),(93,317,12,7),(166,354,13,8),
 (208,406,12,7),(238,412,10,5),(264,414,12,7),(78,406,18,9),(27,397,18,10),
 (298,421,19,11),(350,407,16,8),(389,388,15,9),(453,363,18,10),
 (128,474,12,8),(111,491,13,8),(202,479,13,9),(226,504,12,7),(285,458,22,12),
 (327,435,22,12),(381,454,24,12),(425,428,23,14),(472,466,19,10),
 (290,516,16,9),(244,536,15,9),(189,534,13,8),(338,505,17,10),(456,501,15,8),
 (26,612,20,12),(69,633,20,11),(117,649,17,10),(162,653,14,8),(197,644,15,8),
 (257,643,20,11),(302,623,15,8),(398,610,19,10),(447,594,23,12),
 (467,648,24,16),(412,679,18,10),(366,706,19,11),(447,735,28,16),
 (331,765,22,13),(289,778,20,10),(397,795,24,13),(36,785,25,12),(116,811,23,12)
]

FEATURE_STONES = [
    (161,338,1.1),(322,282,.9),(379,487,1.65),(421,515,.8),
    (95,469,.7),(245,172,.65),(31,198,.7),(450,768,1.1),
    (183,277,.55),(462,184,.6),
]


def build(cells):
    # Resolve terrain_v8 edits before ground plants import this resolver too.
    global GROUND_LEVELS
    GROUND_LEVELS = tuple(sorted(set(cells.values()) | {880,560,280}, reverse=True))
    rng = random.Random(SEED)
    for px, py, reference_scale in ref.TREES:
        h = ground_at_pixel(px, py)
        if h is not None:
            # Both recipes are approximately 384 cm high. Preserve the reference
            # height while Tree_v3 supplies a much narrower branching silhouette.
            place('Tree_v3', px, py, h + 5, reference_scale * 1.12,
                  rng.uniform(0, 360), 'Trees')

    shrub_centers = []

    def add_shrub(px, py, h, size, group):
        if h is None or occupied(px, py, h):
            return False
        if any(math.hypot(px-x, py-y) < 3.8 for x,y,zh in shrub_centers):
            return False
        place('Bush_v2', px, py, h+3, size, rng.uniform(0,360), group)
        shrub_centers.append((px, py, h))
        return True

    for index, (cx, cy, radius, old_budget) in enumerate(GROUPS):
        # Irregular size classes intentionally interrupt the formerly equal
        # neighboring colonies. Only dominant patches receive larger crowns.
        selector = (index * 7 + int(cx) * 3 + int(cy)) % 10
        if selector < 3:
            budget, spread, sizes = math.ceil(old_budget*1.35), .79, (.50,.89)
        elif selector < 7:
            budget, spread, sizes = math.ceil(old_budget*.95), .64, (.34,.66)
        else:
            budget, spread, sizes = max(2,math.ceil(old_budget*.38)), .47, (.24,.47)
        accepted = 0
        for _ in range(budget * 8):
            if accepted >= budget:
                break
            angle = rng.uniform(0, math.tau)
            distance = radius * spread * math.sqrt(rng.random())
            px = cx + math.cos(angle)*distance
            py = cy + math.sin(angle)*distance*.62
            h = ground_at_pixel(px, py)
            if add_shrub(px,py,h,rng.uniform(*sizes),'ReferenceShrubClusters'):
                accepted += 1

    # New lowered lips previously stayed completely bare: a few isolated small
    # crowns punctuate exposed rock shelves. This uses actual cell elevations,
    # not assumed 280/560/880 planes, with visible gaps between the accents.
    terrace_accents = []
    for (x,y),h in sorted(cells.items()):
        if h in (280,560,880) or h < 65:
            continue
        px,py = ref.pixel(x,y,h)
        if not (3<px<478 and 35<py<795):
            continue
        # Coherent, intermittent zones instead of every-cell edge planting.
        if math.sin(x/173-y/249) < .24 or rng.random() > .34:
            continue
        if any(math.hypot(px-qx,py-qy)<16 for qx,qy in terrace_accents):
            continue
        if any(math.hypot(px-qx,py-qy)<10 for qx,qy,qh in shrub_centers):
            continue
        if ref.height(x,y) != h:
            continue
        if add_shrub(px,py,h,rng.uniform(.25,.48),'TerraceShrubAccents'):
            terrace_accents.append((px,py))

    # Small, isolated meadow shrubs add shape between major clusters without
    # rebuilding the removed hedge chains. Low-frequency density and generous
    # gaps leave these as accents rather than an even scatter carpet.
    meadow_rng = random.Random(SEED+91)
    for gy in range(8,825,25):
        for gx in range(3,489,27):
            px,py = gx+meadow_rng.uniform(-10,10),gy+meadow_rng.uniform(-10,10)
            density = .5+.3*math.sin(px/51+py/71)+.2*math.sin(px/33-py/83)
            if density < .34 or meadow_rng.random() > density*.58:
                continue
            h = ground_at_pixel(px,py)
            if any(math.hypot(px-qx,py-qy)<11 for qx,qy,qh in shrub_centers):
                continue
            add_shrub(px,py,h,meadow_rng.uniform(.28,.54),'SmallMeadowShrubs')

    for px, py, size in FEATURE_STONES:
        h = ground_at_pixel(px, py)
        if h is not None:
            place('RockCluster', px, py, h + 1, size,
                  rng.uniform(0, 360), 'FeatureStones')
