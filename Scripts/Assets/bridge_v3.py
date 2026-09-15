"""Worn lightweight footbridge; preserves the v2 deck and submerged supports."""
from meshkit import Mesh


def build():
    m = Mesh('SM_PlankBridge_v3', 451)
    m.refinement_pass = 7
    m.revises = 'SM_PlankBridge_v2'
    # Deck center stays at z58. Stringers intersect both boards and trestles.
    for x in (-74, 74):
        m.box((x, 0, 30.5), (23, 537, 39), '51402b', 4)
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

    # Three lighter posts per side replace four thick, regularly capped posts.
    # Rails explicitly terminate inside posts so variation cannot open joints.
    for x in (-104, 104):
        stations = [(-245, 139), (-9 if x < 0 else 12, 143), (245, 138)]
        for y, top in stations:
            # Half-transoms tie every rail post into its load-bearing stringer.
            m.box((x * .73, y, 41), (70, 18, 17), '675032', 2)
            m.box((x, y, (top + 8) / 2), (17, 18, top - 8), '73552f', 2.6)
            m.box((x, y, top - 1), (20, 21, 7), '987745', 2)
            m.box((x, y - 8.8, top - 15), (5, 1.2, 5), '55432d', .4)
        for (y0, z0), (y1, z1) in zip(stations, stations[1:]):
            m.beam((x, y0, z0 - 12), (x, y1, z1 - 12), 10.5, '927347', 12)
            m.beam((x, y0, 85), (x, y1, 86), 7.5, '6a522f', 8)

    # Original support footprint retained: six piles reach local z-240,
    # world z-18 at the scene's z222 placement, below the river surface.
    for y in (-194, 0, 194):
        for x in (-76, 76):
            m.box((x, y, -92), (24, 27, 296), '5c472b', 3.8)
            for z in (-157, -130):
                m.box((x, y, z), (25, 28, 7), '526037', 1.6)
        m.box((0, y, 19), (190, 28, 23), '695030', 3)
        m.beam((-74, y, -154), (74, y, 16), 9.5, '4f3e27')
        m.beam((74, y, -154), (-74, y, 16), 9.5, '59462a')
    for y in (-267, 267):
        m.box((0, y, 18), (229, 49, 34), '6c7056', 5)
        # Moss stays on the abutment shoulders, clear of the walking deck.
        for x in (-105, 105):
            m.box((x, y, 34), (15, 25, 4), '677340', 1.4)
    return m.save()
