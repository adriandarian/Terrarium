"""Soft earth track: overlapping flat soil patches and a broken grassy fringe.

Coordinates retain the 200 cm path recipe convention. All components are closed
convex solids; broad soil patches replace the old rectangular transverse mosaic.
"""
import math
from meshkit import Mesh


def _patch(mesh, center, size, color, bottom=-6, top=0, yaw=0, sides=7):
    """An ellipse sampled into a convex, irregularly spaced flat polygon."""
    phase = mesh.rng.uniform(0, math.tau)
    points = []
    for i in range(sides):
        angle = phase + math.tau * (i + mesh.rng.uniform(-.18, .18)) / sides
        points.append((math.cos(angle)*size[0]/2, math.sin(angle)*size[1]/2))
    vertices = [(x, y, z) for z in (bottom, top) for x, y in points]
    faces = [list(range(sides)), list(range(sides, 2*sides))]
    faces += [[i, (i+1)%sides, (i+1)%sides+sides, i+sides] for i in range(sides)]
    mesh.solid(vertices, faces, color, pos=(*center, 0), rot=(0, 0, yaw), variation=0)


def build():
    mesh = Mesh('SM_PathTile_v4', 8084)
    mesh.refinement_pass = 7
    mesh.revises = 'SM_PathTile_v3'
    # A broad overlapping base keeps the center passable without separated tiles.
    outline = [(-116,-67),(-89,-96),(77,-100),(114,-62),
               (116,67),(84,98),(-85,100),(-113,66)]
    vertices = [(x,y,z) for z in (-14,-1) for x,y in outline]
    mesh.solid(vertices, [list(range(8)),list(range(8,16))] +
               [[i,(i+1)%8,(i+1)%8+8,i+8] for i in range(8)], 'a18c61', variation=0)
    # Different-sized, diagonal patches have no shared row or transverse seam.
    patches = [((-59,-23),(123,106),'a99569',-12),
               ((13,31),(136,111),'ae996c',19),
               ((67,-30),(113,107),'a89468',-27),
               ((-54,62),(98,48),'a59164',14),
               ((21,-64),(125,53),'a08c61',-9)]
    for index, (center,size,color,yaw) in enumerate(patches):
        _patch(mesh, center, size, color, top=-.65+index*.18, yaw=yaw)
    # Soil lobes and low moss grow in from the banks, leaving a clear center.
    for side in (-1,1):
        for index, x in enumerate((-83,-25,48,91)):
            y=side*mesh.rng.uniform(87,99)
            _patch(mesh,(x,y),(mesh.rng.uniform(34,57),mesh.rng.uniform(20,36)),
                   mesh.rng.choice(('9b885d','9f8d62','a59164')),top=.45+index*.09,
                   yaw=mesh.rng.uniform(-28,28))
        for x in (-69,28,87):
            y=side*mesh.rng.uniform(98,110)
            _patch(mesh,(x,y),(mesh.rng.uniform(20,37),mesh.rng.uniform(15,27)),
                   mesh.rng.choice(('777a40','7e8045','858347')),top=1.0,
                   yaw=mesh.rng.uniform(-50,50),sides=6)
    # Sparse embedded stones, never a regular paving pattern.
    for center,size in [((-28,86,1),(10,7,3)),((73,-98,1),(8,6,3))]:
        mesh.ellipsoid(center,size,'95896a',segments=5,rings=2,
                       rot=(0,0,mesh.rng.uniform(-50,50)))
    return mesh.save()
