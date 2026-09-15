"""Individual hand-laid terracotta tiles with visible joints and supported laps.

v5 merged tiles into rows: the backing almost reached their top faces and the
tiles overlapped sideways. Here the backing is recessed and joints expose dark
clay beneath. Tile lengths overlap down the slope, as a coherent tiled roof.
Compatible with cottage_v5's original coordinates and subsequent body transform.
"""
import random

from cottage_roof_v5 import _RoofParts


CLAY = ('8a4225', 'aa5930', '99502a', 'b56936', 'a75c31',
        '793d26', '97502e', 'b06031', '85432a')


def _segments(rng, start, end, minimum, maximum):
    """Partition a row into irregular widths; callers inset each tile for joints."""
    cursor = start
    while cursor < end:
        width = min(rng.uniform(minimum, maximum), end - cursor)
        if end - cursor - width < minimum * .55:
            width = end - cursor
        yield cursor + width / 2, width
        cursor += width


def _mark(mesh, role):
    # Offline validation can distinguish the actual tiles from hidden backing.
    mesh.parts[-1]['roof_role'] = role


def add_main_roof(mesh, origin=(0, 0, 0), z_scale=1.0):
    roof = _RoofParts(mesh, origin, z_scale)
    rng = random.Random(1406)
    for side in (-1, 1):
        # At the ridge this top is z~463, ~20 below the tile tops. It closes
        # the joints without swallowing their beveled ends or making orange bars.
        roof.box((side * 89, 0, 372), (252, 430, 10), '643b27', 2,
                 rot=(0, side * 43, 0))
        _mark(mesh, 'main_backing')
        roof.box((side * 183, 0, 285), (12, 421, 13), '57422c', 2)
        for col in range(12):
            roof.box((side * 184, -199 + col * 36, 282),
                     (26, 10, 14), rng.choice(('654b2d', '705333', '57432c')), 1.5)
        # Independent row start, joints and tile positions break aligned lanes.
        for row in range(8):
            row_x = 12 + row * 24 + rng.uniform(-1.7, 1.7)
            start, end = -224 + rng.uniform(-3, 3), 224 + rng.uniform(-3, 3)
            for col, (y, span) in enumerate(_segments(rng, start, end, 28, 40)):
                x = side * (row_x + rng.uniform(-3.8, 3.8))
                z = 474 - abs(x) * .94 + rng.uniform(-3.8, 3.8)
                thickness = rng.uniform(18, 24)
                # A 3..5-unit side joint remains visible. Small yaw never bridges
                # the full joint. The longer x dimension retains downhill laps.
                width = span - rng.uniform(3, 5)
                roof.box((x, y, z), (rng.uniform(37, 42), width, thickness),
                         rng.choice(CLAY), rng.uniform(2.1, 3.2),
                         rot=(rng.uniform(-1.2, 1.2),
                              rng.uniform(-2.5, 2.5), rng.uniform(-1.1, 1.1)))
                _mark(mesh, 'main_tile')
                # Restrained broad chips, not a repetitive mark on every tile.
                if (row * 13 + col) % 17 == 0:
                    roof.box((x + side * 11, y - width * .18, z + thickness / 2),
                             (8, 10, 1.8), 'c07a47', .6)
    # The ridge is individually capped rather than a continuous orange beam.
    for y, span in _segments(rng, -229, 228, 26, 36):
        roof.box((rng.uniform(-1.4, 1.4), y, 481 + rng.uniform(-2.6, 2.6)),
                 (rng.uniform(31, 35), span - 2.6, rng.uniform(20, 24)),
                 rng.choice(CLAY), 3.3,
                 rot=(rng.uniform(-1.5, 1.5), 0, rng.uniform(-1.5, 1.5)))
        _mark(mesh, 'main_ridge_cap')


def add_projecting_gable_roof(mesh, origin=(0, 0, 0), z_scale=1.0):
    roof = _RoofParts(mesh, origin, z_scale)
    rng = random.Random(1416)
    for side in (-1, 1):
        roof.box((-146, -60 + side * 35, 384), (151, 107, 8),
                 '603923', 1.5, rot=(-side * 49, 0, 0))
        _mark(mesh, 'gable_backing')
        roof.box((-148, -60 + side * 73, 351), (151, 9, 10), '61482f', 1.5)
        for row in range(4):
            for x, span in _segments(rng, -228 + rng.uniform(-2, 2), -66, 24, 34):
                y = -60 + side * (12 + row * 18 + rng.uniform(-2.5, 2.5))
                z = 443 - abs(y + 60) * 1.16 + rng.uniform(-2.5, 2.5)
                roof.box((x, y, z), (span - 3.2, rng.uniform(29, 33),
                                     rng.uniform(15, 19)), rng.choice(CLAY), 2.3,
                         rot=(rng.uniform(-1.7, 1.7), rng.uniform(-1, 1),
                              rng.uniform(-1, 1)))
                _mark(mesh, 'gable_tile')
    for x, span in _segments(rng, -230, -67, 25, 33):
        roof.box((x, -60 + rng.uniform(-1, 1), 445 + rng.uniform(-2, 2)),
                 (span - 2.4, 25, 20), rng.choice(CLAY), 3)
        _mark(mesh, 'gable_ridge_cap')
