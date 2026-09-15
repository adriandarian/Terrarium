"""Finer hand-laid clay roof for the cottage_v4 coordinate system.

Call both helpers in place of the corresponding v4 roof loops. The projecting
gable's plaster, timber frame and window remain owned by the cottage recipe.
No asset is loaded or saved here; the caller owns the combined static mesh.
"""
import random


CLAY = ('914c29', 'a3572e', 'ad6033', '98502b', 'a95a30', '87472a')


class _RoofParts:
    """Transform roof geometry together with a shortened cottage if requested."""

    def __init__(self, mesh, origin, z_scale):
        if z_scale <= 0:
            raise ValueError('z_scale must be positive')
        self.mesh, self.origin, self.z_scale = mesh, origin, z_scale

    def box(self, pos, size, color, bevel=2, rot=(0, 0, 0)):
        # Transform finished vertices so slopes and their supports stay aligned
        # even when the caller compresses the cottage vertically.
        start = len(self.mesh.vertices)
        self.mesh.box(pos, size, color, bevel, rot=rot, variation=.025)
        ox, oy, oz = self.origin
        self.mesh.vertices[start:] = [
            (x + ox, y + oy, z * self.z_scale + oz)
            for x, y, z in self.mesh.vertices[start:]
        ]
        part = self.mesh.parts[-1]
        x, y, z = part['center']
        part['center'] = (x + ox, y + oy, z * self.z_scale + oz)
        part['volume'] *= self.z_scale


def add_main_roof(mesh, origin=(0, 0, 0), z_scale=1.0):
    """Add 208 small staggered tiles, 14 ridge caps, fascia and rafter ends.

    Local ridge is around z=481, eaves around z=303. Matches the original
    cottage shell and chimney; no global random state or mesh seed is consumed
    for placement, so changing the wall detail does not reshuffle the roof.
    """
    roof = _RoofParts(mesh, origin, z_scale)
    rng = random.Random(1405)
    for side in (-1, 1):
        roof.box((side * 89, 0, 389), (252, 434, 11), '613d29', 2,
                 rot=(0, side * 43, 0))
        # Thin weathered fascia supports the fine, irregular terracotta edge.
        roof.box((side * 188, 0, 294), (13, 430, 15), '58432b', 2)
        for col in range(12):
            y = -199 + col * 36
            roof.box((side * 185, y, 288), (30, 10, 14),
                     rng.choice(('654b2d', '705333', '57432c')), 1.5)
        for row in range(8):
            x = side * (12 + row * 24)
            for col in range(13):
                y = -205 + col * 34 + (7 if row % 2 else -4)
                y += rng.uniform(-1.8, 1.8)
                z = 472 - abs(x) * .94 + rng.uniform(-1.6, 1.6)
                roof.box((x, y, z),
                         (rng.uniform(35, 38), rng.uniform(38, 41),
                          rng.uniform(15, 18)), rng.choice(CLAY), 2.6,
                         rot=(0, rng.uniform(-1.2, 1.2), rng.uniform(-2, 2)))
                # Sparse sun-worn clay accents stay subordinate to tile shapes.
                if (row * 13 + col) % 19 == 0:
                    roof.box((x + side * 9, y - 7, z + 8.8),
                             (9, 13, 1.8), 'b36c3d', .6)
    for col in range(14):
        roof.box((rng.uniform(-.7, .7), -216 + col * 33, 479),
                 (34, 37, 22), rng.choice(('a45a31', 'a95f33', '924d2b')),
                 3.8, rot=(0, 0, rng.uniform(-1.7, 1.7)))


def add_projecting_gable_roof(mesh, origin=(0, 0, 0), z_scale=1.0):
    """Retain the camera-facing cross gable with 48 small tiles and ridge caps.

    Compatible with the v4 gable prism x=-205..-75, y=-127..7, z=350..428.
    Do not retain the old gable tile loops when using this helper.
    """
    roof = _RoofParts(mesh, origin, z_scale)
    rng = random.Random(1415)
    for side in (-1, 1):
        # Underlay closes tiny tile seams without adding a heavy slab silhouette.
        roof.box((-146, -60 + side * 35, 389), (151, 107, 8),
                 '65402a', 1.5, rot=(-side * 49, 0, 0))
        roof.box((-148, -60 + side * 73, 353), (151, 9, 10), '61482f', 1.5)
        for row in range(4):
            y = -60 + side * (12 + row * 18)
            for col in range(6):
                x = -213 + col * 26 + (3 if row % 2 else 0)
                z = 442 - abs(y + 60) * 1.16 + rng.uniform(-1.3, 1.3)
                roof.box((x, y, z), (30, 29, 14), rng.choice(CLAY), 2,
                         rot=(rng.uniform(-1, 1), 0, rng.uniform(-1.5, 1.5)))
    for col in range(6):
        roof.box((-213 + col * 26, -60, 443), (30, 24, 19),
                 rng.choice(('a45a31', 'a95f33', '924d2b')), 3)
