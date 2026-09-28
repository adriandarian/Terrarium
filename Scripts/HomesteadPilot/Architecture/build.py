"""Human-scale architectural pilot. New scene only; source textures remain byte-identical."""
import bpy,math,random,json,shutil,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium');OUT=ROOT/'SourceAssets/Blender/HomesteadPilot/Architecture';DOC=ROOT/'Docs/HomesteadPilot/Architecture'
assert Path(bpy.context.scene.get('terrarium_project',''))==ROOT
assert 'Terrarium_HomesteadArchitecture' not in bpy.data.scenes
prior=bpy.context.window.scene;s=bpy.data.scenes.new('Terrarium_HomesteadArchitecture');bpy.context.window.scene=s
s['terrarium_project']=str(ROOT);s['asset_scope']='Complete cottage, modular fence and bridge; exploration art pilot';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
specs=[('Roof','cottage_roof_tile_v6_candidate.png','bd6732',.87),('Wood','terrain_wood_3d.png','795226',.88),('Plaster','cottage_plaster_v5.png','e5d6af',.93),('Stone','terrain_cliff_face_v7.png','888574',.92),('Teal',None,'236e67',.75),('Iron',None,'454b43',.62),('Moss',None,'68792e',.95),('Brass',None,'c99a3d',.48)]
mats=[];materials=[]
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for name,source,h,rough in specs:
    m=bpy.data.materials.new('M_HP_'+name);m.use_nodes=True;color=[lin(int(h[i:i+2],16)/255) for i in [0,2,4]]+[1];m.diffuse_color=color
    bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=rough
    path=None
    if source:
        path=OUT/('T_HP_'+name+'_BaseColor.png');shutil.copyfile(ROOT/'SourceAssets/Voxel'/source,path)
        image=bpy.data.images.load(str(path),check_existing=False);image.name='T_HP_'+name+'_BaseColor';image.pack()
        tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=image;tx.interpolation='Linear';m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
    materials.append({'name':m.name,'base_color_linear':color,'base_color_texture':str(path) if path else None,'roughness':rough,'source':source,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path else None,'uv_notes':'Explicit tile/wood/stone surface crop per modeled component; plaster uses 2m repeat scale. Base-color sRGB; linear filtering and mipmaps, no global pixelation.'})
    mats.append(m)

