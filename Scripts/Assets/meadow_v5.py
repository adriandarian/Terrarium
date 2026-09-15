"""Quiet meadow: broad interlocking moss islands over olive earth.

Footprint and substrate match previous terrain tiles. Color is carried by
vertices so a world-space surface treatment can be applied by the scene pass.
"""
from meshkit import Mesh


def _patch(mesh, outline, top, tint):
    """Extrude a convex uneven outline as a closed, nearly flush moss layer."""
    count = len(outline)
    vertices = [(x, y, top - .7) for x, y in outline]
    vertices += [(x, y, top) for x, y in outline]
    faces = [list(range(count)), list(range(count, count * 2))]
    faces += [[i, (i + 1) % count, (i + 1) % count + count, i + count]
              for i in range(count)]
    mesh.solid(vertices, faces, tint, variation=.008)


def build():
    mesh = Mesh('SM_MeadowTile_v5', 582)
    mesh.refinement_pass = 5
    mesh.revises = 'SM_MeadowTile_v4'
    mesh.box((0, 0, -160), (203, 203, 320), '555b3e', 2)
    # Neutral olive earth remains exposed between the larger living patches.
    mesh.box((0, 0, -2), (206, 206, 15), '737745', 3, variation=.008)
    # Unequal broad polygons avoid both tiny mottling and a visible patch grid.
    patches = [
        ([(-103, -94), (-58, -103), (-10, -80), (2, -44),
          (-29, -20), (-78, -29), (-103, -60)], '788144'),
        ([(-36, -29), (2, -58), (44, -31), (39, 8),
          (8, 30), (-37, 8)], '6e7a3c'),
        ([(26, -103), (78, -101), (103, -58), (84, -23),
          (47, -21), (17, -53)], '7b8248'),
        ([(-103, 12), (-68, -2), (-26, 25), (-34, 66),
          (-72, 85), (-103, 65)], '68753b'),
        ([(-28, 58), (13, 30), (59, 46), (72, 83),
          (40, 103), (-14, 102)], '7c8548'),
        ([(59, 7), (103, -8), (103, 62), (82, 75),
          (49, 42)], '717e40'),
    ]
    for index, (outline, tint) in enumerate(patches):
        _patch(mesh, outline, 5.9 + index * .035, tint)
    # A single small accent cluster, with a mostly buried second stone.
    mesh.box((61, -6, 7.0), (10, 7, 4), '89866a', 1.0,
             rot=(0, 0, 17), variation=.015)
    mesh.box((70, -1, 6.2), (5, 4, 2), '7b7d5d', .5,
             rot=(0, 0, -12), variation=.015)
    return mesh.save()
