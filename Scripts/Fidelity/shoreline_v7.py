"""Intermittent supported river shelves, wet stones, and reed pockets.

Uses actual exposed 72 cm terrain cells. Placement is locally seeded and
independent of vegetation order. specs() is offline-testable without Unreal.
"""
import math
import random
import sys
import reference as ref

CELL = 72
DIRECTIONS = ((CELL, 0), (-CELL, 0), (0, CELL), (0, -CELL))
BRIDGE_A = ref.world(267, 549, 280)[:2]
BRIDGE_B = ref.world(349, 612, 280)[:2]


def bridge_clear(x, y):
    return ref.distance_segment((x, y), BRIDGE_A, BRIDGE_B) > 180


def bank_candidates(cells):
    """Cell banks plus actual outer edges of the structural river shelves."""
    broad = []
    terrain = sys.modules.get('terrain_v8')
    if terrain is not None and ref.height is terrain.height_at:
        broad = [s for s in terrain.terrain_specs()[4] if s[4] == 0]
    candidates = []
    for (x, y), h in sorted(cells.items()):
        if h is None or h <= 0:
            continue
        for dx, dy in DIRECTIONS:
            if ref.height(x+dx, y+dy) is not None:
                continue
            cx, cy = x+dx*.53, y+dy*.53
            if any(abs(cx-bx) < width*.52 and abs(cy-by) < width*.52
                   for bx, by, top, width, lower in broad):
                continue
            candidates.append((cx, cy, h, dx, dy))
    for x, y, top, width, lower in broad:
        for dx, dy in DIRECTIONS:
            cx, cy = x+dx/CELL*width*.49, y+dy/CELL*width*.49
            if ref.height(cx+dx*.35, cy+dy*.35) is not None:
                continue
            candidates.append((cx, cy, top, dx, dy))
    return candidates


def specs(cells):
    randomizer = random.Random(71329)
    selected = []
    placements = []
    for x, y, h, dx, dy in bank_candidates(cells):
        # Only visible river banks; exclude out-of-frame map boundaries.
        px, py = ref.pixel(x+dx, y+dy, 0)
        if not (-40 < px < 525 and 455 < py < 740):
            continue
        cx, cy = x, y
        if not bridge_clear(cx, cy):
            continue
        # Long quiet sections alternate with pockets, never a border row.
        pocket = math.sin(x/247+y/173)+.6*math.sin(y/93-x/169)
        if pocket < -.35 or randomizer.random() > .85:
            continue
        if any(math.hypot(cx-ax, cy-ay) < 100 for ax, ay in selected):
            continue
        selected.append((cx, cy))
        yaw = math.degrees(math.atan2(dy, dx)) + randomizer.uniform(-14, 14)
        sx = randomizer.uniform(.75, 1.24)
        sy = randomizer.uniform(.68, 1.20)
        sz = randomizer.uniform(.50, min(1.3, max(.55, h*.75/110)))
        origin_z = -randomizer.uniform(3, 17)
        variant = 'ShoreOutcrop' if randomizer.random() < .68 else 'ShoreOutcrop_v2'
        placements.append((variant, (cx, cy, origin_z),
                           (sx, sy, sz), yaw, 'RiverShelves'))
        # Rotate local attachment points with the shelf, keeping reed roots
        # inside the broad middle stone top (57 cm before scaling).
        a = math.radians(yaw)
        def point(lx, ly, lz):
            return (cx+math.cos(a)*lx*sx-math.sin(a)*ly*sy,
                    cy+math.sin(a)*lx*sx+math.cos(a)*ly*sy,
                    origin_z+lz*sz)
        if randomizer.random() < .74:
            reed_anchor = (31, 26, 77) if variant == 'ShoreOutcrop' else (30, -15, 59)
            placements.append(('Reeds', point(*reed_anchor),
                               randomizer.uniform(.38, .68),
                               randomizer.uniform(0, 360), 'RiverPlants'))
        if randomizer.random() < .43:
            # Small low bush is rooted in the landward moss shelf.
            moss_anchor = (-44, 18, 113) if variant == 'ShoreOutcrop' else (-29, 0, 104)
            placements.append(('Bush_v2', point(*moss_anchor),
                               randomizer.uniform(.22, .40),
                               randomizer.uniform(0, 360), 'RiverMoss'))
    return placements


def river_stone_specs(items):
    """Unequal river pockets with quiet intervals and varied submergence."""
    rng=random.Random(712813)
    selected=[]
    result=[]
    for name,xyz,scale,yaw,group in items:
        if name not in ('ShoreOutcrop', 'ShoreOutcrop_v2'):continue
        # Selected pockets, not a stone ribbon extending from every bank cell.
        if rng.random()<.30:continue
        angle=math.radians(yaw)
        pocket_reach=rng.uniform(95,190)
        pocket_along=rng.uniform(-65,65)
        for _ in range(rng.choice((1,2,3,4))):
            reach=pocket_reach+rng.uniform(-48,48)
            along=pocket_along+rng.uniform(-70,70)
            x=xyz[0]+math.cos(angle)*reach-math.sin(angle)*along
            y=xyz[1]+math.sin(angle)*reach+math.cos(angle)*along
            if ref.height(x,y) is not None or not bridge_clear(x,y):continue
            if any(math.hypot(x-px,y-py)<48 for px,py in selected):continue
            selected.append((x,y))
            sx,sy,sz=rng.uniform(.62,1.10),rng.uniform(.60,1.12),rng.uniform(.58,1.02)
            # High crowns break water; some secondary stones remain submerged.
            z=-29*sz*rng.uniform(.36,.68)
            result.append(('RiverStones_v2',(x,y,z),(sx,sy,sz),
                           rng.uniform(0,360),'ShallowRiverStones'))
    return result


def build(cells):
    from placement import place_xyz
    items=specs(cells)
    for name, xyz, scale, yaw, group in items+river_stone_specs(items):
        place_xyz(name, xyz, scale, yaw, group)
