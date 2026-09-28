"""Bounded detail study; creates new datablocks, never executes old constructors.

Run through verified Blender Lab MCP. No canonical source file is overwritten.
"""
import bpy, math, random, json, ast
from pathlib import Path
from mathutils import Vector

ROOT=Path('C:/Users/hello/Projects/Terrarium')
OUT=ROOT/'SourceAssets/Blender/DetailCalibration'
DOC=ROOT/'Docs/DetailCalibration'
assert Path(bpy.context.scene.get('terrarium_project',''))==ROOT
assert 'Terrarium_DetailCalibration' not in bpy.data.scenes, 'Do not overwrite an existing review scene'
old_scene=bpy.context.window.scene
scene=bpy.data.scenes.new('Terrarium_DetailCalibration')
scene['terrarium_project']=str(ROOT)
scene['status']='Provisional dimensions; construction study awaiting visual selection'
scene['scope']='Five fixed-envelope families, coarse / half / third, 1.8 m scale person'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.context.window.scene=scene
palette=[('Stone','74765a'),('StoneLight','929178'),('StoneDark','5c6049'),('Grass','68762d'),('GrassLight','84923e'),('Leaf','6e771d'),('LeafLight','89902a'),('LeafDark','495918'),('Wood','795226'),('WoodLight','986c33'),('Roof','b96230'),('RoofLight','ce783d'),('Plaster','e5d6af'),('Teal','277b70'),('Iron','484d45'),('Person','dda743')]
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
mats=[]
for name,h in palette:
    m=bpy.data.materials.new('M_DC_'+name);m.use_nodes=True
    color=tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1,)
    m.diffuse_color=color;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.88
    mats.append(m)
