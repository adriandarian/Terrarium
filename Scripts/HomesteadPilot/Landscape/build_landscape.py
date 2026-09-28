"""Author/export the landscape pilot in the verified Terrarium Blender session.

Only newly named pilot scenes are changed. Existing asset sources are untouched.
Run with exec(compile(open(__file__).read(), __file__, 'exec')) through Blender MCP.
"""
import bpy,bmesh,math,random,json,sys,subprocess,hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path('C:/Users/hello/Projects/Terrarium')
assert Path(bpy.context.scene.get('terrarium_project','')).resolve()==ROOT.resolve()
OUT=ROOT/'SourceAssets/Blender/HomesteadPilot/Landscape'
DOC=ROOT/'Docs/HomesteadPilot/Landscape'
OUT.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
TEX=OUT/'Textures';TEX.mkdir(exist_ok=True)
R=random.Random(4708)
PALETTE={
 'Stone':('827b60','mineral'),'StoneLight':('999075','mineral'),
 'StoneShade':('69654f','mineral'),'Moss':('66713d','moss'),
 'Grass':('77804b','grass'),'Path':('ac9368','earth'),
 'Bark':('655039','wood'),'Leaf':('697742','leaf'),
 'LeafLight':('82904e','leaf'),'LeafShade':('475932','leaf'),
 'Wheat':('b7a05b','stalk'),'Soil':('655540','earth'),
 'Crop':('607948','leaf')}
MATERIALS={};TEXTURES={}


def texture_material(name,color,kind):
    size=512;rgb=[int(color[i:i+2],16)/255 for i in (0,2,4)]
    image=bpy.data.images.new('PilotLandscape_'+name,width=size,height=size,alpha=False)
    pixels=[]
    for y in range(size):
        for x in range(size):
            # Tileable broad stains plus fine marks, deliberately no screen pixels.
            u=x/size;v=y/size
            broad=tile_noise(u,v,7);grain=tile_noise(u,v,29)
            fine=tile_noise(u,v,71)
            f=1+.17*broad+.095*grain+.045*fine
            if kind=='wood':f+=.10*math.sin(2*math.pi*u*23+math.sin(2*math.pi*v*2))
            if kind=='leaf':f+=.055*math.sin(math.floor(u*34)*7+math.floor(v*34)*11)
            if kind=='mineral':f+=.07*math.sin(math.floor(u*15)*13+math.floor(v*13)*9)
            if kind=='stalk':f+=.08*math.sin(2*math.pi*u*31)
            pixels.extend([max(0,min(1,c*f)) for c in rgb]+[1])
    image.pixels.foreach_set(pixels);image.file_format='PNG'
    image.filepath_raw=str(TEX/(name+'_BaseColor.png'));image.save();image.pack()
    mat=bpy.data.materials.new('M_PilotLandscape_'+name);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.92
    bs.inputs['Specular IOR Level'].default_value=.18
    tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=image;tx.extension='REPEAT';tx.interpolation='Linear'
    mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
    MATERIALS[name]=mat;TEXTURES[name]=str(Path(image.filepath_raw).relative_to(ROOT)).replace('\\','/')
def tile_noise(u,v,n):
    x,y=u*n,v*n;ix,iy=math.floor(x),math.floor(y);a,b=x-ix,y-iy
    a=a*a*(3-2*a);b=b*b*(3-2*b)
    def h(i,j):
        value=((i%n)*73856093)^((j%n)*19349663)^83492791
        value=(value^(value>>13))*1274126177
        return (value&65535)/65535-.5
    return (h(ix,iy)*(1-a)+h(ix+1,iy)*a)*(1-b)+(h(ix,iy+1)*(1-a)+h(ix+1,iy+1)*a)*b
for name,(color,kind) in PALETTE.items():texture_material(name,color,kind)


