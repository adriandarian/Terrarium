"""River coverage with turquoise shallows selected from actual terrain proximity."""
import math
import reference as ref
from placement import place_xyz


def choose_variant(x, y):
    # Sample through a tile and just beyond it. Real land is authoritative,
    # avoiding invented shallows across the center of an open channel.
    for radius in (95, 185, 285):
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            if ref.height(x+math.cos(a)*radius, y+math.sin(a)*radius) is not None:
                return 'WaterShallow_v4' if radius <= 185 else 'WaterTile_v4'
    return 'WaterDeep_v4'


def specs():
    for x in range(-3900, 3901, 300):
        for y in range(-4400, 4401, 300):
            px, py = ref.pixel(x, y, 0)
            if -150 < px < 650 and 340 < py < 850:
                yield choose_variant(x, y), (x, y, 0)


def build(cells=None):
    # Same uninterrupted footprint as the original coverage. Keeping the
    # common yaw also preserves the river's coherent ripple direction.
    for name, xyz in specs():
        place_xyz(name, xyz, 1, 0, 'River')
