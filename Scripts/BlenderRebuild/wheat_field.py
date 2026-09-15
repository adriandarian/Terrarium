"""Dense cuboid wheat from wheat_field.png; reusable stalks also form a placement patch."""
import sys, random, math, json
sys.path.insert(0, 'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import bpy
from assetkit import Asset

def build(key='WheatField', nx=32, ny=20, spacing=.17, border=True):
    palette = [('b69a20','timber'), ('c5aa24','timber'), ('d6ba2b','timber'),
               ('e5c637','timber'), ('f0da50','timber'), ('b59c20','timber'),
               ('6b8627','timber'), ('8ba52f','timber'), ('526c20','timber'),
               ('8f9e30','timber')]
    a = Asset(key, 'wheat_field.png', palette)
    rng = random.Random(133913)
    s = a.scene
    s['stalk_count'] = nx * ny
    s['stalk_grid'] = [nx, ny]
    s['spacing_m'] = spacing
    if key != 'WheatField':
        s['variant_of'] = 'WheatField'
        s['variant_purpose'] = 'Crop-only module using the canonical cuboid stalk design; border greenery omitted between adjacent world patches.'
    def block(label, pos, size, color, plant=-1, top=None):
        ob = a.box(label, pos, size, color, 0, top_index=top)
        ob['plant'] = plant
        return ob
    for iy in range(ny):
        for ix in range(nx):
            plant = iy * nx + ix
            x = (ix-(nx-1)/2)*spacing + rng.uniform(-.027,.027)
            y = (iy-(ny-1)/2)*spacing + rng.uniform(-.028,.028)
            h = rng.uniform(.62, .94)
            # The reference has squared, upright shafts with small forks near their tips.
            w = rng.uniform(.040,.050)
            stem_top = h - .19
            for course in range(4):
                block('Squared wheat shaft course', (x,y,(course+.5)*stem_top/4), (w,w,stem_top/4), rng.choice([0,1,2,5]), plant, 3)
            block('Central grain column', (x,y,stem_top+.075), (.047,.041,.15), rng.choice([1,2,3]), plant, 4)
            block('Upright grain tip', (x,y,h-.021), (.030,.029,.042), 3, plant, 4)
            axis = rng.randrange(2)
            for side in [-1,1]:
                offset = .044 * side
                z = stem_top + rng.uniform(.018,.065)
                p = (x+offset/2,y,z) if axis == 0 else (x,y+offset/2,z)
                size = (.06,.030,.032) if axis == 0 else (.030,.06,.032)
                block('Squared grain fork', p, size, 2, plant, 3)
                rise = rng.uniform(.075,.142)
                p = (x+offset,y,z+rise/2) if axis == 0 else (x,y+offset,z+rise/2)
                block('Side grain prong', p, (.031,.031,rise), rng.choice([1,2,3]), plant, 4)
    if border:
        for iy in range(ny):
            for ix in range(nx):
                x=(ix-(nx-1)/2)*spacing;y=(iy-(ny-1)/2)*spacing
                block('Root bed voxel',(x,y,.018),(spacing,spacing,.036),rng.choice([6,8,8]),top=6)
        # Sparse, stepped cubes at the outer roots; no enclosing box around the crop.
        for ix in range(-1,nx+1):
            for side in [-1,1]:
                if rng.random() < .55: continue
                x = (ix-(nx-1)/2)*spacing
                y = side*(ny/2*spacing+rng.uniform(-.07,.06))
                for tier in range(rng.choice([1,1,2])):
                    block('Green border tuft',(x,y,tier*.075+.0375),(.092,.094,.075),rng.choice([6,7,8,9]),top=7)
                if rng.random()<.75:
                    block('Green border side lobe',(x+.085,y+side*.03,.03),(.085,.090,.060),8,top=7)
        for iy in range(ny):
            for side in [-1,1]:
                if rng.random()<.65:continue
                x=side*(nx/2*spacing+rng.uniform(-.07,.02));y=(iy-(ny-1)/2)*spacing
                block('Green side tuft',(x,y,.045),(.095,.09,.09),8,top=7)
    # Palette hex values denote display sRGB. Store them with the correct linear transfer.
    for node in a.material.node_tree.nodes:
        if node.type != 'TEX_IMAGE':continue
        node.interpolation = 'Closest'
        if 'BaseColor' not in node.image.name:continue
        im = node.image
        values = list(im.pixels)
        for i in range(0,len(values),4):
            for j in range(3):
                v=values[i+j]
                values[i+j]=v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
        im.pixels.foreach_set(values);im.save();im.pack()
    width = nx*spacing
    depth = ny*spacing
    a.studio(focus=(0,0,.37), location=(7,-10,8), scale=max(2.65,max(width,depth)*1.35))
    for ob in s.objects:
        if ob.type=='LIGHT' and ob.data.name.startswith('Key'):
            ob.data.color=(1,.98,.90);ob.data.energy=1100;ob.data.size=6
    s.render.resolution_x=1400;s.render.resolution_y=1000
    s.view_settings.exposure=.15
    roots = {o['plant']: [o.location.x, o.location.y] for o in a.parts if o.get('part') == 'Squared wheat shaft course'}
    (a.review/'stalk-roots.json').write_text(json.dumps({'asset': key, 'roots_xy_m': list(roots.values())}, indent=2))
    return a.save()

if __name__ == '__main__':
    result = build()
