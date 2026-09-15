"""Reference traveler: compact dark silhouette with readable ochre clothing.

Keeps the original planted stride and 157 cm crown height. Broad sleeve and
chest color blocks remain visible at the gameplay camera's miniature scale.
"""
from meshkit import Mesh


def build():
    m = Mesh('SM_Traveler_v2', 612)
    for x, y in [(-12, -5), (12, 9)]:
        m.box((x, y-5, 6), (17, 30, 13), '241f19', 3)
        m.beam((x, y, 12), (x, y*.4, 58), 14, '393025')
        m.box((x, y, 23), (17, 18, 18), '29231c', 2)
    m.box((0, 0, 64), (34, 26, 24), '3d3021', 3)
    m.box((0, 0, 94), (42, 31, 47), 'b88126', 5)
    m.box((0, -17, 93), (27, 5, 38), 'd6a143', 2)
    for x in [-18, 18]:
        m.box((x, -16, 90), (7, 7, 41), '473321', 2)
    m.box((0, -20, 77), (40, 6, 7), '30251a', 1)
    m.box((3, -24, 77), (9, 3, 8), 'b19450', 1)
    for x, dy in [(-26, -5), (26, 8)]:
        m.beam((x*.75, 0, 108), (x, dy, 83), 15, 'c49130')
        m.beam((x, dy, 83), (x*.93, dy-4, 65), 11, '9d6b32')
        m.box((x*.93, dy-4, 64), (12, 13, 14), 'c29c6b', 3)
    m.box((0, 0, 122), (12, 14, 14), 'ad8652', 2)
    m.box((0, -3, 138), (28, 26, 27), 'c7a16b', 4)
    m.box((0, 2, 150), (34, 30, 14), '28241c', 4)
    for x, y, z in [(-14, 0, 142), (14, 0, 145), (-7, 12, 140), (7, 12, 139)]:
        m.box((x, y, z), (12, 13, 19), '30281d', 3)
    m.box((0, -18, 132), (21, 5, 10), '68482b', 2)
    for x in [-7, 7]:
        m.box((x, -17, 140), (3, 2, 3), '211f19', .4)
    m.box((0, 19, 97), (35, 18, 37), '614323', 4)
    for x in [-13, 13]:
        m.box((x, 28, 97), (4, 3, 34), 'b38b45', 1)
    m.box((0, 18, 119), (38, 20, 13), 'aa8c48', 4)
    return m.save()
