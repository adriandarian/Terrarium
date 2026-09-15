"""Broken river shelf with a submerged core and three supported mossy steps.

Local +X faces the river. All exposed ledges are solid down to -65 cm;
the landward core overlaps the terrain rather than balancing on water.
"""
from meshkit import Mesh


def build():
    mesh = Mesh('SM_ShoreOutcrop_v2', 713)
    mesh.refinement_pass = 7
    mesh.revises = 'SM_ShoreOutcrop'
    # Unequal, overlapping columns produce a broken outline and broad shallows.
    for x, y, width, depth, top, tint in [
        (-29, 0, 94, 102, 99, '6d7158'),
        (30, -15, 77, 80, 57, '7b7d62'),
        (70, 20, 64, 60, 19, '7e846a'),
        (1, 57, 51, 47, 31, '686f55'),
    ]:
        mesh.box((x, y, (top-65)/2), (width, depth, top+65), tint, 5)
        # Moss stays on upper dry shelves; river-facing stone remains exposed.
        if top > 40:
            mesh.box((x-4, y+3, top+2), (width*.76, depth*.77, 6),
                     '78843d' if top > 70 else '6e7b3b', 2)
            for ox, oy, size in [(-13, 11, 16), (15, -12, 11)]:
                mesh.box((x+ox, y+oy, top+5.4), (size, size*.8, 2),
                         '899247', .6)
    # Small embedded chips soften the shelf perimeter, without a loose ring.
    for x, y, z, size in [(96, 2, -9, 23), (54, -43, 5, 26),
                           (-26, -52, 39, 19), (9, 77, -4, 20)]:
        mesh.box((x, y, z), (size, size*.8, size*1.3), '6d775d', 3)
    return mesh.save()
