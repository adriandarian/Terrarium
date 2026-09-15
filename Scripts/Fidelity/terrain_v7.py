"""Finer traced terraces with stepped rock shelves and broken cliff profiles.

The returned grid retains reference.height at every sampled point. Additional
shelves occupy only the lower side of an exposed edge, away from paths and
landmarks, so downstream placement keeps the existing height contract.
"""
import math
import random

from placement import place_xyz
import reference as ref

CELL = 72
DIRECTIONS = ((CELL, 0), (-CELL, 0), (0, CELL), (0, -CELL))
CLIFF_HEIGHT = 323.5


def protected(x, y, h, margin=20):
    px, py = ref.pixel(x, y, h)
    if ref.path_distance(px, py, h) < margin:
        return True
    return any(math.hypot(x-ref.world(px, py, z)[0],
                          y-ref.world(px, py, z)[1]) < 190
               for px, py, z in ref.BUILDINGS.values())


def sample_cells():
    cells = {}
    for x in range(-3900, 3901, CELL):
        for y in range(-4400, 4401, CELL):
            h = ref.height(x, y)
            if h is None:
                continue
            px, py = ref.pixel(x, y, h)
            if -150 < px < 630 and -150 < py < 960:
                cells[x, y] = h
    return cells


def shelf_specs(cells):
    """Deterministic non-floating ledges; returns XYZ, width, lower height."""
    randomizer = random.Random(705)
    result = []
    for (x, y), h in cells.items():
        if protected(x, y, h):
            continue
        for dx, dy in DIRECTIONS:
            lower = ref.height(x+dx, y+dy)
            if h==280 and lower is None:
                px,py=ref.pixel(x+dx,y+dy,0)
                if not (-30<px<515 and 485<py<715):
                    continue
                lower=0
            if lower is None or lower >= h-180:
                continue
            # Broad intermittent runs replace the old uninterrupted wall.
            wave = math.sin(x/187+y/263) + .55*math.sin(y/109-x/331)
            if wave < .32 or randomizer.random() > .58:
                continue
            cx, cy = x+dx*.64, y+dy*.64
            if protected(cx, cy, lower, 24):
                continue
            top = h-randomizer.choice((76, 108, 144))
            width = CELL*randomizer.uniform(.80, 1.10)
            # Extends into the lower cell, overlaps the parent rock face.
            result.append((cx, cy, top, width, lower))
    return result


def rock_stack(x, y, top, bottom, width, randomizer, group):
    span = top-bottom
    count = max(1, math.ceil(span/CLIFF_HEIGHT))
    for index in range(count):
        segment = span/count
        # 84 cm continuous core in CliffColumn_v4; overlap adjacent cores.
        scale = width/84*1.025
        place_xyz(randomizer.choice(('CliffColumn_v5A','CliffColumn_v5B','CliffColumn_v5C')), (x, y, bottom+index*segment),
                  (scale, scale, segment/CLIFF_HEIGHT),
                  randomizer.choice((0, 90, 180, 270)), group)


def build():
    randomizer = random.Random(70519)
    cells = sample_cells()
    for (x, y), h in cells.items():
        lower = min(cells.get((x+dx, y+dy), 0) for dx, dy in DIRECTIONS)
        meadow='MeadowTile_Edge_v6' if lower<h else 'MeadowTile_v5'
        place_xyz(meadow, (x, y, h),
                  (CELL/200*1.02, CELL/200*1.02, 1),
                  randomizer.choice((0, 90, 180, 270)), 'Terrain')
        if lower >= h:
            continue
        rock_stack(x, y, h+7, lower-8, CELL, randomizer, 'Terrain')

    for x, y, top, width, lower in shelf_specs(cells):
        rock_stack(x, y, top, lower-7, width, randomizer, 'CliffLedges')
        place_xyz('MeadowTile_Edge_v6', (x, y, top),
                  (width/200, width/200, .55),
                  randomizer.choice((0, 90, 180, 270)), 'CliffLedges')

    import water_v7
    water_v7.build(cells)
    return cells
