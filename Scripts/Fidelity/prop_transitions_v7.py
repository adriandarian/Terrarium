"""Small grounded wear and planting pockets at bridge and stair contacts.

Uses the exact paths_v7 transforms and final reference.height. No foundation
platforms or walking-surface clutter: soil is a nearly flush irregular patch,
and stones/plants are confined to the shoulders.
"""
import math
import random
import reference as ref

LAST_REPORT = {}


def anchor(kind):
    if kind == 'bridge':
        x, y, _ = ref.world(306, 579, 280)
        return (x, y, 222), (.9, 1.4, 1), -4
    top = ref.world(157, 429, 560)
    a = math.radians(2)
    return (top[0] + math.sin(a)*147*.75,
            top[1] - math.cos(a)*147*.75, 280), (1, .75, 280/249), 2


def to_world(kind, x, y):
    origin, scale, yaw = anchor(kind)
    a = math.radians(yaw)
    return (origin[0] + math.cos(a)*x*scale[0] - math.sin(a)*y*scale[1],
            origin[1] + math.sin(a)*x*scale[0] + math.cos(a)*y*scale[1])


def supported(x, y, radius):
    """Reject river overhangs and height breaks across the whole detail pocket."""
    h = ref.height(x, y)
    if h is None:
        return None
    for i in range(12):
        a = math.tau*i/12
        if ref.height(x + math.cos(a)*radius, y + math.sin(a)*radius) != h:
            return None
    return h


def records(cells):
    if not cells:
        raise ValueError('Build terrain before prop transitions')
    rng = random.Random(170807)
    result = []

    def add(kind, zone, name, lx, ly, scale, radius, offset):
        x, y = to_world(kind, lx, ly)
        h = supported(x, y, radius)
        if h is None:
            return
        result.append(dict(name=name, xyz=(x, y, h+offset), scale=scale,
                           yaw=rng.uniform(0, 360), group='PropTransitions',
                           prop=kind, zone=zone, local=(lx, ly), ground=h,
                           radius=radius))

    for sign, zone in ((-1, 'near_abutment'), (1, 'far_abutment')):
        # Three small wear patches connect the timber end to the earth path.
        # At this distance they are beyond the plank ends, not on the bridge.
        for x in (-40, 15, 60):
            add('bridge', zone, 'PathTile_v4', x, sign*315,
                (.21, .16, .25), 33, 6.25)
        # Landward shoulders are asymmetric; full-footprint sampling naturally
        # omits pockets over the river rather than inventing supporting land.
        for side in (-1, 1):
            for index, y in enumerate((283, 317, 347)):
                add('bridge', zone, 'RockCluster', side*128, sign*y,
                    .32, 25, 0)
                add('bridge', zone, 'MeadowGrass_v2', side*143, sign*(y+8),
                    .68, 18, 4)
                if index != 1:
                    add('bridge', zone, 'GroundPlants_v2', side*151, sign*(y+17),
                        .52, 23, 3)

    # Worn earth ends just outside the lowest and highest stone treads.
    for sign, zone in ((-1, 'stair_foot'), (1, 'stair_head')):
        for x in (-58, -8, 44):
            add('stairs', zone, 'PathTile_v4', x, sign*194,
                (.18, .14, .25), 29, 6.25)
        for side in (-1, 1):
            add('stairs', zone, 'RockCluster', side*140, sign*177,
                .30, 23, 0)
            add('stairs', zone, 'MeadowGrass_v2', side*146, sign*193,
                .64, 17, 4)
            add('stairs', zone, 'GroundPlants_v2', side*159, sign*213,
                .55, 24, 3)

    # Sparse contacts along the side masonry, rooted at the actual ground level
    # beside the stair, never at an assumed interpolated tread elevation.
    for side, ys in ((-1, (-103, 33)), (1, (-61, 79))):
        for y in ys:
            add('stairs', 'stair_sides', 'RockCluster', side*143, y,
                .32, 25, 0)
            add('stairs', 'stair_sides', 'MeadowGrass_v2', side*149, y+17,
                .66, 18, 4)
    return result


def build(cells):
    from placement import place_xyz
    from collections import Counter
    items = records(cells)
    for item in items:
        place_xyz(item['name'], item['xyz'], item['scale'], item['yaw'], item['group'])
    LAST_REPORT.clear()
    LAST_REPORT.update(instances=len(items),
                       zones=dict(Counter(item['zone'] for item in items)),
                       meshes=dict(Counter(item['name'] for item in items)),
                       full_footprint_ground_checks=True)
    return items
