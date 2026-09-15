"""Chunky weathered terrain column with staggered fractures, not brick courses.

Keeps the earlier column's origin, nominal 100 cm footprint and 324 cm top.
The four corners deliberately use different fracture heights so rotating placed
instances changes the visible profile without opening holes through the cliff.
"""
from meshkit import Mesh


def build():
    m = Mesh('SM_CliffColumn_v4', 441)
    m.refinement_pass = 4
    m.revises = 'SM_CliffColumn_v3'

    # Recessed continuous rock behind the broken outer faces. This also keeps
    # placed columns opaque when neighbouring instances use different rotations.
    m.box((0, 0, 153), (84, 84, 306), '535943', 5, variation=.02)

    # Offset fracture levels interrupt the old uninterrupted horizontal bands.
    # A few tall masses sit beside shorter stones, as in the reference cliffs.
    corners = [
        (-24, -24, (0, 69, 166, 230, 307)),
        (24, -24, (0, 91, 153, 244, 307)),
        (-24, 24, (0, 104, 184, 247, 307)),
        (24, 24, (0, 78, 140, 228, 307)),
    ]
    palette = ['77745a', '6d7054', '817b5e', '747254', '62694f']
    for corner_index, (x, y, levels) in enumerate(corners):
        for level_index, (bottom, top) in enumerate(zip(levels, levels[1:])):
            # Slight overlap gives deep cracks without exposing background.
            width = m.rng.uniform(51, 61)
            depth = m.rng.uniform(51, 61)
            m.box(
                (x + m.rng.uniform(-2.5, 2.5),
                 y + m.rng.uniform(-2.5, 2.5), (bottom + top) / 2),
                (width, depth, top - bottom + 2),
                palette[(corner_index + level_index * 2) % len(palette)],
                m.rng.uniform(5, 9),
                rot=(m.rng.uniform(-1.3, 1.3),
                     m.rng.uniform(-1.3, 1.3), m.rng.uniform(-3, 3)),
                variation=.035,
            )

    # Local projecting rock shelves: broad pieces, not thin decorative bands.
    # Each side gets a different elevation and extent to avoid a dressed wall.
    for pos, size, tint in [
        ((-44, -14, 103), (26, 46, 35), '78765b'),
        ((17, 45, 181), (45, 24, 48), '6e7154'),
        ((44, -24, 249), (23, 32, 43), '817c5c'),
        ((-19, -44, 41), (39, 24, 39), '686c50'),
    ]:
        m.box(pos, size, tint, 7, rot=(0, 0, m.rng.uniform(-4, 4)))

    # A connected low cap retains placement compatibility while irregular,
    # overlapping patches soften the four-way grid of the earlier mesh.
    m.box((0, 0, 309), (103, 101, 18), '657532', 4, variation=.02)
    for pos, size, tint in [
        ((-27, -25, 314), (59, 58, 19), '78833a'),
        ((25, -23, 312), (56, 63, 19), '7e873d'),
        ((-24, 26, 313), (61, 56, 21), '6f7d34'),
        ((27, 25, 314), (56, 55, 19), '858c41'),
    ]:
        m.box(pos, size, tint, 4, rot=(0, 0, m.rng.uniform(-2, 2)), variation=.025)

    # Sparse moss fingers descend by different amounts; most stone stays bare.
    for pos, size in [
        ((-51, -18, 298), (12, 23, 29)),
        ((-49, 14, 278), (10, 16, 24)),
        ((28, 51, 295), (21, 11, 31)),
        ((49, -29, 299), (12, 18, 26)),
        ((-14, -51, 304), (27, 12, 18)),
    ]:
        m.box(pos, size, '657732', 3, variation=.04)
    return m.save()
