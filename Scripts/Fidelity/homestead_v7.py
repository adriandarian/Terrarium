"""Compact cottage and well, with a fuller mixed kitchen garden for pass seven."""
import reference as ref
from placement import place, place_xyz
from homestead import fence


def build():
    place('Cottage_v6', 260, 308, 568, 1.08, 90, 'Buildings', False)
    place('Shed_v2', 132, 351, 568, .87, 90, 'Buildings', False)
    # The same well ground anchor with 22% less height/width than the old 1.08.
    place('GardenWell_v2', 351, 352, 568, .84, 90, 'Garden', False)
    place('LanternPost', 273, 369, 568, 1.25, 0, 'Garden', False)
    # A broad mixed bed replaces the narrow main bed. The smaller companion
    # bed remains east of the well, clear of both its base and the garden path.
    place('GardenBed_v3', 306, 356, 570, 1.03, 0, 'Garden', False)
    place('GardenBed_v2', 379, 348, 570, .65, 0, 'Garden', False)
    fence([(265, 353), (328, 319), (411, 339), (352, 383)], 560)
    fence([(146, 310), (165, 300), (188, 287), (211, 291)], 560)
    # Keep the established wheat extent and spacing; crop-field redesign is
    # outside this kitchen-garden change.
    corners = [ref.world(*p, 880) for p in ref.WHEAT]
    x0, x1 = min(p[0] for p in corners), max(p[0] for p in corners)
    y0, y1 = min(p[1] for p in corners), max(p[1] for p in corners)
    for x in range(int(x0), int(x1) + 1, 110):
        for y in range(int(y0), int(y1) + 1, 110):
            if ref.inside(ref.pixel(x, y, 880), ref.WHEAT):
                place_xyz('WheatPatch_v2', (x, y, 890), (.48, .48, .8), 0, 'Wheat')
