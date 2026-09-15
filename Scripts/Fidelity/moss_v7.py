"""Broad broken moss cushions rooted into exposed terrace lips and faces."""
import math
import random

import reference as ref
from placement import place_xyz
from terrain_v8 import CELL, DIRECTIONS, protected


def patch_specs(cells):
    """Vary patch silhouette while preserving a root inside the rock core.

    CliffMoss_v1 has a 114.5cm long central finger. Most instances compress that
    to 12-38cm and spread laterally, so the same source reads as attached moss
    cushions rather than evenly spaced dangling strings.
    """
    rng = random.Random(70619)
    result = []
    occupied = []
    for (x, y), h in sorted(cells.items()):
        if protected(x, y, h, 26):
            continue
        for dx, dy in DIRECTIONS:
            lower = ref.height(x + dx, y + dy)
            if lower is None:lower=0
            if lower > h - 95:
                continue
            # Coherent stretches with gaps, rather than one patch per column.
            pocket = math.sin(x / 229 + y / 173) + .42*math.sin(x/117-y/263)
            if pocket < -.45 or rng.random() > .62:
                continue
            nx, ny = dx/CELL, dy/CELL
            # ±36.9cm is the guaranteed core of the current 84cm column at
            # CELL/84*1.025 scale. These roots sit several centimeters inside it,
            # irrespective of v6 variant rotation, shear, or projecting chunks.
            radial = rng.uniform(30.5, 35)
            tangent = rng.uniform(-4, 4)
            ax, ay = x+nx*radial-ny*tangent, y+ny*radial+nx*tangent
            if protected(ax, ay, h, 26):
                continue
            if any(math.hypot(ax-bx, ay-by)<rng.uniform(58, 77)
                   and abs(h-bh)<45 for bx, by, bh in occupied):
                continue
            profile = rng.random()
            if profile < .69:
                width, length = rng.uniform(1.45, 2.3), rng.uniform(.11, .30)
            elif profile < .94:
                width, length = rng.uniform(1.15, 1.85), rng.uniform(.31, .47)
            else:
                width, length = rng.uniform(1.25, 1.75), rng.uniform(.48, .62)
            length = min(length, (h-lower)*.42/114.5)
            depth = rng.uniform(.88, 1.20)
            yaw = math.degrees(math.atan2(dy, dx))
            # The cushion intersects the top surface, while the compressed
            # fingers stay rooted in the face below. No free-floating decals.
            result.append(((ax, ay, h+5.5-length), (depth, width, length), yaw))
            occupied.append((ax, ay,h))
            # Occasional short separated patches farther down the same face
            # break up the cap-only pattern. At this depth every root remains
            # within the upper column core even on a stepped terrace base.
            if profile < .27 and h-lower>160:
                drop = rng.uniform(22, 42)
                face_tangent = rng.uniform(-6, 6)
                bx, by = x+nx*32-ny*face_tangent, y+ny*32+nx*face_tangent
                result.append(((bx, by, h-drop),
                               (rng.uniform(.90, 1.13), rng.uniform(.82, 1.34),
                                rng.uniform(.08, .16)), yaw))
    return result


def build(cells):
    specs = patch_specs(cells)
    for xyz, scale, yaw in specs:
        place_xyz('CliffMoss_v1', xyz, scale, yaw, 'CliffMoss')
    return len(specs)
