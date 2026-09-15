"""Relief geometry for each source surface revision; original color UV stays 0..1."""
import functools,json,math
from pathlib import Path
from meshkit import Mesh
DATA=json.loads((Path(__file__).resolve().parents[2]/'Docs/Reconstruction/surfaces-source.json').read_text())
def build(row):
    name=row['name'];m=Mesh('SM_Recon_'+name,100+sum(map(ord,name)))
    if name in ('cottage_roof_tile_v5','cottage_roof_tile_v6_candidate'):
        import roof_surface
        return roof_surface.build(name)
    if name == 'cottage_plaster_v5':
        # Continuous sandstone/plaster: the source has grain, not masonry joints.
        # One planar face keeps the original 0..1 color UVs without grid seams.
        m.box((50,50,2.5),(100,100,5),row['colors'][0],.10,variation=0)
        m.surface_geometry = 'continuous_flat_slab'
        return m
    # Physical 1 m module. Height is authored by surface use, never inferred from painted shadows.
    for y in range(20):
        for x in range(20):
            if 'water' in name:h=5+.30*math.sin((x+y)*.6)+.10*math.sin(x*2.2)
            elif 'cliff' in name:h=6+2*((x//3+y//4)%4)+(.5 if (x+y)%3==0 else 0)
            elif 'roof' in name:h=5+(y%3)*1.5
            elif 'wood' in name:h=6+.15*(x%4)
            elif 'stair' in name:h=7+.12*((x//4+y//4)%3)
            elif 'trail' in name:h=5+.45*((x//3+y//2)%3)
            elif 'foliage' in name or 'moss' in name:h=5+1.4*((x//2+y//3)%3)
            else:h=5+.35*((x//3+y//3)%3)
            m.box(((x+.5)*5,(y+.5)*5,h/2),(4.98,4.98,h),row['colors'][y*20+x],.10,variation=0)
    return m
BUILDERS={r['name']:functools.partial(build,r) for r in DATA}
