"""Blender-authored cottage, measured against SourceAssets/Voxel/cottage.png.

Metres; Z up; facade faces -Y. Run in the verified Terrarium Blender session.
Retains the original scene and all earlier Unreal assets. No image billboards.
"""
import bpy, math, random, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path('C:/Users/hello/Projects/Terrarium')
OUT=ROOT/'SourceAssets/Blender/Cottage'
REVIEW=ROOT/'Docs/BlenderRebuild/Cottage'
OUT.mkdir(parents=True,exist_ok=True)
REVIEW.mkdir(parents=True,exist_ok=True)
NAME='Terrarium_Cottage'
assert bpy.data.filepath in ('',str(OUT/'Cottage.blend').replace('\\','/')) or bpy.context.scene.get('terrarium_project')==str(ROOT)
if NAME in bpy.data.scenes:
    old=bpy.data.scenes[NAME]
    for obj in list(old.objects):
        bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(old)
scene=bpy.data.scenes.new(NAME)
bpy.context.window.scene=scene
scene['terrarium_project']=str(ROOT)
scene['concept']='SourceAssets/Voxel/cottage.png'
scene['fidelity_status']='work_in_progress_requires_visual_comparison'
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1
rng=random.Random(411)
parts=[]
PALETTE=['a6a491','959582','b6b29a','878a79',
         '795331','684626','845d37','98622f',
         'ece0bd','e6d9b4','c5692f','bc602b','cd7336','b65a27',
         '758a2b','899e32','627823','9bae40',
         '167f77','12665f','21948a','dbac40',
         'eee4ac','e58a30','302a20','64754c']

