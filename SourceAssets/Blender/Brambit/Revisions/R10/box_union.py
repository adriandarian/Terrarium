"""Boundary-only union of axis-aligned construction boxes, using planar quads."""
import bpy
import bmesh
from itertools import product


def box_union(label, sources, scene, material):
    bpy.context.view_layer.update()
    boxes = []
    for source in sources:
        assert all(abs(v) < 1e-7 for v in source.rotation_euler)
        vertices = [source.matrix_world @ v.co for v in source.data.vertices]
        lo = tuple(round(min(v[i] for v in vertices), 6) for i in range(3))
        hi = tuple(round(max(v[i] for v in vertices), 6) for i in range(3))
        boxes.append((lo, hi, source['palette_index']))
    axes = [sorted({b[j][i] for b in boxes for j in (0, 1)}) for i in range(3)]
    indexes = [{value: j for j, value in enumerate(axis)} for axis in axes]
    occupied = {}
    for lo, hi, pigment in boxes:
        ranges = [range(indexes[i][lo[i]], indexes[i][hi[i]]) for i in range(3)]
        for cell in product(*ranges):
            occupied[cell] = pigment

    vertices, faces, pigments, vertex_ids = [], [], [], {}

    def vertex(corner):
        if corner not in vertex_ids:
            vertex_ids[corner] = len(vertices)
            vertices.append(tuple(axes[i][corner[i]] for i in range(3)))
        return vertex_ids[corner]

    for cell, pigment in occupied.items():
        for axis in range(3):
            other = [i for i in range(3) if i != axis]
            for sign in (-1, 1):
                neighbor = list(cell)
                neighbor[axis] += sign
                if tuple(neighbor) in occupied:
                    continue
                corners = []
                for a, b in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    corner = list(cell)
                    corner[axis] += int(sign > 0)
                    corner[other[0]] += a
                    corner[other[1]] += b
                    corners.append(vertex(tuple(corner)))
                faces.append(corners)
                pigments.append(pigment)

    mesh = bpy.data.meshes.new(label)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    uv = mesh.uv_layers.new(name='UVMap')
    for face, pigment in zip(mesh.polygons, pigments):
        color_uv = ((pigment % 8 + .5) / 8, (pigment // 8 + .5) / 8)
        for index in face.loop_indices:
            uv.data[index].uv = color_uv
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(edge.is_manifold for edge in bm.edges), label
    assert bm.calc_volume(signed=True) > 0, label
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    ob = bpy.data.objects.new(label, mesh)
    scene.collection.objects.link(ob)
    ob['union_method'] = 'Axis-aligned cell occupancy; shared internal faces omitted'
    ob['boundary_quads'] = len(faces)
    return ob
