"""Weathered stairs with worn stone joints and rooted grass at the sides."""
from meshkit import Mesh


def build():
    m = Mesh('SM_StoneStairs_v3', 244)
    m.refinement_pass = 7
    m.revises = 'SM_StoneStairs_v2'
    # Preserve eight 30cm rises at y=-147..147, and upper tread top z249.
    for i in range(8):
        y = -147 + i * 42
        h = 30 * (i + 1)
        m.box((0, y, h / 2), (200, 43, h), 'stone_dark', 5)
        # Offset the joints between steps, preserving the 200cm walking width.
        split = [-100, -43, 25, 100] if i % 2 else [-100, -28, 40, 100]
        for j in range(3):
            x = (split[j] + split[j + 1]) / 2
            width = split[j + 1] - split[j] - 1
            shift = m.rng.uniform(-1, 1)
            m.box((x, y + shift, h + 3), (width, 45, 12),
                  m.rng.choice(['8d8268', 'a49a7b', '999374', '92886e']),
                  4.5 + m.rng.uniform(0, 1))
            # Short embedded front chips break long pristine nosing lines.
            m.box((x + m.rng.uniform(-12, 12), y + shift - 21.5, h + 1),
                  (m.rng.uniform(6, 13), 2, 3), '695f4b', .7)
        for side, x in enumerate((-111, 111)):
            for k in range(i + 1):
                m.box((x, y, k * 30 + 22), (24, 41, 31),
                      m.rng.choice(['stone', 'stone_dark', '7f775f']), 4)
            # Low, varying edge stones replace the higher continuous parapet.
            cap_top = h + 13 + (i + side) % 3 * 2
            m.box((x, y, cap_top - 5), (28, 42, 10),
                  m.rng.choice(['7d8350', '8b8960', '807c59']), 3.8)
            if (i + side) % 3 != 1:
                # Embedded moss patches at actual cap height, plus fine tufts.
                m.box((x, y + 6, cap_top - .2), (15, 17, 2), '657132', .6)
                for d in (-4, 2, 6):
                    m.beam((x, y + d, cap_top - .5),
                           (x + side * 4 - 2, y + d + 1, cap_top + 7 + d / 2),
                           1.2, m.rng.choice(['819045', '6c793e']))
    return m.save()