def lin(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

def atlas():
    size=512;cell=64
    im=bpy.data.images.new('Cottage_BaseColor',width=size,height=size,alpha=False)
    pix=[]
    for y in range(size):
        for x in range(size):
            idx=min((y//cell)*8+x//cell,len(PALETTE)-1)
            col=PALETTE[idx];rgb=[int(col[k:k+2],16)/255 for k in (0,2,4)]
            # Subtle material pigment only; lighting comes from actual geometry.
            n=.99+.012*math.sin(x*.27+y*.17)+.007*math.sin(x*.71-y*.38)
            if 4<=idx<=7:n+=.018*math.sin(x*.63+math.sin(y*.035))
            pix.extend([min(1,c*n) for c in rgb]+[1])
    im.pixels.foreach_set(pix)
    im.filepath_raw=str(OUT/'Cottage_BaseColor.png');im.file_format='PNG';im.save();im.pack()
    mat=bpy.data.materials.new('M_Cottage_Atlas');mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
    bs.inputs['Specular IOR Level'].default_value=.24
    tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im
    mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
    return mat
MAT=atlas()

def box(label,p,s,idx,bev=.012):
    # Outward winding, six full faces, explicit UVs per component.
    w,d,h=[v/2 for v in s]
    vs=[(-w,-d,-h),(w,-d,-h),(w,d,-h),(-w,d,-h),(-w,-d,h),(w,-d,h),(w,d,h),(-w,d,h)]
    fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(label);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(label,me);scene.collection.objects.link(ob);ob.location=p
    me.materials.append(MAT);uv=me.uv_layers.new(name='UVMap')
    u0=(idx%8)/8+.008;v0=(idx//8)/8+.008
    for poly in me.polygons:
        for li,co in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):
            uv.data[li].uv=(u0+co[0]*.109,v0+co[1]*.109)
    if bev:
        mod=ob.modifiers.new('Crafted edge bevel','BEVEL');mod.width=min(bev,min(s)*.12);mod.segments=2
        mod=ob.modifiers.new('Weighted face normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=40
    ob['part']=label;parts.append(ob)
    return ob

def roof_tile(p,idx):
    """Four shallow-jointed subtiles preserve each large stepped roof course."""
    x,y,z=p
    for dx in [-.0675,.0675]:
        for dy in [-.0675,.0675]:
            for dz in [-.0515,.0515]:
                box('Terracotta roof tile',(x+dx,y+dy,z+dz),(.134,.134,.102),idx,.004)

def masonry(label,p,s,cw=.28,ch=.19):
    x,y,z=p;w,d,h=s
    rows=max(1,round(h/ch))
    for row in range(rows):
        step=w/max(1,round(w/cw));edges=[-w/2]
        edges += [t for i in range(round(w/step)+1) if -w/2<(t:=-w/2+(i+(.5 if row%2 else 0))*step)<w/2]
        edges += [w/2]
        for a,b in zip(edges,edges[1:]):
            box(label,(x+(a+b)/2,y,z-h/2+(row+.5)*h/rows),(b-a-.007,d,h/rows-.007),rng.choice([0,0,1,2,3]),.009)

def window(x,y,z,w=.67,h=.88):
    box('Window recessed shadow',(x,y+.06,z),(w,.08,h),24,.003)
    for a in [-1,1]:
        for b in [-1,1]:
            box('Teal inset pane',(x+a*w*.22,y+.002,z+b*h*.22),(w*.39,.07,h*.4),19 if a<0 else 18,.008)
    box('Window mullion upright',(x,y-.055,z),(.068,.10,h),18,.008)
    box('Window mullion cross',(x,y-.055,z),(w,.10,.058),20,.005)
    for a in [-1,1]:box('Window timber jamb',(x+a*(w/2+.04),y-.085,z),(.095,.16,h+.07),4,.014)
    box('Window timber lintel',(x,y-.09,z+h/2+.055),(w+.2,.17,.11),4,.013)
    box('Projecting window sill',(x,y-.16,z-h/2-.065),(w+.26,.31,.125),4,.016)

# Low stone foundation closely follows the building footprint.
box('Foundation solid core',(0,0,.275),(4.40,3.25,.55),1)
masonry('Front foundation blocks',(0,-1.67,.285),(4.54,.24,.57))
masonry('Rear foundation blocks',(0,1.67,.285),(4.54,.24,.57))
for side in [-1,1]:
    for row in range(3):
        for j in range(12):box('Side footing block',(side*2.2,-1.51+(j+.5)*3.02/12,(row+.5)*.19),(.26,3.02/12-.007,.183),rng.choice([0,1,2,3]),.009)

# Separate infill panels leave real recesses for window/door construction.
box('Plaster building core',(0,.09,1.40),(4.06,2.90,1.70),8,.006)
for side in [-1,1]:
    box('Facade outer plaster',(side*1.92,-1.55,1.43),(.26,.23,1.76),8,.006)
    box('Facade central plaster',(side*.69,-1.55,1.43),(.34,.23,1.76),8,.006)
    box('Window lower plaster',(side*1.28,-1.55,.80),(.83,.23,.50),9,.005)
    box('Window upper plaster',(side*1.28,-1.55,2.12),(.83,.23,.37),8,.005)
    for y in [-1.56,1.48]:box('Corner timber post',(side*2.06,y,1.48),(.24,.27,1.86),4,.022)
box('Facade upper beam',(0,-1.67,2.34),(4.45,.28,.25),5,.018)
for side in [-1,1]:box('Side eave beam',(side*2.19,0,2.35),(.25,3.65,.25),4,.018)
box('Rear beam',(0,1.59,2.34),(4.45,.26,.25),5,.018)
for side in [-1,1]:window(side*1.28,-1.68,1.48)

# Door has five physical planks, framed reveals and a cuboid brass latch.
box('Door recess',(0,-1.61,1.19),(1.08,.14,1.47),24,.008)
for j in range(5):box('Door vertical plank',(-.415+j*.207,-1.735,1.2),(.203,.10,1.43),7 if j%2 else 10,.009)
for side in [-1,1]:box('Door jamb',(side*.57,-1.80,1.22),(.17,.25,1.60),4,.019)
box('Door header',(0,-1.80,2.02),(1.33,.24,.16),4,.016)
box('Brass door handle',(.34,-1.865,1.17),(.15,.12,.16),21,.012)
for j in range(3):
    h=.18*(3-j);y=-1.85-.29*j
    masonry('Front stair',(0,y,h/2),(1.22,.34,h),cw=.40,ch=.18)
    for side in [-1,1]:box('Stair timber cheek',(side*.73,y,h/2+.08),(.25,.34,h+.16),5,.015)

# Stepped plaster gable fits underneath the front fascia, without protrusions.
for ix in range(10):
    x=(ix-4.5)*.27
    top=2.51+max(0,5-math.floor(abs(x)/.27))*.185-.31
    bottom=2.42
    if top>bottom:
        box('Front gable plaster',(x,-1.78,(top+bottom)/2),(.27,.18,top-bottom),8,.004)
box('Gable upright',(0,-1.90,2.80),(.20,.16,.74),5,.012)

# Main ridge runs X; front cross-gable runs Y. Roof tiles are individual solids.
step=.27;cols=18;rows=15
for iy in range(rows):
    y=(iy-(rows-1)/2)*step
    main=2.51+(7-abs(iy-7))*.185
    for ix in range(cols):
        x=(ix-(cols-1)/2)*step
        cross=2.51+max(0,5-math.floor(abs(x)/step))*.185 if y<.10 else 0
        top=max(main,cross)
        roof_tile((x,y,top),rng.choice([10,10,11,12,13]))
        # Filled structure below raised cross-gable steps, no suspended roof blocks.
        if cross>main+.05 and iy>0:
            box('Cross-gable tile riser',(x,y,(cross+main)/2-.04),(step-.006,step-.005,cross-main+.09),10,.008)
        if iy==0:
            box('Stepped gable timber fascia',(x,y-.035,top-.205),(step-.003,.31,.21),5,.014)
        if ix in [0,cols-1]:
            box('Outer eave timber',(x,y,top-.205),(step,.28,.21),4,.013)
    if main>2.72:
        box('Enclosed roof core',(0,y,(2.43+main-.22)/2),(4.33,.27,main-.22-2.43),9,.003)

# Tall pale stone chimney on the source's left roof slope.
cx=-1.62;cy=.26
box('Chimney interior',(cx,cy,3.67),(.57,.55,1.58),1,.006)
for row in range(7):
    z=3.04+row*.19
    for k in range(2):
        box('Chimney front masonry',(cx+(k-.5)*.29,cy-.30,z),(.282,.12,.183),[0,2,1][row%3],.008)
        box('Chimney rear masonry',(cx+(k-.5)*.29,cy+.30,z),(.282,.12,.183),[0,2,1][row%3],.008)
        box('Chimney side masonry',(cx-.30,cy+(k-.5)*.29,z),(.12,.282,.183),[2,0,1][row%3],.008)
        box('Chimney side masonry',(cx+.30,cy+(k-.5)*.29,z),(.12,.282,.183),[2,0,1][row%3],.008)
for x in [-1,1]:
    for y in [-1,1]:box('Chimney stone cap',(cx+x*.20,cy+y*.20,4.40),(.394,.394,.22),2,.013)
for x in [-1,1]:
    for y in [-1,1]:box('Chimney clay crown',(cx+x*.12,cy+y*.12,4.64),(.234,.234,.27),10,.010)

# The footing has tiered moss clumps and two tiny flower clusters.
for side in [-1,1]:
    clumps=[[(0,-1),(1,-1),(2,-1),(3,0),(0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(3,1)],
            [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(3,1),(1,2),(2,2)],
            [(0,1),(1,0),(1,1),(2,1),(1,2),(2,2)],[(0,2),(1,2)]]
    for layer,coords in enumerate(clumps):
        for ix,iy in coords:
            x=side*(1.66+ix*.19);y=-1.99+iy*.18
            box('Moss corner cushion',(x,y,.60+layer*.165),(.20,.20,.185),rng.choice([14,15,16,17]),.010)
    for ix in range(4):
        for iy in range(3):
            if ix+iy>4:continue
            x=side*(1.62+ix*.20);y=-2.07+iy*.18
            for row in range(2):box('Stepped planter stone',(x,y,.11+row*.20),(.22,.23,.193),rng.choice([0,1,2]),.008)
            box('Low moss lip',(x,y-.02,.47),(.215,.24,.13),rng.choice([14,15,16]),.009)
    for j in range(12):
        y=-1.32+j*.245
        if rng.random()<.8:box('Side creeping moss',(side*2.28,y,.57+rng.choice([0,.13])),(.23,.26,.20),rng.choice([14,15,16]),.014)
    for a,b,z in [(0,0,1.09),(.11,.015,.98),(-.09,-.03,.99),(.015,-.09,.97)]:
        box('Ivory flower' if side<0 else 'Ochre flower',(side*1.91+a,-2.0+b,z),(.11,.11,.13),22 if side<0 else 23,.005)
for x,y,z in [(-2.35,-1.70,.32),(2.34,-1.75,.20),(1.97,-1.87,.32),(-1.56,-1.82,.37)]:
    box('Footing moss spill',(x,y,z),(.22,.22,.22),16,.013)

# Studio lighting is separate from exportable asset geometry.
def area(label,loc,power,size,color):
    data=bpy.data.lights.new(label,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    ob=bpy.data.objects.new(label,data);scene.collection.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler()
area('Warm large key',(-4,-6,9),1100,5,(1,.88,.72))
area('Soft cool fill',(5,-3,5),700,5,(.80,.91,1))
area('Top rim',(1,5,8),1000,4,(1,.95,.83))
world=bpy.data.worlds.new('Cottage studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.36,.40,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;scene.world=world
camdata=bpy.data.cameras.new('Concept comparison camera');cam=bpy.data.objects.new('Concept comparison camera',camdata);scene.collection.objects.link(cam)
cam.location=(-3.5,-13,8.3);target=Vector((0,-.1,2.23));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=6.70;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.45
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(REVIEW/'front.png')
for ob in scene.objects:ob.select_set(False)
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.context.view_layer.update()
for ar in bpy.context.screen.areas:
    if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Cottage.blend'))
result={'scene':scene.name,'revision':2,'parts':len(parts),'blend':str(OUT/'Cottage.blend'),'status':'authored_awaiting_render'}
(REVIEW/'build.json').write_text(json.dumps(result,indent=2))
