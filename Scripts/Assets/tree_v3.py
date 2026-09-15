"""Slender, tiered woodland tree with exposed branching and small leaf sprays.

Build once in Terrarium's editor; the returned asset uses the meshkit contract.
Rotate and vary instance scale modestly to avoid repeating its asymmetric crown.
"""
import math

from meshkit import Mesh


def build():
    m = Mesh('SM_Tree_v3', 761)
    m.refinement_pass = 3
    m.revises = 'SM_OrchardTree_v2'

    # The slightly bent, tapered trunk remains visible between separate tiers.
    trunk = [(0, 0, 3), (4, 1, 109), (-2, 3, 206), (9, 0, 288), (5, 8, 348)]
    for i, width in enumerate((22, 18, 13, 8)):
        m.beam(trunk[i], trunk[i + 1], width, ('514126', '604c2b')[i % 2])
    for end in ((31, 12, 3), (-25, 18, 3), (8, -29, 3)):
        m.beam((1, 0, 29), end, 11, '514529')
    # Unequal tier extents deliberately leave trunk/branch windows. Branches
    # originate at different heights rather than forming one spherical canopy.
    sprays = [
        ((2, 1, 107), (-56, 13, 177), 31, 29),
        ((2, 1, 135), (48, -27, 201), 30, 28),
        ((-1, 3, 171), (-16, 43, 222), 29, 25),
        ((1, 2, 199), (-39, -35, 258), 28, 27),
        ((5, 1, 226), (43, 18, 281), 28, 26),
        ((7, 2, 261), (-24, 30, 308), 24, 24),
        ((7, 4, 287), (12, -21, 337), 23, 23),
        ((7, 5, 316), (3, 7, 359), 19, 22),
    ]
    palette = ['435825', '516728', '637831', '718236', '80903b']
    for tier, (start, tip, radius, height) in enumerate(sprays):
        m.beam(start, tip, max(5, 11 - tier * .7), '59472a')
        # A compact central spray plus four offset twig sprays. Small leaves
        # overlap within a spray, with negative space between the main tiers.
        centers = [(tip[0], tip[1], tip[2] + 6)]
        for twig in range(4):
            angle = twig * math.pi / 2 + tier * .83
            reach = radius * m.rng.uniform(.58, .92)
            end = (tip[0] + math.cos(angle) * reach,
                   tip[1] + math.sin(angle) * reach,
                   tip[2] + m.rng.uniform(-4, height * .65))
            m.beam((tip[0], tip[1], tip[2] - 9), end, 4, '65502b')
            centers.append(end)
        for cluster, center in enumerate(centers):
            for leaf in range(4):
                offset = (m.rng.uniform(-10, 10), m.rng.uniform(-10, 10),
                          m.rng.uniform(-6, 12))
                pos = tuple(center[k] + offset[k] for k in range(3))
                key = palette[m.rng.randrange(1, 5) if leaf == 3 else m.rng.randrange(0, 4)]
                m.box(pos, (m.rng.uniform(16, 27), m.rng.uniform(15, 25),
                            m.rng.uniform(13, 22)), key, 2,
                      rot=(m.rng.uniform(-7, 7), m.rng.uniform(-7, 7),
                           m.rng.uniform(-18, 18)))
    return m.save()


if __name__ == '__main__':
    build()
