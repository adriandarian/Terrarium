"""Coarse, quiet ground surfaces for the reference-led environment assembly.

Both recipes return UNSAVED meshkit.Mesh objects. Units are centimeters; XY is
exactly -100..100 and the nominal walking surface is Z=0. Support extends below
that surface. Do not translate these meshes to a bottom-grounded pivot.
"""
from meshkit import Mesh


SPECS = {
    'meadow_tile': {
        'name': 'SM_Env_MeadowTile',
        'dimensions_cm': [200, 200, 12],
        'bounds_cm': {'min': [-100, -100, -12], 'max': [100, 100, 0]},
        'top_surface_z': 0,
        'notes': 'Coarse 4x4 square turf courses, shallow interior depressions, two small bare patches and solid earth support. All perimeter cells remain at Z=0.',
    },
    'path_tile': {
        'name': 'SM_Env_PathTile',
        'dimensions_cm': [200, 200, 6],
        'bounds_cm': {'min': [-100, -100, -6], 'max': [100, 100, 0]},
        'top_surface_z': 0,
        'notes': 'Sparse warm tan rectangular dirt/paver mosaic on continuous closed support. Flush perimeter and no out-of-footprint detail; existing actors shape the path.',
    },
}


def block(m,x0,x1,y0,y1,z0,z1,color):
    """Closed solid box with exact shared edges and no recessed bevel cracks."""
    assert x0<x1 and y0<y1 and z0<z1
    vertices=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
              (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    m.solid(vertices,[[0,3,2,1],[4,5,6,7],[0,1,5,4],
                      [1,2,6,5],[2,3,7,6],[3,0,4,7]],color,variation=0)


def meadow_tile():
    m=Mesh(SPECS['meadow_tile']['name'],2210)
    # A single buried support closes every small turf-height transition. The
    # top courses overlap this support by 1 cm; there is no hollow shell.
    block(m,-100,100,-100,100,-12,-3,'625b35')
    colors=[
        ['6d7534','707737','707737','697230'],
        ['687130','6b7332','717935','6e7633'],
        ['6e7633','737a37','697330','6b7432'],
        ['6a7331','6e7633','6c7532','707736'],
    ]
    height={(1,1):-.60,(2,1):-1.05,(1,2):-.35,(2,2):-.80}
    for iy in range(4):
        for ix in range(4):
            x0,y0=-100+ix*50,-100+iy*50
            z=height.get((ix,iy),0)
            if (ix,iy)==(1,1):
                # One small ochre-earth cell cut into the turf course. The
                # surrounding rectangles tile the region exactly, no overlay.
                block(m,x0,x0+18,y0,y0+23,-4,z,'827342')
                block(m,x0+18,x0+50,y0,y0+23,-4,z,colors[iy][ix])
                block(m,x0,x0+50,y0+23,y0+50,-4,z,colors[iy][ix])
            elif (ix,iy)==(2,2):
                block(m,x0+29,x0+50,y0+31,y0+50,-4,z,'79713d')
                block(m,x0,x0+29,y0,y0+50,-4,z,colors[iy][ix])
                block(m,x0+29,x0+50,y0,y0+31,-4,z,colors[iy][ix])
            else:
                block(m,x0,x0+50,y0,y0+50,-4,z,colors[iy][ix])
    m.top_surface_z=0
    m.placement_contract='preserve top Z=0; actor XY scale .36 gives 72cm tile and 18cm primary turf cells'
    return m


def path_tile():
    m=Mesh(SPECS['path_tile']['name'],2211)
    block(m,-100,100,-100,100,-6,-1.5,'a28d5b')
    # Four broad rows, each divided at different X stations. All top surfaces
    # stay flush: palette and rectangular facets carry the paver/dirt reading
    # without tiny raised grains, dark seams or a jagged outer silhouette.
    rows=[
        (-100,-50,[-100,-36,29,100],['b6a06b','b29c66','b8a36e']),
        (-50,0,[-100,-58,3,58,100],['b39d66','baa56f','b59f68','b29b63']),
        (0,50,[-100,-24,39,100],['b7a16a','b09b65','b7a16b']),
        (50,100,[-100,-54,13,57,100],['b29c66','b7a16b','baa56f','b59f69']),
    ]
    for y0,y1,stations,colors in rows:
        for i,(x0,x1) in enumerate(zip(stations,stations[1:])):
            block(m,x0,x1,y0,y1,-2,0,colors[i])
    m.top_surface_z=0
    m.placement_contract='preserve top Z=0; existing path actor X stretch and map boundary own silhouette'
    return m


BUILDERS={'meadow_tile':meadow_tile,'path_tile':path_tile}