class Builder:
    def __init__(self,key,offset):
        self.key=key;self.offset=Vector(offset);self.parts={};self.collection=bpy.data.collections.new(key);scene.collection.children.link(self.collection)
    def mesh(self,part,verts,faces,mi):
        v,f,mat=self.parts.setdefault(part,([],[],[]));n=len(v);v.extend(verts);f.extend(tuple(n+i for i in p) for p in faces);mat.extend([mi]*len(faces))
    def box(self,part,p,s,mi):
        x,y,z=p;a,b,c=[v/2 for v in s]
        self.mesh(part,[(x+dx*a,y+dy*b,z+dz*c) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mi)
    def stone(self,p,s,mi,side=0):
        x,y,z=p;w,d,h=s;cut=min(w,h)*.10
        outline=[(-w/2+cut,-h/2),(w/2-cut,-h/2),(w/2,-h/2+cut),(w/2,h/2-cut),(w/2-cut,h/2),(-w/2+cut,h/2),(-w/2,h/2-cut),(-w/2,-h/2+cut)]
        verts=[]
        for depth in [-d/2,d/2]:
            for u,v in outline:verts.append((x+u,y+depth,z+v) if side==0 else (x+depth,y+u,z+v))
        faces=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
        # Winding is repaired on final mesh, since side orientation swaps axes.
        self.mesh('StoneCourses',verts,faces,mi)
    def voxels(self,part,cells,cell,mi=5):
        # Only exposed faces. No hidden voxel boxes or internal faces are emitted.
        dirs=[((-1,0,0),[(0,0,0),(0,0,1),(0,1,1),(0,1,0)]),((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),((0,-1,0),[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),((0,1,0),[(0,1,0),(0,1,1),(1,1,1),(1,1,0)]),((0,0,-1),[(0,0,0),(0,1,0),(1,1,0),(1,0,0)]),((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)])]
        for x,y,z in sorted(cells):
            for (dx,dy,dz),corners in dirs:
                if (x+dx,y+dy,z+dz) in cells:continue
                col=mi+(0 if (x*7+y*3+z)%7<4 else (1 if dz>=0 else 2)) if mi==5 else mi
                self.mesh(part,[((x+a)*cell,(y+b)*cell,(z+c)*cell) for a,b,c in corners],[(0,1,2,3)],col)
    def finish(self,bounds):
        import bmesh
        allv=[p for v,f,m in self.parts.values() for p in v]
        lo=[min(p[i] for p in allv) for i in range(3)];hi=[max(p[i] for p in allv) for i in range(3)]
        if 'SteppedTrunk' in self.parts:
            crown=[p for part,(v,f,m) in self.parts.items() if part!='SteppedTrunk' for p in v]
            crown_lo=[min(p[i] for p in crown) for i in [0,1]];crown_hi=[max(p[i] for p in crown) for i in [0,1]]
        self.objects=[]
        for part,(v,f,mi) in self.parts.items():
            vs=[tuple((p[i]-lo[i])/(hi[i]-lo[i])*bounds[i]-(bounds[i]/2 if i<2 else 0) for i in range(3)) for p in v]
            if part=='SteppedTrunk':vs=[(p[0]*.85,p[1]*.4,p[2]) for p in vs]
            elif 'SteppedTrunk' in self.parts:vs=[tuple((raw[i]-crown_lo[i])/(crown_hi[i]-crown_lo[i])*bounds[i]-bounds[i]/2 for i in [0,1])+(p[2],) for raw,p in zip(v,vs)]
            me=bpy.data.meshes.new(self.key+'_'+part);me.from_pydata(vs,[],f);me.update()
            for m in mats:me.materials.append(m)
            for p,m in zip(me.polygons,mi):p.material_index=m
            bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.update()
            ob=bpy.data.objects.new(self.key+'_'+part,me);self.collection.objects.link(ob);ob.location=self.offset;ob['calibration_part']=part;self.objects.append(ob)
        return self

def cliff(b,n):
    b.box('Core',(0,0,1.14),(2.80,1.30,2.28),2)
    rows=5*n;h=2.28/rows;step=.58/n
    for side,length,plane in [(0,3,-.73),(1,1.5,1.43)]:
        for row in range(rows):
            edges=[-length/2]+[q for i in range(math.ceil(length/step)+2) if -length/2<(q:=-length/2+(i+(.5 if row%2 else 0))*step)<length/2]+[length/2]
            for j,(a,c) in enumerate(zip(edges,edges[1:])):
                depth=.11+.018*((row*3+j)%3);p=((a+c)/2,plane,(row+.5)*h) if side==0 else (plane,(a+c)/2,(row+.5)*h)
                b.stone(p,(c-a-.009,depth,h-.012),[0,1,0,2][(row+j)%4],side)
    cell=.30/n;nx=round(3/cell);ny=round(1.5/cell)
    for ix in range(nx):
        for iy in range(ny):
            # Smaller root/grass silhouette bites and staggered overhangs, fixed cap top.
            depth=.07+(.06/n if (ix*7+iy*3)%5<2 else 0)
            b.box('GrassCap',(-1.5+(ix+.5)*3/nx,-.75+(iy+.5)*1.5/ny,2.4-depth/2),(3/nx-.003,1.5/ny-.003,depth),3+(ix+iy)%2)

def cottage(b,n):
    b.box('Wall', (0,.2,1.1),(2.2,.75,2.2),12)
    for row in range(3*n):
        count=7*n
        for j in range(count):b.box('Footing',(-1.1+(j+.5)*2.2/count,-.23,(row+.5)*.42/(3*n)),(2.2/count-.006,.22,.42/(3*n)-.006),[0,1,2][(row+j)%3])
    for x in [-1.04,1.04]:b.box('TimberPosts',(x,-.26,1.30),(.17,.18,1.8),8)
    b.box('Header',(0,-.26,2.18),(2.32,.2,.17),8)
    b.box('WindowShadow',(0,-.204,1.35),(.91,.12,1.01),14)
    b.box('WindowPane',(0,-.28,1.35),(.75,.04,.85),13)
    for x in [-.45,.45]:b.box('WindowFrame',(x,-.35,1.35),(.1,.14,1.04),8)
    for z in [.85,1.85]:b.box('WindowFrame',(0,-.35,z),(1.0,.14,.1),8)
    b.box('WindowMullion',(0,-.38,1.35),(.06,.12,.9),13);b.box('WindowMullion',(0,-.38,1.35),(.85,.12,.055),13)
    # Fixed roof slope/envelope, but actual rise changes .185 / n; no same-course subdivision.
    count=6*n;run=1.62/count;rise=1.11/count;width=2.4;tilew=.27/n
    for row in range(count):
        y=-.65+(row+.5)*run;top=2.29+(row+1)*rise
        edges=[-width/2]+[q for j in range(math.ceil(width/tilew)+1) if -width/2<(q:=-width/2+(j+(.5 if row%2 else 0))*tilew)<width/2]+[width/2]
        for j,(a,c) in enumerate(zip(edges,edges[1:])):b.box('RoofCourses',((a+c)/2,y,top-rise*.48),(c-a-.004,run+.014,rise*.96),10+(row+j)%2)
        for x in [-1.15,1.15]:b.box('SteppedFascia',(x,y,top-rise-.05),(.1,run+.003,.10),8)

def tree(b,n):
    cell=.075;wood=set()
    paths=[([(0,0,.08),(0,0,1.5),(.10,.05,2.6)],.30),([(0,0,1.2),(-.4,0,1.5),(-.95,0,2.1)],.15),([(0,0,1.4),(.5,0,1.9),(1.05,0,2.25)],.15),([(0,0,1.7),(-.3,.35,2.25)],.15)]
    for pts,width in paths:
        for start,end in zip(pts,pts[1:]):
            steps=max(1,math.ceil(math.dist(start,end)/.035))
            for i in range(steps+1):
                p=[round((start[k]+(end[k]-start[k])*i/steps)/cell) for k in range(3)]
                r=round(width/cell)//2
                for dx in range(-r,r+1):
                    for dy in range(-r,r+1):
                        for dz in range(-r,r+1):wood.add((p[0]+dx,p[1]+dy,max(0,p[2]+dz)))
    b.voxels('SteppedTrunk',wood,cell,8)
    # Read only literal crown definitions, never execute the destructive asset constructor.
    module=ast.parse((ROOT/'Scripts/BlenderRebuild/homestead_tree.py').read_text())
    columns=next(ast.literal_eval(node.value) for node in module.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='columns' for t in node.targets))
    columns += [(-.8,0,1.4,.35,.35,.32),(.88,.02,1.45,.28,.28,.33),(.9,.12,2,.4,.4,.38)]
    if n==1:
        for i,(u,v,z,w,d,h) in enumerate(columns):b.box('CoarseCrown',(u,v,z),(w,d,h),[5,6,5,7][i%4])
    else:
        leaf=.235/n;cells=set()
        for k,(u,v,z,w,d,h) in enumerate(columns):
            # Cluster lobes fill around original scaffold with notches, irregular stepped margins.
            rx=max(w*.60,.15);ry=max(d*.85,.19);rz=max(h*.62,.17)
            for ix in range(math.floor((u-rx)/leaf),math.ceil((u+rx)/leaf)):
                for iy in range(math.floor((v-ry)/leaf),math.ceil((v+ry)/leaf)):
                    for iz in range(math.floor((z-rz)/leaf),math.ceil((z+rz)/leaf)):
                        p=((ix+.5)*leaf,(iy+.5)*leaf,(iz+.5)*leaf)
                        norm=sum(((p[j]-[u,v,z][j])/[rx,ry,rz][j])**2 for j in range(3))
                        if norm<1.12 and not(norm>.76 and (ix*13+iy*7+iz*3+k)%11==0):cells.add((ix,iy,iz))
        b.voxels('FineCrownExterior',cells,leaf)

def fence(b,n):
    post=[.18,.12,.10][n-1];rail=[.13,.085,.065][n-1]
    for x in [-1.4+post/2,0,1.4-post/2]:
        b.box('Posts',(x,0,.62),(post,.20,1.24),8)
        b.box('PostCaps',(x,0,1.205),(post+.025,.22,.07),9)
    for z in [.38,.85]:
        for a,c in [(-1.36,-.025),(.025,1.36)]:b.box('Rails',((a+c)/2,-.06,z),(c-a,.095,rail),9)
    if n>1:
        for x in [-1.34,0,1.34]:
            for z in [.38,.85]:b.box('JoineryPins',(x,-.115,z),(.027,.019,.027),14)

def bridge(b,n):
    length=2.1;count=7*n;gap=.018/n
    for x in [-.47,.47]:b.box('Bearers',(x,0,.39),(.14,2.1,.18),8)
    for i in range(count):
        y=-length/2+(i+.5)*length/count
        b.box('DeckPlanks',(0,y,.565),(1.14,length/count-gap,.11),8+i%2)
        for x in [-.45,.45]:b.box('DeckPins',(x,y,.622),(.025,.045/n,.006),14)
    for x in [-.62,.62]:
        for y in [-.94,.94]:
            b.box('Posts',(x,y,.61),(.16,.18,1.22),8)
            b.box('PostCaps',(x,y,1.245),(.19,.21,.09),9)
            for z in [.25,1.03]:b.box('Bands',(x,y-.095,z),(.17,.016,.03),14)
        for z in [.9,1.14]:b.box('Rails',(x,0,z),(.082,1.98,.085),9)

def person(b):
    for x in [-.115,.115]:
        b.box('Feet',(x,-.04,.065),(.18,.31,.13),8);b.box('Legs',(x,0,.48),(.17,.19,.75),8)
    b.box('Torso',(0,0,1.14),(.45,.26,.55),15)
    for x in [-.30,.30]:b.box('Arms',(x,0,1.09),(.15,.2,.58),15)
    b.box('Head',(0,0,1.615),(.28,.28,.31),15)
    b.box('Hair',(0,0,1.755),(.30,.3,.09),8)

families=[('Cliff',cliff,(3,1.5,2.4)),('Cottage',cottage,(2.4,1.65,3.4)),('Tree',tree,(3.3,2.2,3.5)),('Fence',fence,(2.8,.22,1.24)),('Bridge',bridge,(1.42,2.1,1.29))]
builders=[];records=[]
for row,(family,fn,dim) in enumerate(families):
    for col,n in enumerate([1,2,3]):
        key=f'DC_{family}_{["Coarse","Half","Third"][col]}'
        b=Builder(key,(col*5.5,row*6,0));fn(b,n);b.finish(dim);builders.append(b)
        records.append({'name':key,'family':family,'variant':['Coarse','Half','Third'][col],'row':row,'column':col,'placement_m':list(b.offset),'dimensions_m':list(dim),'bounds_m':{'min':[-dim[0]/2,-dim[1]/2,0],'max':[dim[0]/2,dim[1]/2,dim[2]]},'parts':len(b.objects)})
p=Builder('DC_Person',(15,0,0));person(p);p.finish((.75,.31,1.8));builders.append(p)
records.append({'name':'DC_Person','family':'Person','variant':'Shared','row':0,'column':3,'placement_m':[15,0,0],'dimensions_m':[.75,.31,1.8],'bounds_m':{'min':[-.375,-.155,0],'max':[.375,.155,1.8]},'parts':len(p.objects)})

# Neutral studio, shared across every comparison.
world=bpy.data.worlds.new('DC_Studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.24,.22,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55;scene.world=world
ld=bpy.data.lights.new('DC_Key','SUN');ld.energy=2.3;ld.angle=.20;ob=bpy.data.objects.new('DC_Key',ld);scene.collection.objects.link(ob);ob.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-28))
cd=bpy.data.cameras.new('DC_Camera');camera=bpy.data.objects.new('DC_Camera',cd);scene.collection.objects.link(camera);cd.type='ORTHO';cd.ortho_scale=5;scene.camera=camera
camera.location=(6,-10,8);camera.rotation_euler=(Vector((0,0,1.6))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for b,r in zip(builders,records):
    vs=[];fs=[];mis=[]
    for o in b.objects:
        shift=len(vs);vs.extend(tuple(v.co) for v in o.data.vertices)
        for f in o.data.polygons:fs.append(tuple(i+shift for i in f.vertices));mis.append(f.material_index)
    name='SM_'+b.key;me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    for m in mats:me.materials.append(m)
    for f,i in zip(me.polygons,mis):f.material_index=i
    me.calc_loop_triangles();r['triangles']=len(me.loop_triangles);r['vertices']=len(me.vertices)
    r['material_slots']=[m.name for m in mats];r['fbx']=str(OUT/(name+'.fbx'))
    export=bpy.data.objects.new(name,me);scene.collection.objects.link(export)
    for o in scene.objects:o.select_set(False)
    export.select_set(True);bpy.context.view_layer.objects.active=export
    bpy.ops.export_scene.fbx(filepath=r['fbx'],use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE',path_mode='AUTO')
    bpy.data.objects.remove(export,do_unlink=True)
manifest={'scene':scene.name,'dimension_status':'provisional; same family envelopes exactly fixed','units':'metres in Blender; FBX UnitScaleFactor=100 centimetres per source unit','import_scale':1,'palette':[{'slot':i,'name':m.name,'linear_rgba':list(m.diffuse_color),'roughness':.88} for i,m in enumerate(mats)],'specimens':records,'scope_note':'Source-informed coarse construction sections, not byte-identical copies of canonical models. Tree crown positions read from existing recipe. No texture detail has been added.'}
(DOC/'manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.data.libraries.write(str(OUT/'DetailCalibration.library.blend'),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
bpy.context.window.scene=old_scene
result={'scene':scene.name,'specimens':len(records),'triangles':sum(r['triangles'] for r in records),'library':str(OUT/'DetailCalibration.library.blend'),'original_scene_restored':old_scene.name,'manifest':str(DOC/'manifest.json')}
