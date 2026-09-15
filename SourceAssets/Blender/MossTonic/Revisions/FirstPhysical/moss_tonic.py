"""Physical squared bottle from moss_tonic.png; unseen surfaces are inferred."""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path('C:/Users/hello/Projects/Terrarium')
sys.path.insert(0,str(ROOT/'Scripts/BlenderRebuild'))
from assetkit import Asset

PALETTE=[('126359','glass'),('218978','gloss'),('3da08c','gloss'),('70bd98','gloss'),
         ('a5d6a2','gloss'),('17a59d','gloss'),('103f39','gloss'),('236e5b','gloss'),
         ('e0a748','cork'),('c68a31','cork'),('ecb951','cork'),('f4d793','paper'),
         ('ffe5a9','paper'),('ddbc79','paper'),('88983d','leaf'),('a4ae50','leaf'),
         ('667d2d','leaf'),('c6c273','leaf'),('c29a4b','cord'),('dab363','cord'),('9bdac6','glass')]
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4

class Tonic(Asset):
    def make_material(self):
        images=[]
        for kind in ['BaseColor','Emission','Roughness']:
            im=bpy.data.images.new(self.key+'_'+kind,width=512,height=512,alpha=False,float_buffer=True)
            if kind=='Roughness':im.colorspace_settings.name='Non-Color'
            px=[]
            for y in range(512):
                for x in range(512):
                    idx=min(y//64*8+x//64,len(self.palette)-1);hx,typ=self.palette[idx]
                    rgb=[int(hx[i:i+2],16)/255 for i in (0,2,4)]
                    # Larger block pigment patches; no dark checkerboard grout baked into glass.
                    u=x%64;v=y%64
                    f=1+(.004 if typ in ['paper','cork','cord'] else (.10 if idx==0 else .016))*math.sin((u//8)*13.1+(v//8)*7.9+idx*2)
                    if kind=='BaseColor':rgb=[linear(min(1,c*f)) for c in rgb]
                    elif kind=='Emission':rgb=[0]*3
                    else:rgb=[{'glass':.07,'gloss':.22,'cork':.64,'paper':.72,'leaf':.45,'cord':.55}[typ]]*3
                    px.extend(rgb+[1])
            im.pixels.foreach_set(px);im.filepath_raw=str(self.out/(self.key+'_'+kind+'.png'));im.file_format='PNG';im.save();im.pack();images.append(im)
        self.material=bpy.data.materials.new('M_MossTonic_Trim');self.material.use_nodes=True
        bs=self.material.node_tree.nodes.get('Principled BSDF');bs.inputs['Specular IOR Level'].default_value=.4
        for im,pin in zip(images,['Base Color','Emission Color','Roughness']):
            tx=self.material.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im
            self.material.node_tree.links.new(tx.outputs['Color'],bs.inputs[pin])
        self.glass=self.material.copy();self.glass.name='M_MossTonic_Glass'
        bs=self.glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.82;bs.inputs['IOR'].default_value=1.46
        self.liquid=self.material.copy();self.liquid.name='M_MossTonic_Liquid'
        bs=self.liquid.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.08;bs.inputs['IOR'].default_value=1.33

    def solid(self,label,verts,faces,index,material=None,bevel=.002):
        me=bpy.data.meshes.new(label);me.from_pydata(verts,[],faces);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        me.materials.append(material or self.material)
        uv=me.uv_layers.new(name='UVMap')
        for p in me.polygons:
            ax=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=ax]
            coords=[me.vertices[me.loops[li].vertex_index].co for li in p.loop_indices]
            lo=[min(v[a] for v in coords) for a in axes];hi=[max(v[a] for v in coords) for a in axes]
            for li,v in zip(p.loop_indices,coords):
                uv.data[li].uv=tuple((index%8 if j==0 else index//8)/8+.006+.113*(v[a]-lo[j])/max(hi[j]-lo[j],1e-6) for j,a in enumerate(axes))
        ob=bpy.data.objects.new(label,me);self.scene.collection.objects.link(ob);ob['part']=label;self.parts.append(ob)
        if bevel:
            md=ob.modifiers.new('Soft manufactured edges','BEVEL');md.width=bevel;md.segments=2
            md=ob.modifiers.new('Broad face normals','WEIGHTED_NORMAL');md.keep_sharp=True
        return ob

def ring(w,d,z,c=.025):
    x=w/2;y=d/2;c=min(c,w/5,d/5)
    return [(-x+c,-y,z),(x-c,-y,z),(x,-y+c,z),(x,y-c,z),(x-c,y,z),(-x+c,y,z),(-x,y-c,z),(-x,-y+c,z)]

a=Tonic('MossTonic','moss_tonic.png',PALETTE)
outer=[(.43,.355,.025),(.45,.375,.05),(.45,.375,.475),(.43,.355,.50),(.39,.325,.50),(.39,.325,.54),(.33,.28,.54),(.33,.28,.58),(.27,.235,.58),(.27,.235,.68),(.325,.284,.68),(.325,.284,.735)]
inner=[(w-.032,d-.032,z if j else z+.018) for j,(w,d,z) in enumerate(outer)]
verts=[v for w,d,z in outer+inner for v in ring(w,d,z)]
faces=[];n=len(outer);offset=n*8
for base in [0,offset]:
    for k in range(n-1):
        for j in range(8):faces.append((base+k*8+j,base+k*8+(j+1)%8,base+(k+1)*8+(j+1)%8,base+(k+1)*8+j))
# Both base surfaces are closed. Top joins the outer and inner walls around an open mouth.
faces.extend([tuple(range(7,-1,-1)),tuple(offset+j for j in range(8))])
for j in range(8):faces.append(((n-1)*8+j,(n-1)*8+(j+1)%8,offset+(n-1)*8+(j+1)%8,offset+(n-1)*8+j))
shell=a.solid('Continuous hollow glass bottle',verts,faces,20,a.glass,.0015)
shell['wall_thickness_m']=.016;shell['open_mouth']=True
liquid_rings=[(.397,.322,.045),(.414,.339,.055),(.414,.339,.478),(.348,.29,.502),(.348,.29,.522)]
vs=[v for w,d,z in liquid_rings for v in ring(w,d,z)]
fs=[tuple(range(7,-1,-1)),tuple((len(liquid_rings)-1)*8+j for j in range(8))]
for k in range(len(liquid_rings)-1):
    for j in range(8):fs.append((k*8+j,k*8+(j+1)%8,(k+1)*8+(j+1)%8,(k+1)*8+j))
a.solid('Contained teal tonic with level surface',vs,fs,0,a.liquid,.0006)

# Four substantial corner ribs and their pale mint collars.
for x in [-.204,.204]:
    for y in [-.165,.165]:
        a.box('Long glass corner rib',(x,y,.267),(.047,.046,.402),1,.003)
        for z in [.067,.458]:
            a.box('Mint corner collar',(x,y,z),(.056,.055,.058),3,.0025)
        a.box('Bright foot end',(x,y,.039),(.063,.058,.04),2,.0025)
for y in [-.174,.174]:
    for z in [.047,.48]:
        for k in range(7):a.box('Segmented body frame',((k-3)*.053,y,z),(.053,.035,.042),2 if z>.4 else 1,.0018)
for x in [-.216,.216]:
    for z in [.047,.48]:
        for k in range(5):a.box('Side body frame',(x,(k-2)*.06,z),(.029,.06,.042),2 if z>.4 else 1,.0018)
# Tiled shoulder bands sit on and overlap the actual closed bottle shell.
for level,(w,d,z) in enumerate([(.386,.323,.516),(.33,.279,.556),(.272,.237,.603)]):
    for face in [-1,1]:
        for k in range(5):a.box('Shoulder front blocks',((k-2)*w/5,face*d/2,z),(w/5,.023,.035),[2,1,6][level],.0018)
        for k in range(3):a.box('Shoulder side blocks',(face*w/2,(k-1)*d/3,z),(.023,d/3,.035),[2,1,6][level],.0018)
# Lip is a genuine ring, tiled around the cork opening.
for ix in range(7):
    for iy in range(6):
        if 1<=ix<=5 and 1<=iy<=4:continue
        a.box('Mint mouth rim',((ix-3)*.05,(iy-2.5)*.05,.712),(.05,.05,.058),3 if (ix+iy)%4 else 4,.003)
for ix in range(5):
    for iy in range(4):
        for iz in range(3):
            a.box('Tiled golden cork',((ix-2)*.045,(iy-1.5)*.045,.75+iz*.042),(.0448,.0448,.042),8 if iz<2 else 10,.0018)

# Raised blank cream label, with stepped clipped corners and fine physical tile seams.
for ix in range(8):
    for iz in range(7):
        if ix in [0,7] and iz in [0,6]:continue
        edge=ix in [0,7] or iz in [0,6]
        a.box('Blank label tile',((ix-3.5)*.036,-.198,(iz-3)*.034+.292),(.03595,.013 if edge else .012,.03395),11 if not edge else (13 if (ix+iz)%4==0 else 12),.0006)

# Braided collar rendered as joined angular cord segments, with two folded loops.
def bar(name,start,end,thick,index,depth=None):
    mid=(Vector(start)+Vector(end))/2;v=Vector(end)-Vector(start)
    ob=a.box(name,mid,(thick,depth or thick,v.length+thick*.25),index,.002)
    ob.rotation_euler=v.to_track_quat('Z','Y').to_euler();return ob
points=ring(.303,.267,.636,.032)
for j in range(8):
    p=Vector(points[j]);q=Vector(points[(j+1)%8]);count=max(1,round((q-p).length/.035))
    for k in range(count):bar('Gold neck cord',p+(q-p)*k/count,p+(q-p)*(k+1)/count,.024,18 if k%3==0 else 19)
for dx in [0,.042]:
    loop=[(.143+dx,-.108,.64),(.177+dx,-.119,.628),(.20+dx,-.124,.602),(.203+dx,-.122,.573),(.179+dx,-.112,.559),(.163+dx,-.10,.581),(.159+dx,-.097,.621)]
    for j in range(len(loop)):bar('Folded binding loop',loop[j],loop[(j+1)%len(loop)],.024,18)

leaf_matrix=Matrix.Translation(Vector((.225,-.118,.59)))@Matrix.Rotation(math.radians(35),4,'Z')@Matrix.Rotation(math.radians(-25),4,'Y')
def leaf_box(name,p,size,idx):
    ob=a.box(name,p,size,idx,.0015);ob.matrix_world=leaf_matrix@Matrix.Translation(Vector(p));return ob
rows=[2,4,5,6,6,5,4,3,1]
for r,count in enumerate(rows):
    for c in range(count):
        leaf_box('Leaf block',((c-(count-1)/2)*.034,0,-r*.034),(.034,.028,.034),14 if (r+c)%4 else 15)
for r in range(6):leaf_box('Pale central leaf vein',(0,-.016,-r*.034),(.020,.007,.034),17)
bar('Leaf attachment stem',(.191,-.107,.596),(.225,-.118,.607),.016,16)

# Sparse turquoise chips on the side wall, as in the concept.
for xsign in [-1,1]:
    for y,z in [(-.107,.36),(-.107,.324),(.10,.12),(.10,.087)]:
        a.box('Turquoise side glint',(xsign*.228,y,z),(.004,.037,.035),5,.0005)
a.studio((.023,0,.443),(3.35,-5,2.35),1.14)
a.scene.render.resolution_x=1254;a.scene.render.resolution_y=1254
a.scene.cycles.samples=64;a.scene.cycles.transmission_bounces=10
for ob in a.scene.objects:
    if ob.type=='LIGHT':
        if ob.name.startswith('Key'):ob.data.energy=1600
        elif ob.name.startswith('Fill'):ob.data.energy=600
a.scene['fidelity_status']='first_physical_bottle_pending_visual_review'
a.save()
spec={'source':'SourceAssets/Voxel/moss_tonic.png','interpretation':'One visible view; rear label-free and underside inferred. Hollow closed glass wall with open mouth, separate liquid, tiled cork, neck cord and attached leaf.','materials':['Trim','Glass','Liquid'],'status':'pending_render_comparison_and_engine_import'}
(a.review/'source-adaptation.json').write_text(json.dumps(spec,indent=2))
result={'asset':a.key,'parts':len(a.parts),'scene':a.scene.name}
