"""Three deterministic fractured-rock columns for mixed terrain placement.

build('A'|'B'|'C') returns a new StaticMesh; build_variants() builds all three.
All columns share the old origin, recessed 84 cm core and 323.5 cm cap height.
"""
from meshkit import Mesh


def _rock(m, pos, size, tint):
    """An irregular eight-sided block with independently clipped XY corners.

    Four convex rings make large flat rock faces, broken corners and unequal
    top/bottom bevels without the identical machined bevels of Mesh.box.
    """
    hx, hy, height = size[0] / 2, size[1] / 2, size[2]
    cuts = [m.rng.uniform(2, 10) for _ in range(4)]
    outline = [(-hx + cuts[0], -hy), (hx - cuts[1], -hy),
               (hx, -hy + cuts[1]), (hx, hy - cuts[2]),
               (hx - cuts[2], hy), (-hx + cuts[3], hy),
               (-hx, hy - cuts[3]), (-hx, -hy + cuts[0])]
    bottom_bevel = m.rng.uniform(2, 5)
    top_bevel = m.rng.uniform(3, 7)
    rings = [(.85, -height / 2), (1, -height / 2 + bottom_bevel),
             (1, height / 2 - top_bevel), (.89, height / 2)]
    vertices = [(x * scale, y * scale, z) for scale, z in rings for x, y in outline]
    faces = [list(range(7, -1, -1)), list(range(24, 32))]
    for ring in range(3):
        for i in range(8):
            j = (i + 1) % 8
            faces.append([ring * 8 + i, ring * 8 + j,
                          (ring + 1) * 8 + j, (ring + 1) * 8 + i])
    m.solid(vertices, faces, tint, pos=pos, variation=.045)


def build(variant='A'):
    if variant not in ('A', 'B', 'C'):
        raise ValueError('Cliff variant must be A, B or C')
    variant_index = ord(variant) - ord('A')
    m = Mesh('SM_CliffColumn_v5' + variant, 541 + variant_index * 137)
    m.refinement_pass = 5
    m.revises = 'SM_CliffColumn_v4'
    m.box((0, 0, 151), (84, 84, 302), '50563f', 2, variation=.02)

    palettes = ['6b6c50', '79775a', '807b5b', '60674c', '747455', '888062']
    # No shared rows: each corner gets independent fracture levels. A clipped
    # outer envelope allows adjacent rotated cells to overlap without cracks.
    for corner, (x, y) in enumerate([(-25, -25), (25, -25), (-25, 25), (25, 25)]):
        count = 4 + ((corner + variant_index) % 2)
        weights = [m.rng.uniform(.65, 1.35) for _ in range(count)]
        levels = [0]
        for weight in weights:
            levels.append(levels[-1] + 307 * weight / sum(weights))
        for index, (bottom, top) in enumerate(zip(levels, levels[1:])):
            px = x + m.rng.uniform(-1.5, 1.5)
            py = y + m.rng.uniform(-1.5, 1.5)
            sx, sy = m.rng.uniform(51, 59), m.rng.uniform(51, 59)
            _rock(m, (px, py, (bottom + top) / 2),
                  (sx, sy, top - bottom), m.rng.choice(palettes))

            # Broad but shallow secondary face fragments interrupt otherwise
            # pristine surfaces. Their stone color remains close to the parent.
            for axis in (0, 1):
                if m.rng.random() < .72:
                    z = m.rng.uniform(bottom + 9, top - 8)
                    length = m.rng.uniform(10, 25)
                    patch_height = m.rng.uniform(7, min(22, top - bottom - 12))
                    if axis == 0:
                        face = px + (1 if x > 0 else -1) * (sx / 2 - .4)
                        pos = (face, py + m.rng.uniform(-8, 8), z)
                        size = (2.4, length, patch_height)
                    else:
                        face = py + (1 if y > 0 else -1) * (sy / 2 - .4)
                        pos = (px + m.rng.uniform(-8, 8), face, z)
                        size = (length, 2.4, patch_height)
                    m.box(pos, size, m.rng.choice(['727554', '7a7958', '666d4c']),
                          1, variation=.035)

    # A low dark moss base is overlapped by uneven small grassy blocks. No
    # continuous raised lip is left exposed around the full column perimeter.
    m.box((0, 0, 308), (98, 98, 13), '5e6c2f', 3, variation=.02)
    for x in (-35, -1, 33):
        for y in (-34, 0, 34):
            top = 323.5 if (x == -1 and y == 0) else m.rng.uniform(318, 323.5)
            height = m.rng.uniform(12, 22)
            m.box((x + m.rng.uniform(-2, 2), y + m.rng.uniform(-2, 2), top - height / 2),
                  (m.rng.uniform(35, 39), m.rng.uniform(35, 39), height),
                  m.rng.choice(['718039', '7d873a', '899042', '637430']),
                  m.rng.uniform(2, 4), variation=.04)

    # Chunky asymmetrical descending moss, with gaps between clustered fingers.
    for axis, sign in [(0, -1), (0, 1), (1, -1), (1, 1)]:
        for cluster in range(2):
            tangent = m.rng.uniform(-35, 35)
            z = m.rng.uniform(289, 306)
            for step in range(m.rng.choice([1, 2, 3])):
                pos = [tangent + m.rng.uniform(-4, 4), tangent, z - step * 12]
                pos[axis] = sign * m.rng.uniform(48, 51)
                size = [m.rng.uniform(13, 24), m.rng.uniform(13, 24), m.rng.uniform(12, 19)]
                size[axis] = m.rng.uniform(8, 11)
                m.box(tuple(pos), tuple(size), m.rng.choice(['62742e', '738135', '596d2d']),
                      2, variation=.04)
    return m.save()


def build_variants():
    return {variant: build(variant) for variant in ('A', 'B', 'C')}
