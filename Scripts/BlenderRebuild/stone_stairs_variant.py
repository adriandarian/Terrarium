"""Terrace-fit stone module: source block silhouette with face-authored stone/moss atlas."""
import sys, math, random
sys.path.insert(0, 'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import bpy
from assetkit import Asset

a = Asset('StoneStairs', 'river_crossing.png', [('92947a', 'mineral')])
s = a.scene
s['variant_of'] = 'RiverCrossing'
s['variant_purpose'] = 'Eight 35 cm rises over the existing terrace flight; source stone block and moss treatment. The canonical crossing retains four steps.'
s['tread_count'] = 8
s['rise_m'] = .35
s['run_m'] = .315
s['width_m'] = 2.5
size = 1024
tile = 64
pixels = [0.0, 0.0, 0.0, 1.0] * (size * size)
rng = random.Random(91384)
stone = ['969982', 'a2a38c', '868d70', '91957a', 'a9aa91', '7c8469']
moss = ['747f38', '828e3c', '637332', '8d9849']

def linear(c):
    v = c / 255
    return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4

def paint_face(index, width, height, face, step):
    # Each face has its own tile, with cell counts proportional to physical size.
    # sRGB reference colors are converted to linear before Blender writes the PNG.
    nx = max(2, round(width / .044))
    ny = max(2, round(height / .044))
    colors = {}
    for j in range(ny):
        for i in range(nx):
            edge = min(i, nx - 1 - i)
            if face == 1:
                covered = (j >= ny - 1 and rng.random() < .63) or (edge == 0 and rng.random() < .27)
            else:
                course = j * height / ny
                covered = (course < .18 and rng.random() < .43) or (edge == 0 and rng.random() < .30)
            hexcolor = rng.choice(moss if covered else stone)
            shade = rng.uniform(.95, 1.035)
            colors[i, j] = [linear(min(255, round(int(hexcolor[k:k+2], 16) * shade))) for k in (0, 2, 4)] + [1]
    ox, oy = (index % 16) * tile, (index // 16) * tile
    for v in range(tile):
        for u in range(tile):
            i = min(nx - 1, max(0, int((u - 2) / 60 * nx)))
            j = min(ny - 1, max(0, int((v - 2) / 60 * ny)))
            at = ((oy + v) * size + ox + u) * 4
            pixels[at:at+4] = colors[i, j]

face_index = 0
for step in range(8):
    top = (step + 1) * .35
    y = -1.1025 + step * .315
    cuts = [-1.25, -.57, .40, 1.25] if step % 2 else [-1.25, -.33, .69, 1.25]
    for left, right in zip(cuts, cuts[1:]):
        width = right - left - .008
        depth = .315
        ob = a.box('Solid mossy stair block', ((left + right) / 2, y, top / 2), (width, depth, top), 0, .002)
        ob['tread'] = step + 1
        for poly in ob.data.polygons:
            w, h = (width, depth) if poly.index < 2 else ((width, top) if poly.index in [2, 4] else (depth, top))
            paint_face(face_index, w, h, poly.index, step)
            ox, oy = face_index % 16 * tile, face_index // 16 * tile
            for loop, (u, v) in zip(poly.loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                ob.data.uv_layers.active.data[loop].uv = ((ox + 2 + u * 60) / size, (oy + 2 + v * 60) / size)
            face_index += 1

for n in a.material.node_tree.nodes:
    if n.type != 'TEX_IMAGE':
        continue
    n.interpolation = 'Closest'
    if 'BaseColor' in n.image.name:
        im = n.image
        im.scale(size, size)
        im.pixels.foreach_set(pixels)
        im.filepath_raw = str(a.out / 'StoneStairs_BaseColor.png')
        im.save()
        im.pack()

a.studio(focus=(0, 0, 1.38), location=(-5, -8, 7), scale=4.9)
s.render.resolution_x = 1100
s.render.resolution_y = 1100
s.view_settings.exposure = .3
result = a.save()
result['variant_of'] = 'RiverCrossing'
