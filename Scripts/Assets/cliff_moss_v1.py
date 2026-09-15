"""Original moss fringe, anchored inside a cliff face and growing over its lip.

Origin is the upper cliff edge; local +X faces outward. Deep overlapping roots
intersect the column core instead of leaving leaves suspended over its cracks.
"""
from meshkit import Mesh


def build():
    m = Mesh('SM_CliffMoss_v1', 706)
    m.refinement_pass = 1
    # An asymmetric cushion grows from the meadow across the cliff lip.
    for pos, size, tint in [
        ((-9, -6, 0), (34, 31, 10), '788339'),
        ((-2, 10, -2), (30, 21, 10), '697b32'),
        ((4, -12, -7), (25, 17, 14), '748239'),
    ]:
        m.box(pos, size, tint, 3, variation=.035)

    # Three connected, differently tapered fingers. Their roots extend into
    # solid stone; coarse foliage sits on the visible outer edge.
    for y, length, width in [(-11, 51, 11), (1, 98, 9), (12, 32, 13)]:
        steps = max(2, round(length / 13))
        for index in range(steps):
            t = index / (steps - 1)
            z = -8 - t * length
            taper = 1 - .48 * t
            m.box((0, y + 2 * t, z), (34, width * taper, 17),
                  '526c2e', 2, variation=.035)
            m.box((14, y + 2 * t, z + 2),
                  (10, width * taper + 4, 10),
                  m.rng.choice(['637a31', '708235', '7c873b']),
                  2, rot=(0, 0, m.rng.uniform(-8, 8)), variation=.025)
    return m.save()
