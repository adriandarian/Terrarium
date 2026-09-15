"""Shallow independent clay tiles, following the original painted seam layout."""
import hashlib
import json
from pathlib import Path
from meshkit import Mesh

ROOT=Path(__file__).resolve().parents[2]


def build(key='cottage_roof_tile_v5'):
    assert key in ('cottage_roof_tile_v5','cottage_roof_tile_v6_candidate')
    layout_file='Docs/Reconstruction/'+('roof-tile-layout.json' if key=='cottage_roof_tile_v5' else 'roof-tile-v6-layout.json')
    layout=json.loads((ROOT/layout_file).read_text())
    assert hashlib.sha256((ROOT/'SourceAssets/Voxel'/layout['source']).read_bytes()).hexdigest()==layout['source_sha256']
    m=Mesh('SM_Recon_'+key,2502)
    m.box((50,50,1.9),(100,100,3.8),'ffffff',.015,variation=0)
    w,h=layout['size_px'];widths=[];foot_heights=[]
    for row in layout['rows']:
        for tile in row['tiles']:
            # Keep UVs in the original image's full 0..1 domain. The small inset
            # falls inside the painted dark seam rather than cutting a new line.
            x0=max(0,tile['left']+.9);x1=min(w,tile['right']-.9)
            if tile['left']==0:x0=0
            if tile['right']==w:x1=w
            y0=max(0,tile['top']-3);y1=min(h,tile['bottom'])
            dx=x1-x0;dy=y1-y0
            if dx<3 or dy<3:continue
            ct=min(2.5,dy*.1,dx*.1)
            corner_ratio=.13 if key=='cottage_roof_tile_v5' else .025
            cl=min(dx*corner_ratio,dy*.16)*m.rng.uniform(.8,1.1)
            cr=min(dx*corner_ratio,dy*.16)*m.rng.uniform(.8,1.1)
            # The staggered widths come from source seams; the clipped lower
            # corners preserve the source's softened, individually shaped feet.
            outline=[(x0+ct,y0),(x1-ct,y0),(x1,y0+ct),(x1,y1-cr),
                     (x1-cr,y1),(x0+cl,y1),(x0,y1-cl),(x0,y0+ct)]
            cx=(x0+x1)/2;cy=(y0+y1)/2
            offset=m.rng.uniform(-.035,.035)
            def top_z(y):return 4.04+offset+.43*(y-y0)/dy
            vertices=[(x/w*100,y/h*100,3.7) for x,y in outline]
            vertices += [(x/w*100,y/h*100,top_z(y)-.085) for x,y in outline]
            top_outline=[(cx+(x-cx)*.976,cy+(y-cy)*.984) for x,y in outline]
            vertices += [(x/w*100,y/h*100,top_z(y)) for x,y in top_outline]
            faces=[list(range(7,-1,-1)),list(range(16,24))]
            for ring in range(2):
                for i in range(8):
                    j=(i+1)%8;a=ring*8
                    faces.append([a+i,a+j,a+8+j,a+8+i])
            m.solid(vertices,faces,'ffffff',variation=0)
            widths.append(round(dx/w*100,4));foot_heights.append(round(top_z(y1),4))
    assert len(widths)==layout['tile_count']
    m.surface_geometry='source_aligned_individual_roof_tiles'
    m.surface_details={'tile_count':len(widths),'source_row_count':len(layout['rows']),
                       'layout_file':layout_file,
                       'source_texture_unchanged':True,'full_source_uv_domain':[0,1],
                       'tile_width_range_cm':[min(widths),max(widths)],
                       'foot_height_range_cm':[min(foot_heights),max(foot_heights)],
                       'original_20_by_20_cube_grid_removed':True,
                       'original_every_third_row_height_reset_removed':True,
                       'tile_relief_authored_not_inferred_from_luminance':True}
    return m
