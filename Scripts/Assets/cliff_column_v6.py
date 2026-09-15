"""Three overlapping fractured-rock columns with displaced, chipped masses.

Origin and maximum height (323.5 cm) retain the terrain_v8 contract. Rock
fractures are actual displaced convex solids, not brick-face decoration.
"""
from meshkit import Mesh


def _chunk(m, pos, size, tint, yaw=0):
    """Sheared convex octagon with unequal corner breaks and broad end chips."""
    hx, hy, height = size[0]/2, size[1]/2, size[2]
    cuts = [m.rng.uniform(.12, .32)*min(hx, hy) for _ in range(4)]
    outline = [(-hx+cuts[0], -hy), (hx-cuts[1], -hy),
               (hx, -hy+cuts[1]), (hx, hy-cuts[2]),
               (hx-cuts[2], hy), (-hx+cuts[3], hy),
               (-hx, hy-cuts[3]), (-hx, -hy+cuts[0])]
    # A shear changes the normals of the large side faces. Ring profiles keep
    # the rock convex and avoid identical bevels on every fracture boundary.
    shear_x, shear_y = m.rng.uniform(-5, 5), m.rng.uniform(-5, 5)
    lower, upper = m.rng.uniform(.10, .19), m.rng.uniform(.12, .24)
    rings = [(m.rng.uniform(.76, .87), -.5), (1, -.5+lower),
             (1, .5-upper), (m.rng.uniform(.76, .91), .5)]
    vertices = [(x*scale+shear_x*z, y*scale+shear_y*z, z*height)
                for scale, z in rings for x, y in outline]
    faces = [list(range(7, -1, -1)), list(range(24, 32))]
    for ring in range(3):
        for i in range(8):
            j = (i+1) % 8
            faces.append([ring*8+i, ring*8+j, (ring+1)*8+j, (ring+1)*8+i])
    m.solid(vertices, faces, tint, pos=pos, rot=(0, 0, yaw), variation=.035)


def recipe(variant='A'):
    if variant not in ('A', 'B', 'C'):
        raise ValueError('Cliff variant must be A, B or C')
    index = ord(variant)-ord('A')
    m = Mesh('SM_CliffColumn_v6'+variant, 641+index*149)
    m.refinement_pass = 8
    m.revises = 'SM_CliffColumn_v5'+variant
    # This recessed interior preserves continuous terrain coverage beneath the
    # intersecting rock masses, including their deepest corner fractures.
    m.box((0, 0, 153), (84, 84, 306), '535940', 4, variation=.015)
    colors = ['727254', '807b59', '686d50', '8a8060', '737657', '626a4c']
    # Each variant has different fracture levels. Pieces span the column width;
    # none repeats the previous four uninterrupted narrow vertical corner stacks.
    weights = ([1.12, .77, 1.25, .96, 1.04],
               [.84, 1.17, .91, 1.24, .97],
               [1.21, .96, 1.11, .80, 1.04])[index]
    levels = [0]
    for weight in weights:
        levels.append(levels[-1]+309*weight/sum(weights))
    for layer, (bottom, top) in enumerate(zip(levels, levels[1:])):
        # 6cm overlap prevents mortar-like holes between chipped ends.
        low = max(0, bottom-6)
        high = min(314, top+6)
        _chunk(m, (m.rng.uniform(-2, 2), m.rng.uniform(-2, 2), (low+high)/2),
               (m.rng.uniform(99, 107), m.rng.uniform(99, 107), high-low),
               colors[(layer+index*2) % len(colors)], m.rng.uniform(-5, 5))
        # Selected deep side fractures break the main face with a projecting
        # rock shoulder. They intersect the parent chunk, including at roots.
        axis = (layer+index) % 2
        sign = -1 if (layer+index) % 3 else 1
        pos = [m.rng.uniform(-22, 22), m.rng.uniform(-22, 22),
               bottom+(top-bottom)*m.rng.uniform(.35, .65)]
        pos[axis] = sign*m.rng.uniform(36, 39)
        size = [m.rng.uniform(45, 58), m.rng.uniform(44, 57),
                (top-bottom)*m.rng.uniform(.63, .90)]
        size[axis] = m.rng.uniform(28, 34)
        pos[2] = max(size[2]/2, min(314-size[2]/2, pos[2]))
        _chunk(m, tuple(pos), tuple(size), m.rng.choice(colors),
               m.rng.uniform(-7, 7))

    # Three unequal turf plates rather than a regular nine-square cap grid.
    # They overlap the upper rock and each other. One fixes exact maximum Z.
    for part, (x, y, sx, sy) in enumerate(((-24, -19, 65, 71),
                                          (24, -8, 65, 91),
                                          (-13, 29, 88, 55))):
        height = m.rng.uniform(17, 23)
        top = 323.5 if part == 0 else m.rng.uniform(320, 323.2)
        _chunk(m, (x, y, top-height/2), (sx, sy, height),
               ['75813b', '81893f', '697b34'][(part+index) % 3],
               m.rng.uniform(-3, 3))
    # Small irregular moss pockets grow in selected fractures; no all-around
    # horizontal green stripe or thin floating face decals.
    for side in range(3):
        axis, sign = (side+index) % 2, (-1 if side % 2 else 1)
        p = [m.rng.uniform(-23, 23), m.rng.uniform(-23, 23), m.rng.uniform(282, 303)]
        p[axis] = sign*46
        for drop in range(2 + (side+index) % 2):
            q = (p[0], p[1], p[2]-drop*10)
            size = [m.rng.uniform(17, 23), m.rng.uniform(17, 23), 15]
            size[axis] = 23
            _chunk(m, q, tuple(size), m.rng.choice(['617430', '74803a', '596d32']))
    return m


def build(variant='A'):
    return recipe(variant).save()


def build_variants():
    return {variant: build(variant) for variant in ('A', 'B', 'C')}
