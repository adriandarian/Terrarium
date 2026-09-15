"""Fine native turquoise river surface with coherent pools and small glints.

Three compatible 302 cm tiles use one shared boundary color, avoiding visible
square color seams when the shoreline-aware placement mixes depth variants.
All water detail is closed 3D geometry with lit vertex colors, never an overlay.
"""
import math
from meshkit import Mesh, color

PALETTES = {
    'medium': ('26666b', '318587', '429595'),
    'shallow': ('327a7d', '429b99', '50aaa4'),
    'deep': ('20555e', '276f78', '34838a'),
}
NAMES = {'medium': 'WaterTile_v4', 'shallow': 'WaterShallow_v4',
         'deep': 'WaterDeep_v4'}


def surface_color(x, y, depth):
    """Broad pools, small tonal ripples, and an identical outer join."""
    shade = .5 + .23*math.sin(x/63+y/101) + .17*math.cos(y/58-x/97)
    shade = max(0, min(1, shade))
    palette = [color(c) for c in PALETTES[depth]]
    if shade < .5:
        a, b, amount = palette[0], palette[1], shade*2
    else:
        a, b, amount = palette[1], palette[2], (shade-.5)*2
    body = tuple(aa+(bb-aa)*amount for aa, bb in zip(a, b))
    # Boundary blending prevents obvious repeating tile outlines. Adjacent
    # tiles overlap by 2 cm, and both evaluate the same final edge color.
    fade = min(1, max(0, (151-max(abs(x), abs(y)))/38))
    boundary = color('318184')
    return tuple(edge+(inside-edge)*fade for edge, inside in zip(boundary, body))


def recipe(depth='medium'):
    m = Mesh('SM_'+NAMES[depth], {'medium': 1204, 'shallow': 1205, 'deep': 1206}[depth])
    m.refinement_pass = 7
    m.revises = 'SM_WaterTile_v3'
    # Solid continuous base; all surface prisms are slightly embedded.
    m.box((0, 0, -15), (302, 302, 29), '26666b', .15, variation=0)
    divisions = 18
    points = {}
    for ix in range(divisions+1):
        for iy in range(divisions+1):
            x = -151+302*ix/divisions
            y = -151+302*iy/divisions
            if 0 < ix < divisions and 0 < iy < divisions:
                x += m.rng.uniform(-3.1, 3.1)
                y += m.rng.uniform(-3.1, 3.1)
            points[ix, iy] = (x, y)
    faces = [[0, 1, 2], [3, 5, 4], [0, 3, 4, 1],
             [1, 4, 5, 2], [2, 5, 3, 0]]
    for ix in range(divisions):
        for iy in range(divisions):
            corners = [points[ix, iy], points[ix+1, iy],
                       points[ix+1, iy+1], points[ix, iy+1]]
            for tri in ((0, 1, 2), (0, 2, 3)):
                verts = [(*corners[i], z) for z in (-.8, 1) for i in tri]
                first = len(m.colors)
                m.solid(verts, faces, '318184', variation=0)
                # Continuous interpolated color across shared surface vertices
                # makes the fine triangulation disappear under normal lighting.
                m.colors[first:] = [surface_color(x, y, depth) for x, y, _ in verts]
    # Short, broken parallel glints are individually small at the game camera.
    # They remain below 2.3 cm and cannot read as floating props.
    for i in range(29 if depth == 'shallow' else 22):
        x, y = m.rng.uniform(-137, 137), m.rng.uniform(-137, 137)
        length = m.rng.uniform(5, 15)
        tint = m.rng.choice(['69b8b0', '559f9d', '87c5b8', '489796'])
        m.box((x, y, 1.75), (length, m.rng.uniform(1.0, 2.4), .7),
              tint, .12, rot=(0, 0, 23), variation=.015)
        if i % 5 == 0:
            m.box((x+3, y+4, 1.7), (length*.48, 1.0, .6),
                  '65aaa6', .1, rot=(0, 0, 23), variation=.01)
    return m


def build():
    return recipe().save()


def build_variants():
    return {depth: recipe(depth).save() for depth in NAMES}
