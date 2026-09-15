"""Authored pigment regions in the face and belly atlas cells; no lighting bake."""
import json
import numpy as np


def paint_regions(asset, lo, hi, point, front, linear):
    size = 1024
    # Source-view guides describe painted regions, not projected image pixels.
    # Each guide becomes an axis-aligned rectangle on the physical X/Z surface.
    guides = [
        (5, 700, 682, 48, 46, 'c8924c', .78, front-.012, 'forehead pigment'),
        (5, 553, 779, 48, 70, 'dfae6f', .76, front-.012, 'left cheek'),
        (5, 650, 724, 50, 48, 'efbf83', .74, front-.012, 'upper face'),
        (5, 847, 756, 46, 66, 'e3b173', .76, front-.012, 'right cheek'),
        (5, 601, 884, 48, 58, 'd6a160', .77, front-.012, 'lower left face'),
        (5, 649, 927, 150, 23, 'ca924d', .78, front-.012, 'lower ochre band'),
        (4, 649, 953, 150, 25, 'e3ba84', .75, front-.012, 'upper belly band'),
        (4, 649, 994, 100, 26, 'ce9d5c', .77, front-.012, 'lower belly block'),
        (4, 749, 969, 49, 24, 'd8a364', .76, front-.012, 'right belly block'),
    ]
    arrays = []
    for image in (asset.images[0], asset.images[2]):
        pixels = np.empty(size*size*4, dtype=np.float32)
        image.pixels.foreach_get(pixels)
        arrays.append(pixels.reshape(size, size, 4))
    base, roughness = arrays
    records = []
    for cell, u, v, width, height, color, rough, y, name in guides:
        corner = point(u, v, y)
        right = point(u+width, v, y)
        bottom = point(u, v+height, y)
        cx, cy = cell % 8, cell // 8
        xs = np.arange(cx*128, (cx+1)*128)
        ys = np.arange(cy*128, (cy+1)*128)
        x = lo[0]+((xs+.5)/size-cx/8-.006)/.113*(hi[0]-lo[0])
        z = lo[2]+((ys+.5)/size-cy/8-.006)/.113*(hi[2]-lo[2])
        mask = (x[None, :] >= corner.x) & (x[None, :] <= right.x)
        mask = mask & (z[:, None] <= corner.z) & (z[:, None] >= bottom.z)
        assert mask.any(), name
        rgb = np.array([int(color[i:i+2], 16)/255 for i in (0, 2, 4)])
        # A small non-directional pigment fluctuation retains block texture.
        fluctuation = (((xs[None, :]//12)*7+(ys[:, None]//14)*11) % 9-4)*.003
        painted = np.minimum(1, rgb[None, None, :]*(1+fluctuation[:, :, None]))
        painted = np.where(painted <= .04045, painted/12.92, ((painted+.055)/1.055)**2.4)
        tile = base[cy*128:(cy+1)*128, cx*128:(cx+1)*128]
        tile[:, :, :3][mask] = painted[mask]
        tile = roughness[cy*128:(cy+1)*128, cx*128:(cx+1)*128]
        tile[:, :, :3][mask] = np.repeat((rough+fluctuation)[mask, None], 3, axis=1)
        records.append({'region': name, 'palette_cell': cell, 'guide_pixel': [u, v],
                        'pigment_srgb_hex': color, 'painted_texels': int(mask.sum()),
                        'world_xz_bounds_m': [corner.x, right.x, bottom.z, corner.z]})
    for image, pixels in zip((asset.images[0], asset.images[2]), arrays):
        image.pixels.foreach_set(pixels.ravel()); image.save(); image.pack()
    # Emission remains zero, but save the resized map as part of the same set.
    asset.images[1].save(); asset.images[1].pack()
    (asset.review/'authored-pigment-regions.json').write_text(json.dumps({
        'atlas_size': [size, size], 'regions': records,
        'method': 'Authored flat pigment rectangles and nondirectional variation in planar UV cells. No source pixel sampling or illumination bake.',
        'limits': 'Approximate painted region placement. Does not establish full concept fidelity.'
    }, indent=2))