class Asset:
    def __init__(self,name,lod):
        self.name=name;self.lod=lod;self.parts={};self.rng=random.Random(842+lod)
        self.col=bpy.data.collections.new(f'HP_{name}_LOD{lod}');s.collection.children.link(self.col);self.objects=[]
    def mesh(self,part,vs,fs,mat,uv=None):
        v,f,mi,uvs=self.parts.setdefault(part,([],[],[],[]));off=len(v);v.extend(vs)
        if uv is None:
            if mat==0:
                j=self.rng.choice([1,2,3,4]);k=self.rng.choice([1,2,3,4]);rect=(j/6+.012,k/6+.012,1/6-.025,1/6-.025)
            elif mat==1:rect=self.rng.choice([(.20,.93,.23,.045),(.62,.93,.25,.045),(.22,.935,.20,.04)])
            elif mat==3:rect=self.rng.choice([(.195,.835,.15,.11),(.58,.64,.16,.14),(.33,.335,.14,.11)])
            else:rect=(0,0,1,1)
        for face in fs:
            f.append(tuple(off+i for i in face));mi.append(mat)
            coords=[]
            p0,p1,p2=[Vector(vs[j]) for j in face[:3]];normal=(p1-p0).cross(p2-p0);axis=max(range(3),key=lambda k:abs(normal[k]));axes=[i for i in range(3) if i!=axis]
            if mat==1:axes.sort(key=lambda i:max(vs[j][i] for j in face)-min(vs[j][i] for j in face),reverse=True)
            lo=[min(vs[j][i] for j in face) for i in axes];hi=[max(vs[j][i] for j in face) for i in axes]
            for j in face:
                if mat==2:coords.append(tuple(vs[j][i]/2 for i in axes))
                else:coords.append(tuple(rect[k]+(vs[j][axes[k]]-lo[k])/max(.000001,hi[k]-lo[k])*rect[k+2] for k in [0,1]))
            uvs.append(coords)
    def box(self,part,p,size,mat,angle=0,bevel=0):
        x,y,z=p;w,d,h=size;a=math.cos(angle);b=math.sin(angle)
        if bevel>0:
            c=min(bevel,w*.2,d*.2);outline=[(-w/2+c,-d/2),(w/2-c,-d/2),(w/2,-d/2+c),(w/2,d/2-c),(w/2-c,d/2),(-w/2+c,d/2),(-w/2,d/2-c),(-w/2,-d/2+c)]
            vs=[(x+u*a-v*b,y+u*b+v*a,z+dz) for dz in [-h/2,h/2] for u,v in outline];fs=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
        else:
            vs=[(x+u*w/2*a-v*d/2*b,y+u*w/2*b+v*d/2*a,z+q*h/2) for u,v,q in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
            fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        self.mesh(part,vs,fs,mat)
    def beam(self,part,p,q,width,depth,mat=1):
        # Rectangular beam whose long axis follows the 3D segment; UV grain follows length.
        delta=Vector(q)-Vector(p);length=delta.length;rot=delta.to_track_quat('Z','Y').to_matrix();mid=(Vector(p)+Vector(q))/2
        vs=[tuple(mid+rot@Vector((x*width/2,y*depth/2,z*length/2))) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        self.mesh(part,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
    def finish(self):
        import bmesh
        for part,(v,f,mi,uvs) in self.parts.items():
            me=bpy.data.meshes.new(f'{self.name}_{part}_LOD{self.lod}');me.from_pydata(v,[],f);me.update()
            for m in mats:me.materials.append(m)
            layer=me.uv_layers.new(name='UVMap')
            for poly,idx,coords in zip(me.polygons,mi,uvs):
                poly.material_index=idx
                for li,co in zip(poly.loop_indices,coords):layer.data[li].uv=co
            bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.update()
            ob=bpy.data.objects.new(me.name,me);self.col.objects.link(ob);ob['part']=part;ob['asset']=self.name;ob['lod']=self.lod;self.objects.append(ob)
        return self
    def export(self):
        vs=[];fs=[];mis=[];uvs=[]
        for ob in self.objects:
            shift=len(vs);vs.extend(tuple(v.co) for v in ob.data.vertices)
            for p in ob.data.polygons:fs.append(tuple(i+shift for i in p.vertices));mis.append(p.material_index);uvs.append([tuple(ob.data.uv_layers.active.data[i].uv) for i in p.loop_indices])
        name=f'SM_HP_{self.name}_LOD{self.lod}';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();layer=me.uv_layers.new(name='UVMap')
        for m in mats:me.materials.append(m)
        for p,m,coords in zip(me.polygons,mis,uvs):
            p.material_index=m
            for li,co in zip(p.loop_indices,coords):layer.data[li].uv=co
        ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob)
        for q in s.objects:q.select_set(False)
        ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.view_layer.update()
        path=OUT/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE',path_mode='AUTO')
        me.calc_loop_triangles();lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
        report={'level':self.lod,'fbx':str(path),'triangles':len(me.loop_triangles),'vertices':len(vs),'bounds_m':{'min':lo,'max':hi},'dimensions_m':[hi[i]-lo[i] for i in range(3)],'parts':len(self.objects),'material_slots':[m.name for m in mats]}
        bpy.data.objects.remove(ob,do_unlink=True);self.col.hide_render=self.lod>0
        return report

def masonry(a,center,size,part='Foundation',cell=.28):
    x,y,z=center;w,d,h=size;rows=max(1,round(h/.17));cols=max(1,round(w/cell))
    for r in range(rows):
        edges=[-w/2]+[q for i in range(cols+1) if -w/2<(q:=-w/2+(i+(.5 if r%2 else 0))*w/cols)<w/2]+[w/2]
        for l,t in zip(edges,edges[1:]):a.box(part,(x+(l+t)/2,y,z-h/2+(r+.5)*h/rows),(t-l-.007,d,h/rows-.006),3,bevel=.012 if a.lod==0 else 0)

def window(a,x,y,z,width=.8,side=False):
    # Frames are offset forward from solid panes, so no z fighting.
    def B(part,p,d,mat):
        if side:p=(y+(1 if y>0 else -1)*(y-p[1]),p[0],p[2]);d=(d[1],d[0],d[2])
        elif y>0:p=(p[0],y+(y-p[1]),p[2])
        a.box(part,p,d,mat,bevel=.006 if a.lod==0 else 0)
    B('TealWindow',(x,y,z),(width,.07,1.05),4)
    for dx in [-width/2-.04,width/2+.04]:B('WindowTrim',(x+dx,y-.07,z),(.105,.16,1.20),1)
    for dz in [-.60,.60]:B('WindowTrim',(x,y-.08,z+dz),(width+.20,.18,.11),1)
    B('WindowSill',(x,y-.18,z-.64),(width+.30,.38,.105),1)
    B('TealMullion',(x,y-.10,z),(.055,.10,1.08),4);B('TealMullion',(x,y-.105,z),(width,.10,.055),4)
    if a.lod<2:
        for dx in [-width/2-.19,width/2+.19]:B('Shutter',(x+dx,y-.04,z),(.20,.09,1.12),4)
        for dx in [-.19,.19]:
            for dz in [-.25,.25]:B('GlassFacet',(x+dx,y-.047,z+dz),(.22,.004,.32),4)

def cottage(a):
    # Open shell: 5m x4.4m main footprint. Floor top=.24; doorway is clear x ±.65.
    a.box('FloorSubstrate',(0,0,.095),(5,4.4,.19),3)
    count=[28,18,10][a.lod]
    for j in range(count):
        x=-2.34+(j+.5)*4.68/count
        for k in range(4):a.box('Floorboards',(x,-1.98+(k+.5)*3.96/4,.2175),(4.68/count-.003,.988,.045),1)
    # Door opening remains free from Z=.24 through2.46, with frame narrowing to1.28m.
    for side in [-1,1]:a.box('FrontPlaster',(side*1.65,-2.10,1.52),(1.70,.22,2.56),2)
    a.box('DoorOverwall',(0,-2.10,2.65),(1.60,.22,.30),2)
    a.box('BackPlaster',(0,2.10,1.52),(4.78,.22,2.56),2)
    for side in [-1,1]:a.box('SidePlaster',(side*2.39,0,1.52),(.22,4.2,2.56),2)
    for side in [-1,1]:
        masonry(a,(side*1.64,-2.245,.31),(1.73,.16,.30),cell=.30 if a.lod==0 else .50)
        for y in [-2.09,0,2.09]:a.box('TimberPosts',(side*2.42,y,1.58),(.19,.24,2.76),1,bevel=.012 if a.lod==0 else 0)
        a.box('EaveRing',(side*2.45,0,2.84),(.20,4.72,.20),1)
        a.box('WallFootBeam',(side*2.48,0,.46),(.16,4.40,.16),1)
        for y in [-.95,1.00]:window(a,y,side*2.51,1.75,.76,side=True)
    for y in [-2.18,2.18]:
        a.box('EaveRing',(0,y,2.84),(5.06,.22,.20),1)
        if y>0:
            masonry(a,(0,y+.1,.31),(5.08,.16,.3),cell=.30 if a.lod==0 else .50);window(a,0,y+.17,1.75,.85)
    for x in [-1.57,1.57]:window(a,x,-2.28,1.73,.81)
    for x in [-.735,.735]:a.box('DoorJamb',(x,-2.22,1.39),(.19,.28,2.30),1,bevel=.008 if a.lod==0 else 0)
    a.box('DoorLintel',(0,-2.23,2.52),(1.66,.30,.20),1)
    a.box('Threshold',(0,-2.26,.22),(1.29,.42,.04),3)
    # Open oak door folded against the inside front wall on its left hinge.
    angle=math.radians(105);hinge=Vector((-.64,-2.10,0));dw=1.18
    for i in range([7,5,3][a.lod]):
        width=dw/[7,5,3][a.lod];local=Vector(((i+.5)*width,0,0));p=hinge+Vector((local.x*math.cos(angle),local.x*math.sin(angle),1.29))
        a.box('OpenDoor',tuple(p),(width-.004,.08,2.08),1,angle,bevel=.005 if a.lod==0 else 0)
    for z in [.55,2.02]:
        p=hinge+Vector((dw*.5*math.cos(angle),dw*.5*math.sin(angle),z));a.box('DoorStrap',tuple(p),(dw-.1,.095,.075),5,angle)
    p=hinge+Vector((dw*.86*math.cos(angle),dw*.86*math.sin(angle),1.35));a.box('DoorHandle',tuple(p),(.075,.12,.12),7,angle)
    # Two broad12cm treads from the exterior ground into a24cm-high floor.
    for y,top,depth in [(-2.45,.24,.38),(-2.84,.12,.40)]:masonry(a,(0,y,top/2),(1.65,depth,top),'EntrySteps',.40)
    # Four side gable infill slabs beneath the actual stepped roof.
    n=[18,12,8][a.lod];run=2.45/n
    for iy in range(2*n):
        y=-2.45+(iy+.5)*run;roof=2.98+1.62*(1-abs(y)/2.45);height=max(.01,roof-2.80)
        for x in [-2.37,2.37]:a.box('GableInfill',(x,y,2.8+height/2),(.20,run+.001,height),2)
    # Continuous thin sloping under-roof shells close the interior without a solid cube.
    for sign in [-1,1]:
        verts=[(-2.67,sign*2.47,2.91),(2.67,sign*2.47,2.91),(2.67,0,4.56),(-2.67,0,4.56)]
        verts+= [(x,y,z-.045) for x,y,z in verts]
        faces=[(0,1,2,3),(7,6,5,4)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
        # Correct each thin closed prism normal consistently after creation.
        if sign<0:faces=[tuple(reversed(f)) for f in faces]
        a.mesh('RoofUnderside',verts,faces,1)
    cols=[30,21,13][a.lod];step=5.54/cols
    for row in range(2*n):
        y=-2.45+(row+.5)*run;main=2.98+1.62*(1-abs(y)/2.45)
        for col in range(cols):
            x=-2.77+(col+.5)*step;cross=2.97+1.00*max(0,1-abs(x)/1.16) if y<-.60 else 0
            top=max(main,cross);variation=(.012*math.sin(col*5.7+row*1.7)) if a.lod==0 else 0
            a.box('RoofTiles',(x,y,top+variation), (step-.007,run+.025,.095),0,bevel=.012 if a.lod==0 else 0)
            if cross>main+.03 and row>0:a.box('CrossGableRiser',(x,y,(cross+main)/2-.02),(step-.007,run+.012,cross-main),0)
            if row==0:a.box('FrontSteppedFascia',(x,y-.025,top-.13),(step+.001,.17,.20),1)
            if col in [0,cols-1]:a.box('SideSteppedFascia',(x,y,top-.12),(.14,run+.005,.18),1)
            if cross>main+.03 and row==0:a.box('FrontCrossGableInfill',(x,y+.035,(cross+2.84)/2),(step+.003,.13,cross-2.84),2)
    for col in range(cols):
        x=-2.77+(col+.5)*step;a.box('RidgeCaps',(x,0,4.63),(step-.005,.22,.16),0,bevel=.01 if a.lod==0 else 0)
    a.box('GableUpright',(0,-2.53,3.36),(.14,.14,.98),1)
    # Exposed interior ridge, transverse ties and sloping rafters.
    a.box('InteriorRidge',(0,0,4.30),(4.8,.18,.22),1)
    for x in [-1.8,0,1.8]:
        a.box('InteriorTie',(x,0,2.80),(.16,4.18,.18),1)
        for sign in [-1,1]:a.beam('Rafters',(x,sign*2.08,2.78),(x,0,4.38),.13,.15)
    # Pale masonry chimney, open crown, and interior hearth below.
    cx=-1.70;cy=.75
    for z in [3.83,4.02,4.21,4.40,4.59,4.78,4.97,5.16]:
        masonry(a,(cx,cy-.31,z),(.69,.16,.18),'Chimney',.23)
        masonry(a,(cx,cy+.31,z),(.69,.16,.18),'Chimney',.23)
        for side in [-1,1]:a.box('Chimney',(cx+side*.29,cy,z),(.16,.50,.18),3,bevel=.008 if a.lod==0 else 0)
    for x,y,w,d in [(cx-.35,cy,.16,.88),(cx+.35,cy,.16,.88),(cx,cy-.35,.54,.16),(cx,cy+.35,.54,.16)]:a.box('ChimneyRim',(x,y,5.31),(w,d,.17),3)
    a.box('Hearth',(0,1.67,.33),(1.45,.74,.18),3)
    for x in [-.58,.58]:a.box('HearthJamb',(x,1.88,.86),(.20,.35,1.10),3)
    a.box('HearthMantel',(0,1.83,1.44),(1.6,.49,.17),1)
    a.box('HearthShadow',(0,1.99,.85),(.9,.10,.92),5)
    # Wall shelf and bench avoid the central route.
    a.box('Shelf',(-1.89,.95,1.46),(.57,1.12,.10),1)
    for y in [.5,1.35]:a.box('ShelfBracket',(-1.98,y,1.27),(.30,.09,.34),1)
    a.box('Bench',(1.72,.70,.67),(.65,1.44,.13),1)
    for y in [.15,1.25]:a.box('BenchLeg',(1.72,y,.435),(.46,.14,.39),1)
    if a.lod<2:
        # Small geometry wear/ivy groups, deliberately sparse and away from doorway.
        for side in [-1,1]:
            for k in range(22 if a.lod==0 else 9):
                x=side*(2.38+.13*math.sin(k*1.7));y=-2.05+.10*(k%8);z=.42+.07*(k//8)
                a.box('MossFooting',(x,y,z),(.14,.17,.10),6)
        for x in [-1.57,1.57]:
            a.box('WindowPlanter',(x,-2.59,1.09),(1.05,.28,.19),1)
            for j in range(7):a.box('PlanterLeaves',(x-.43+j*.14,-2.59,1.24+.04*(j%3)),(.13,.17,.12),6)

def fence(a):
    for x in [-1.41,0,1.41]:
        a.box('Posts',(x,0,.60),(.18,.20,1.20),1,bevel=.014 if a.lod==0 else 0)
        a.box('PostCap',(x,0,1.21),(.21,.23,.10),1,bevel=.025 if a.lod==0 else 0)
    for z in [.40,.86]:
        for x in [-.705,.705]:a.box('Rails',(x,-.025,z),(1.43,.12,.115),1,bevel=.008 if a.lod==0 else 0)
    if a.lod<2:
        for x in [-1.41,0,1.41]:
            for z in [.40,.86]:a.box('IronPins',(x,-.093,z),(.029,.025,.029),5)
        for x in [-1.4,1.4]:a.box('MossAtFoot',(x,0,.035),(.22,.24,.07),6)

def bridge(a):
    # Tileable3.6m bridge module: deck top .32m, centered ground-base pivot.
    for x in [-.87,.87]:a.box('Bearers',(x,0,.155),(.18,3.6,.25),1,bevel=.015 if a.lod==0 else 0)
    count=[24,16,10][a.lod]
    for j in range(count):
        y=-1.8+(j+.5)*3.6/count
        a.box('Deck',(0,y,.275),(2.04,3.6/count-.012,.09),1,bevel=.008 if a.lod==0 else 0)
        if a.lod==0:
            for x in [-.84,.84]:a.box('DeckPins',(x,y+.02,.323),(.025,.046,.008),5)
    for x in [-1.14,1.14]:
        for y in [-1.70,0,1.70]:
            a.box('Posts',(x,y,.64),(.18,.19,1.28),1,bevel=.012 if a.lod==0 else 0)
            a.box('PostCap',(x,y,1.29),(.23,.24,.10),1,bevel=.025 if a.lod==0 else 0)
            if a.lod<2:
                for z in [.31,1.10]:
                    for sign in [-1,1]:a.box('IronBands',(x,y+sign*.102,z),(.195,.015,.043),5)
        for y in [-.85,.85]:
            for z in [.75,1.16]:a.box('Rails',(x,y,z),(.11,1.73,.10),1,bevel=.009 if a.lod==0 else 0)
    for y in [-1.70,0,1.70]:a.box('Crossbearers',(0,y,.11),(2.42,.18,.22),1)

assets=[]
for name,fn in [('Cottage',cottage),('Fence',fence),('Bridge',bridge)]:
    lods=[]
    for level in range(3):
        a=Asset(name,level);fn(a);a.finish();lods.append(a.export())
    rec={'name':name,'fbx':lods[0]['fbx'],'lods':lods,'bounds_m':lods[0]['bounds_m'],'dimensions_m':lods[0]['dimensions_m'],'material_slots':[m.name for m in mats],'collision_notes':'Use complex-as-simple for static cottage, or author separate wall/floor collision pieces. A single convex hull will seal the doorway. Fence/bridge rails must not seal the clear route.'}
    if name=='Cottage':rec['traversal']={'floor_top_m':.24,'door_clear_width_m':1.28,'door_clear_height_m':2.18,'door_front_y_m':-2.22,'entry_step_rise_m':.12,'interior_clear_footprint_m':[4.56,3.96],'door_open_degrees':105,'central_route_x_m':[-.5,.5]}
    if name=='Bridge':rec['traversal']={'deck_top_m':.32,'clear_width_m':2.04,'module_length_m':3.6,'deck_end_y_m':[-1.8,1.8],'rail_top_m':1.21,'placement_note':'Ground-base pivot; to join a path at elevation H, place actor Z=H-32cm. Supports need terrain or dedicated piles below them.'}
    assets.append(rec)
manifest={'source_blend':str(OUT/'HomesteadArchitecture.blend'),'coordinates':{'units':'metres','up':'Z','front':'-Y','pivot':'base center, Z=0','fbx_import_scale':1},'assets':assets,'materials':materials,'lod_method':'Authored feature count reduction, no blanket decimation. Preserve doorway and traversal dimensions; fine trim drops only atdistance. Screen thresholds and runtime tests belong to Unreal integration.','source_references':['Docs/CalibrationIntegration/References/settlement-growth-stage-'+str(i)+'-'+name+'.png' for i,name in [(1,'homestead'),(2,'village'),(3,'town'),(4,'city')]]}
(DOC/'manifest.json').write_text(json.dumps(manifest,indent=2))
world=bpy.data.worlds.new('HP_Studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.28,.25,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;s.world=world
for name,pos,power,size,col in [('Key',(-5,-7,10),1700,5,(1,.86,.69)),('Fill',(6,-2,6),1100,5,(.81,.90,1)),('Rim',(0,5,9),1400,4,(1,.96,.84))]:
    d=bpy.data.lights.new('HP_'+name,'AREA');d.energy=power;d.size=size;d.color=col;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('HP_Review');cam=bpy.data.objects.new('HP_Review',cd);s.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=8.0;cam.location=(-8,-12,9);cam.rotation_euler=(Vector((0,0,2.2))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
for c in s.collection.children:c.hide_render=c.name!='HP_Cottage_LOD0'
bpy.data.libraries.write(str(OUT/'Architecture.library.blend'),{s},path_remap='RELATIVE',fake_user=True,compress=True)
bpy.context.window.scene=prior
result={'manifest':str(DOC/'manifest.json'),'assets':[{r['name']:[l['triangles'] for l in r['lods']]} for r in assets],'scene_restored':prior.name,'library_saved':True}