class Mesh:
    def __init__(self,name):self.name=name;self.v=[];self.f=[];self.mi=[];self.parts=0
    def solid(self,vs,fs,mat):
        start=len(self.v);self.v.extend(vs);self.f.extend(tuple(start+i for i in f) for f in fs)
        self.mi.extend([mat]*len(fs));self.parts+=1
    def box(self,c,s,mat,bevel=.008):
        # 24-vertex corner chamfer, avoiding Blender modifier/object overhead.
        h=[x/2 for x in s];b=min(bevel,min(h)*.3);vs=[];ix={}
        if b<1e-6:
            vs=[(c[0]+x*h[0],c[1]+y*h[1],c[2]+z*h[2]) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
            self.solid(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat);return
        for axis in range(3):
            for sx in (-1,1):
                for sy in (-1,1):
                    for sz in (-1,1):
                        signs=(sx,sy,sz);ix[axis,signs]=len(vs)
                        vs.append(tuple(c[j]+signs[j]*(h[j] if j==axis else h[j]-b) for j in range(3)))
        fs=[]
        for axis in range(3):
            other=[j for j in range(3) if j!=axis]
            for sign in (-1,1):
                f=[]
                for a,d in [(-1,-1),(1,-1),(1,1),(-1,1)]:
                    q=[0,0,0];q[axis]=sign;q[other[0]]=a;q[other[1]]=d;f.append(ix[axis,tuple(q)])
                fs.append(f)
        for a,d in [(0,1),(0,2),(1,2)]:
            other=3-a-d
            for sa in (-1,1):
                for sd in (-1,1):
                    p=[0,0,0];p[a]=sa;p[d]=sd;p[other]=-1;q=p.copy();q[other]=1
                    fs.append([ix[a,tuple(p)],ix[a,tuple(q)],ix[d,tuple(q)],ix[d,tuple(p)]])
        for sx in (-1,1):
            for sy in (-1,1):
                for sz in (-1,1):fs.append([ix[a,(sx,sy,sz)] for a in range(3)])
        self.solid(vs,fs,mat)
    def beam(self,a,b,r,mat,sides=7):
        av,bv=Vector(a),Vector(b);axis=(bv-av).normalized();right=axis.cross(Vector((0,0,1)))
        if right.length<.01:right=Vector((1,0,0))
        right.normalize();up=axis.cross(right).normalized();vs=[]
        for p,mult in [(av,1),(bv,.72)]:
            for j in range(sides):
                t=j*2*math.pi/sides;vs.append(tuple(p+(right*math.cos(t)+up*math.sin(t))*r*mult))
        fs=[tuple(reversed(range(sides))),tuple(range(sides,sides*2))]
        fs.extend((j,(j+1)%sides,(j+1)%sides+sides,j+sides) for j in range(sides))
        self.solid(vs,fs,mat)
    def voxel_crown(self,lobes,cell,mats):
        vox=set()
        for cx,cy,cz,rx,ry,rz in lobes:
            for x in range(math.floor((cx-rx)/cell),math.ceil((cx+rx)/cell)):
                for y in range(math.floor((cy-ry)/cell),math.ceil((cy+ry)/cell)):
                    for z in range(math.floor((cz-rz)/cell),math.ceil((cz+rz)/cell)):
                        u,v,w=(x+.5)*cell,(y+.5)*cell,(z+.5)*cell
                        if ((u-cx)/rx)**2+((v-cy)/ry)**2+((w-cz)/rz)**2<1:
                            vox.add((x,y,z))
        # Join diagonal edge contacts with one tiny cell so the exterior is
        # manifold for subsequent LOD processing, not four faces on one edge.
        for repair in range(3):
            additions=set()
            for p in vox:
                for a,b in ((0,1),(0,2),(1,2)):
                    for sa in (-1,1):
                        for sb in (-1,1):
                            q=list(p);q[a]+=sa;q[b]+=sb
                            qa=list(p);qa[a]+=sa;qb=list(p);qb[b]+=sb
                            if tuple(q) in vox and tuple(qa) not in vox and tuple(qb) not in vox:
                                additions.add(tuple(qa))
            if not additions:break
            vox.update(additions)
        lookup={};faces=[];mi=[]
        dirs=[((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),((-1,0,0),[(0,1,0),(0,0,0),(0,0,1),(0,1,1)]),((0,1,0),[(1,1,0),(0,1,0),(0,1,1),(1,1,1)]),((0,-1,0),[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)]),((0,0,-1),[(0,1,0),(1,1,0),(1,0,0),(0,0,0)])]
        vs=[]
        for x,y,z in sorted(vox):
            for (dx,dy,dz),corners in dirs:
                if (x+dx,y+dy,z+dz) in vox:continue
                f=[]
                for a,b,c in corners:
                    key=(x+a,y+b,z+c)
                    if key not in lookup:lookup[key]=len(vs);vs.append(tuple(k*cell for k in key))
                    f.append(lookup[key])
                faces.append(f);mi.append(mats[(x*17+y*11+z*7+(2 if dz>0 else 0))%len(mats)])
        start=len(self.v);self.v.extend(vs);self.f.extend(tuple(start+i for i in f) for f in faces);self.mi.extend(mi);self.parts+=1


def cliff():
    m=Mesh('MossCliff4m');m.box((0,0,.94),(3.87,3.87,1.88),'StoneShade',.01)
    z=0;row=0
    while z<1.93:
        h=min(R.uniform(.18,.27),1.93-z)
        for side in range(4):
            p=-2
            while p<1.999:
                width=min(R.uniform(.24,.48),2-p)
                if width>.025:
                    v=p+width/2;out=1.944+R.uniform(-.022,.02)
                    pos=(v,out,z+h/2) if side==0 else ((out,v,z+h/2) if side==1 else ((v,-out,z+h/2) if side==2 else (-out,v,z+h/2)))
                    size=(width-.014,.11,h-.012) if side%2==0 else (.11,width-.014,h-.012)
                    m.box(pos,size,R.choice(['Stone','Stone','StoneLight','StoneShade']),.012)
                    if R.random()<.18 and z>1:
                        moss=list(pos);moss[2]+=h*.35;m.box(moss,(size[0],size[1]+.012,.045),'Moss',.007)
                p+=width
        z+=h;row+=1
    m.box((0,0,1.965),(4,4,.07),'Grass',.018)
    for i in range(70):
        x,y=R.uniform(-1.94,1.94),R.uniform(-1.94,1.94)
        m.box((x,y,2.005),(R.uniform(.04,.15),R.uniform(.04,.14),.018),R.choice(['Moss','Grass']),.004)
    return m


def tree():
    m=Mesh('BroadTree5m')
    trunk=[(0,0,.06),(-.06,.02,.75),(.01,.03,1.5),(.12,.02,2.25),(.03,.09,3.25)]
    for i,(a,b) in enumerate(zip(trunk,trunk[1:])):m.beam(a,b,.22-i*.027,'Bark',9)
    for j in range(7):
        t=j*math.tau/7;m.beam((0,0,.18),(.62*math.cos(t),.62*math.sin(t),.035),.12,'Bark')
    lobes=[]
    for j in range(9):
        t=j*math.tau/9;rad=1.15+R.uniform(-.15,.22);height=3.35+R.uniform(-.35,.25)
        end=(rad*math.cos(t),rad*math.sin(t),height)
        m.beam((0,0,1.7+j*.1),(.55*end[0],.55*end[1],height-.6),.11,'Bark')
        m.beam((.55*end[0],.55*end[1],height-.6),end,.075,'Bark')
        lobes.append((*end,R.uniform(.63,.82),R.uniform(.62,.8),R.uniform(.55,.75)))
    lobes += [(-.15,.1,4.15,.92,.89,.83),(.55,.3,4.1,.75,.70,.65),(-.7,-.05,4.0,.72,.78,.7),(0,-.65,3.83,.80,.65,.65)]
    m.voxel_crown(lobes,.115,['LeafShade','Leaf','Leaf','LeafLight','Leaf'])
    for j in range(26):
        t=R.random()*math.tau;z=R.uniform(.2,1.65)
        seg=min(2,int(z/.75));a,b=trunk[seg],trunk[seg+1]
        along=max(0,min(1,(z-a[2])/(b[2]-a[2])))
        cx=a[0]+along*(b[0]-a[0]);cy=a[1]+along*(b[1]-a[1])
        radius=(.22-seg*.027)*(1-.28*along)-.015
        m.box((cx+radius*math.cos(t),cy+radius*math.sin(t),z),(.025,.035,R.uniform(.09,.23)),'StoneShade',.003)
    for j in range(22):
        t=R.random()*math.tau;r=R.uniform(.2,.55)
        m.box((r*math.cos(t),r*math.sin(t),.025),(R.uniform(.08,.18),R.uniform(.07,.17),.05),'Moss',.005)
    return m


def cliff_column():
    m=Mesh('FineCliffColumn1m');m.box((0,0,1.565),(.90,.90,3.13),'StoneShade',0)
    z=0
    while z<3.13:
        h=min(R.uniform(.24,.32),3.13-z)
        for side in range(4):
            p=-.5
            while p<.499:
                width=min(R.uniform(.21,.36),.5-p)
                if width>.018:
                    v=p+width/2;out=.462+R.uniform(-.012,.007)
                    pos=(v,out,z+h/2) if side==0 else ((out,v,z+h/2) if side==1 else ((v,-out,z+h/2) if side==2 else (-out,v,z+h/2)))
                    size=(width-.009,.074,h-.012) if side%2==0 else (.074,width-.009,h-.012)
                    m.box(pos,size,R.choice(['Stone','Stone','StoneLight','StoneShade']),.004 if R.random()<.2 else 0)
                p+=width
        z+=h
    m.box((0,0,3.165),(1,1,.07),'Grass',.008)
    for j in range(12):
        x,y=R.uniform(-.45,.45),R.uniform(-.45,.45)
        m.box((x,y,3.202),(.07,.08,.015),R.choice(['Moss','Grass']),.002)
    return m


def shrub():
    m=Mesh('ShrubGroundcover')
    lobes=[(-.39,-.1,.30,.37,.36,.29),(.03,.1,.44,.43,.40,.4),(.4,.0,.3,.34,.38,.3),(.12,-.35,.20,.34,.29,.2)]
    m.voxel_crown(lobes,.065,['Leaf','LeafShade','Leaf','LeafLight'])
    for j in range(44):
        t=R.random()*math.tau;r=R.uniform(.47,.85);x,y=r*math.cos(t),r*math.sin(t)
        m.beam((x,y,0),(x+R.uniform(-.06,.06),y+R.uniform(-.06,.06),R.uniform(.08,.24)),.014,'Grass',4)
    return m


def path():
    m=Mesh('WornPath2m');m.box((0,0,.033),(2,2,.066),'Path',.018)
    for j in range(48):
        x,y=R.uniform(-.96,.96),R.uniform(-.98,.98)
        if abs(x)>.70 or R.random()<.2:
            m.box((x,y,.075),(R.uniform(.03,.11),R.uniform(.04,.15),R.uniform(.012,.035)),R.choice(['Stone','StoneLight','Path']),.006)
    return m


def stairs():
    m=Mesh('StoneStairs2mRise')
    for step in range(12):
        z=(step+1)/6;y=-1.8+(step+.5)*.30
        m.box((0,y,(z-.112)/2),(2,.30,z-.112),'StoneShade',.002)
        for j in range(7):
            x=-1+(j+.5)*2/7
            m.box((x,y,z-.055),(2/7-.01,.292,.11),R.choice(['Stone','StoneLight','Stone']),.007)
            if j in (0,6) and R.random()<.4:m.box((x,y-.03,z+.006),(.12,.13,.012),'Moss',.003)
    return m


def wheat():
    m=Mesh('WheatPatch2m');m.box((0,0,.018),(2,2,.036),'Soil',.012)
    for x in range(15):
        for y in range(15):
            px=-.92+x*.13+R.uniform(-.018,.018);py=-.92+y*.13+R.uniform(-.018,.018);h=R.uniform(.65,.90)
            m.beam((px,py,.035),(px+.035,py,h),.008,'Wheat',4)
            for k in range(3):m.box((px+.035,py,h-.07+k*.035),(.030,.026,.042),'Wheat',.003)
    return m


def garden():
    m=Mesh('GardenPatch2m');m.box((0,0,.025),(2,2,.05),'Soil',.012)
    for x in range(5):
        for y in range(5):
            px=-.76+x*.38;py=-.76+y*.38
            m.voxel_crown([(px,py,.135,.14,.14,.11),(px+.045,py,.19,.07,.07,.08)],.045,['Crop','LeafLight','Crop'])
    return m


def write_asset(recipe):
    m=recipe();key=m.name;folder=OUT/key;folder.mkdir(exist_ok=True)
    bottom=min(v[2] for v in m.v)
    m.v=[(x,y,z-bottom) for x,y,z in m.v]
    s=bpy.data.scenes.new('Terrarium_Pilot_'+key);bpy.context.window.scene=s
    s['terrarium_project']=str(ROOT);s['asset_name']=key;s['asset_purpose']='Homestead landscape art pilot'
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1.0
    me=bpy.data.meshes.new('SM_Pilot_'+key);me.from_pydata(m.v,[],m.f);me.update()
    used=list(dict.fromkeys(m.mi))
    for name in used:me.materials.append(MATERIALS[name])
    for p,mat in zip(me.polygons,m.mi):p.material_index=used.index(mat)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        dominant=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=dominant]
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(v[axes[0]],v[axes[1]]) # 512 texels/metre, repeating tile
    ob=bpy.data.objects.new(me.name,me);s.collection.objects.link(ob);ob['part']='Editable landscape mesh';ob['asset_key']=key
    me.calc_loop_triangles();bounds={'min':[min(v.co[i] for v in me.vertices) for i in range(3)],'max':[max(v.co[i] for v in me.vertices) for i in range(3)]}
    dims=[bounds['max'][i]-bounds['min'][i] for i in range(3)]
    for o in s.objects:o.select_set(False)
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    fbx=folder/(me.name+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},apply_unit_scale=True,
        axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='COPY')
    focus=Vector((0,0,dims[2]*.47));radius=max(dims)*1.8
    world=bpy.data.worlds.new(key+'_World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.20,.14,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45;s.world=world
    for name,pos,power,size in [('Key',(-radius,-radius,radius*1.5),1200,5),('Fill',(radius,-radius*.3,radius),650,5),('Rim',(0,radius,radius*1.2),900,4)]:
        dat=bpy.data.lights.new(key+name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size
        light=bpy.data.objects.new(key+name,dat);s.collection.objects.link(light);light.location=pos;light.rotation_euler=(focus-light.location).to_track_quat('-Z','Y').to_euler()
    dat=bpy.data.cameras.new(key+'_Camera');cam=bpy.data.objects.new(key+'_Camera',dat);s.collection.objects.link(cam)
    cam.location=(radius,-radius,radius*.95);cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler()
    dat.type='ORTHO';dat.ortho_scale=max(dims[2]*1.3,max(dims[:2])*1.75);s.camera=cam
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
    s.render.film_transparent=False;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
    s.render.image_settings.file_format='PNG';preview=DOC/(key+'.png');s.render.filepath=str(preview)
    bpy.ops.render.render(write_still=True)
    blend=folder/(key+'.blend');bpy.data.libraries.write(str(blend),{s},path_remap='RELATIVE',fake_user=True,compress=True)
    # Existing project convention packages an isolated scene into a normal file.
    package=ROOT/'Scripts/HomesteadPilot/Landscape/package_asset.py'
    proc=subprocess.run([bpy.app.binary_path,'--background','--factory-startup','--python-exit-code','1','--python',str(package),'--',str(blend),s.name],capture_output=True,text=True,timeout=120,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    assert proc.returncode==0,(proc.stdout[-2000:],proc.stderr[-2000:])
    report={'key':key,'name':key,'mesh_name':me.name,'bounds_m':bounds,'dimensions_m':dims,'origin':'base-center, Z-up, metres',
        'fbx':str(fbx.relative_to(ROOT)).replace('\\','/'),
        'fbx_path':str(fbx.relative_to(ROOT)).replace('\\','/'),'blend_path':str(blend.relative_to(ROOT)).replace('\\','/'),
        'preview_path':str(preview.relative_to(ROOT)).replace('\\','/'),'vertices':len(me.vertices),'triangles':len(me.loop_triangles),
        'material_slots':[{'slot':i,'name':MATERIALS[name].name,'color_hex':PALETTE[name][0],
            'base_color_texture':TEXTURES[name],'roughness':.92,'specular':.18,'texels_per_metre':512} for i,name in enumerate(used)],
        'lods':[{'level':0,'fbx':str(fbx.relative_to(ROOT)).replace('\\','/'),'triangles':len(me.loop_triangles)}],
        'collision_notes':'Use simple authored-envelope collision for terrain/path; ramp proxy on stair; trunk-only on tree; no collision on foliage/crops. Runtime integration owns collision creation.',
        'traversal':{'walkable_width_m':2.0 if key in ('WornPath2m','StoneStairs2mRise') else None,'stair_riser_m':1/6 if key=='StoneStairs2mRise' else None,'stair_tread_m':.30 if key=='StoneStairs2mRise' else None},
        'geometry':'Exterior-only voxel canopy surfaces; closed chamfered solids for stone and wood. No internal voxel faces.',
        'uv_mapping':'Dominant-axis world-unit UV, repeating 1m authored surface textures',
        'lod_status':'source LOD0 only; runtime LOD/traversal agent owns integration',
        'validation':'exported, render saved, packaged normal Blender project; Unreal appearance pending'}
    (folder/'manifest.json').write_text(json.dumps(report,indent=2));(DOC/(key+'.json')).write_text(json.dumps(report,indent=2))
    return report


results=[]
for recipe in [cliff,cliff_column,tree,shrub,path,stairs,wheat,garden]:
    results.append(write_asset(recipe))
    (DOC/'progress.json').write_text(json.dumps({'completed':[r['key'] for r in results],'count':len(results)},indent=2))
def linear_color(h):
    rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return [v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
manifest={'project':'Terrarium','purpose':'finished homestead landscape pilot candidates','assets':results,
    'materials':[{'name':MATERIALS[name].name,'base_color_linear':linear_color(PALETTE[name][0]),'base_color_texture':TEXTURES[name],'roughness':.92,'uv_notes':'Dominant-axis 512px/m; repeating 1m tile; linear filtering, no global pixelation'} for name in MATERIALS],
    'source_blend':[r['blend_path'] for r in results],'coordinates':{'unit':'metres','up_axis':'Z','origin':'base center','fbx_forward_axis':'-Y'},
    'reference_files':[str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'Docs/CalibrationIntegration/References').glob('*.png')],
    'visual_status':'previews authored; review required; no blanket fidelity approval'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));(DOC/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('TERRARIUM_LANDSCAPE_PILOT_COMPLETE '+str(len(results)))
