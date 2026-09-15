"""Dark chipped river stones with sloping polygonal caps, partly submerged.

There are no flat rectangular highlight plates. Each complete stone extends
below the water and narrows through asymmetric facets toward its visible cap.
"""
import math
from meshkit import Mesh, color


def stone(mesh, x, y, width, depth, top, tint, cap_tint, yaw):
    angles = (0, 49, 115, 181, 240, 307)
    outline = []
    for degree in angles:
        angle = math.radians(degree + mesh.rng.uniform(-6, 6))
        outline.append((math.cos(angle)*width*.5,
                        math.sin(angle)*depth*.5))
    vertices = [(px, py, -58) for px, py in outline]
    vertices += [(px, py, top*.24) for px, py in outline]
    vertices += [(px*.48+width*.06, py*.48-depth*.05,
                  top+px*.08-py*.035) for px, py in outline]
    n = len(outline)
    faces = [list(range(n)), list(range(2*n, 3*n))]
    for ring in (0, 1):
        a = ring*n
        b = (ring+1)*n
        faces += [[a+i, a+(i+1)%n, b+(i+1)%n, b+i]
                  for i in range(n)]
    offset = len(mesh.vertices)
    mesh.solid(vertices, faces, tint, rot=(0, 0, yaw), pos=(x, y, 0),
               variation=.015)
    # Smoothly darken the submerged body rather than outlining a pale tile.
    for index in range(offset+2*n, offset+3*n):
        mesh.colors[index] = color(cap_tint, mesh.rng.uniform(.96, 1.03))


def build():
    mesh = Mesh('SM_RiverStones_v2', 71382)
    mesh.refinement_pass = 8
    mesh.revises = 'SM_RiverStones_v1'
    for item in [
        (-26, 5, 49, 37, 29, '365d54', '4a6657', 17),
        (12, -16, 38, 31, 19, '315b56', '456557', -23),
        (34, 17, 27, 22, 10, '315957', '41675e', 42),
        (-18, 36, 22, 17, 7, '365e59', '45695e', -12),
        (1, 18, 19, 25, 14, '345c54', '486658', 71),
    ]:
        stone(mesh, *item)
    return mesh.save()
