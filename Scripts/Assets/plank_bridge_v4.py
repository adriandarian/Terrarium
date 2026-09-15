"""Slender reference footbridge; identical v3 deck footprint and approach anchors."""
from meshkit import Mesh


def build():
    m = Mesh('SM_PlankBridge_v4', 451)
    m.refinement_pass = 7
    m.revises = 'SM_PlankBridge_v3'
    # Deck center stays at z58. Stringers intersect both boards and trestles.
    for x in (-74, 74):
        m.box((x, 0, 37.5), (15, 537, 25), '51402b', 4)
    # Thirteen broad planks add smaller-scale wear without narrow striping.
    for i in range(13):
        y = -246 + i * 41
        z = 58 + m.rng.uniform(-1.1, 1.1)
        width = 191 + m.rng.uniform(-3, 3)
        m.box((0, y, z), (width, 38.5 + m.rng.uniform(-.6, .6), 20),
              m.rng.choice(['806036', '89673a', '927042', '775a32', '947748']), 3.7)
        # Wear and pegs intersect the board surface, avoiding floating overlays.
        for x in (-72, 72):
            m.box((x, y, z + 9.8), (3.5, 3.5, 1.1), '514730', .4)
        for j in range(2 + i % 2):
            m.box((m.rng.uniform(-43, 43), y + m.rng.uniform(-12, 12), z + 9.95),
                  (m.rng.uniform(21, 53), m.rng.uniform(.7, 1.4), .6),
                  m.rng.choice(['6c512f', '9b7c4a']), .1)
        if i % 3 == 1:
            # A dark short split at the end grain; it remains on the plank.
            m.box((m.rng.choice([-82, 82]), y + 7, z + 9.9), (20, 1.4, .7), '4e4027', .1)

    # Low, thin handrails retain the side stations but expose much more scenery.
    # Rails explicitly terminate inside posts so variation cannot open joints.
    for x in (-104, 104):
        stations = [(-245, 109), (-9 if x < 0 else 12, 112), (245, 108)]
        for y, top in stations:
            # Half-transoms tie every rail post into its load-bearing stringer.
            m.box((x * .80, y, 44), (55, 12, 12), '675032', 2)
            m.box((x, y, (top + 34) / 2), (11, 12, top - 34), '73552f', 2.6)
            m.box((x, y, top - 1), (13, 14, 4), '987745', 2)
            m.box((x, y - 5.8, top - 12), (3, 1.0, 3), '55432d', .4)
        for (y0, z0), (y1, z1) in zip(stations, stations[1:]):
            m.beam((x, y0, z0 - 9), (x, y1, z1 - 9), 7.0, '927347', 8)
            m.beam((x, y0, 77), (x, y1, 78), 4.5, '6a522f', 5)

    # Four slender end piles keep the submerged bearing depth while the center
    # span is open. Removing its central trestle is the main silhouette change.
    # With scene z222, pile bottoms still reach world z-18 beneath the river.
    for y in (-194, 194):
        for x in (-76, 76):
            m.box((x, y, -98), (13, 16, 284), '55432d', 2.1)
            for z in (-157, -130):
                m.box((x, y, z), (13.5, 16.5, 4), '526037', 1)
        m.box((0, y, 24), (176, 17, 16), '695030', 2)
        # One thin diagonal at each end, alternating directions, supports the
        # end trestles without another conspicuous X over the water.
        direction = -1 if y < 0 else 1
        m.beam((-74*direction, y, -121), (74*direction, y, 26), 6, '59462a')
    for y in (-267, 267):
        m.box((0, y, 25), (199, 32, 20), '6c7056', 3)
        # Compact shoulders disappear into the existing approach dressing.
        for x in (-93, 93):
            m.box((x, y, 34), (10, 19, 3), '677340', 1)
    return m.save()
