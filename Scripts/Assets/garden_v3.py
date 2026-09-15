"""A productive mixed kitchen garden with broad soil beds and modest yard detail."""
import math
from meshkit import Mesh


def build_mesh():
    m = Mesh('SM_GardenBed_v3', 16073)
    m.refinement_pass = 3
    m.revises = 'SM_GardenBed_v2'
    m.box((0, 0, 7), (275, 225, 16), '594831', 5)
    # Low worn edging keeps the plants, rather than the raised frame, prominent.
    for x in (-139, 139):
        for y in (-57, 57):
            m.box((x, y, 13), (9, 111, 18), 'wood', 2,
                  rot=(0, 0, m.rng.uniform(-1.5, 1.5)))
        for y in (-110, 5, 110):
            m.box((x, y, 17), (12, 12, 27), 'wood_dark', 2)
    for y in (-115, 115):
        for x in (-70, 70):
            m.box((x, y, 13), (136, 9, 18), 'wood_light', 2,
                  rot=(0, 0, m.rng.uniform(-1, 1)))
    for row in range(4):
        y = -84 + row * 55
        m.box((0, y, 17), (252, 37, 10), '685438', 3)
        for col in range(6):
            x = -109 + col * 43 + m.rng.uniform(-3, 3)
            yy = y + m.rng.uniform(-3, 3)
            size = m.rng.uniform(.8, 1.12)
            # Three crop silhouettes: leafy cabbage, low red produce, and
            # narrow upright carrot/herb foliage. Heights remain below the well.
            kind = (row + col // 3) % 3
            if kind == 2:
                m.ellipsoid((x, yy, 23), (12, 13, 13), 'ad632f', 6, 3)
                for k in range(6):
                    a = k * math.tau / 6
                    end = (x + math.cos(a) * 15 * size,
                           yy + math.sin(a) * 15 * size, 42 * size)
                    m.beam((x, yy, 24), end, 3.2, 'crop')
                    m.ellipsoid(end, (7, 9, 18), '729545', 5, 3,
                                rot=(0, 20, math.degrees(a)))
            else:
                m.ellipsoid((x, yy, 29), (26 * size, 27 * size, 22 * size),
                            '536932', 7, 3)
                for k in range(6):
                    a = k * math.tau / 6 + m.rng.uniform(-.15, .15)
                    dx, dy = math.cos(a) * 12 * size, math.sin(a) * 12 * size
                    m.ellipsoid((x + dx, yy + dy, 30),
                                (24 * size, 18 * size, 10 * size),
                                m.rng.choice(('526c32', '708141', '81934b')), 6, 3,
                                rot=(0, 0, math.degrees(a)))
                if kind == 0:
                    m.ellipsoid((x, yy, 38), (22 * size, 23 * size, 20 * size),
                                '84984f', 7, 3)
                else:
                    for dx, dy in ((-7, -4), (7, 1), (0, 8)):
                        m.ellipsoid((x + dx, yy + dy, 38), (11, 11, 12),
                                    m.rng.choice(('b64a29', 'c36832')), 6, 3)
                        m.box((x + dx, yy + dy, 44), (4, 4, 2.5), 'leaf_dark', .5)
    # A small harvest crate sits along one side; loose stones and a hand tool
    # suggest use without building a second large visual feature in the yard.
    cx, cy = 156, 69
    m.box((cx, cy, 5), (24, 37, 5), 'wood_dark', 1)
    for x in (cx - 13, cx + 13):
        for z in (10, 20):
            m.box((x, cy, z), (4, 40, 7), 'wood', 1)
    for y in (cy - 19, cy + 19):
        for z in (10, 20):
            m.box((cx, y, z), (27, 4, 7), 'wood_light', 1)
    for y in (cy - 11, cy, cy + 11):
        m.ellipsoid((cx, y, 15), (11, 11, 10), 'fruit', 6, 3)
    m.beam((-155, -68, 7), (-149, -21, 11), 3, 'wood_light')
    m.box((-155, -73, 6), (11, 15, 3), 'metal', 1, rot=(0, 0, -7))
    for _ in range(23):
        x, y = m.rng.uniform(-129, 129), m.rng.uniform(-105, 105)
        m.ellipsoid((x, y, 16), (4, 5, 3), '8d8268', 5, 2)
    return m


def build():
    return build_mesh().save()
