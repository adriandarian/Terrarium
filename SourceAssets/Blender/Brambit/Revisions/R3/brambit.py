"""Physical Brambit: rounded stepped body, inset face, feet and three shoots."""
import bpy,sys,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path('C:/Users/hello/Projects/Terrarium')
assert Path(bpy.context.scene.get('terrarium_project',''))==ROOT
sys.path.insert(0,str(ROOT/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset,linear

# Pigments only. Form shading is supplied by actual geometry and studio lights.
P=[('92541f',.8,0),('a56528',.79,0),('b87530',.77,0),('8b541e',.82,0),
   ('d5a35e',.75,0),('deb477',.74,0),('c8924c',.79,0),('3d3827',.86,0),
   ('6e791f',.8,0),('7d882a',.78,0),('8b952f',.78,0),('57631b',.83,0),
   ('6b6f20',.82,0),('9b9b3c',.78,0),('a07b32',.8,0),('bc893e',.78,0)]
class BrambitAsset(PaletteAsset):
    def make_material(self):
        super().make_material()
        self.material.name='M_Brambit_Pigment'
        self.material.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0
        colors=[[linear(int(h[j:j+2],16)/255) for j in (0,2,4)]+[1] for h,_,_ in self.palette]
        self.images[0].pixels.foreach_set([c for y in range(512) for x in range(512) for c in colors[min(y//64*8+x//64,len(colors)-1)]])
        self.images[0].save();self.images[0].pack()
a=BrambitAsset('Brambit','brambit.png',P)
AZ=math.radians(37);EL=math.radians(20);UNIT=.001;V0=1120
XC=-.095;FRONT=-.28

def point(u,v,y):
    x=((u-627)*UNIT+math.sin(AZ)*y)/math.cos(AZ)
    z=((V0-v)*UNIT-math.sin(EL)*(math.sin(AZ)*x+math.cos(AZ)*y))/math.cos(EL)
    return Vector((x,y,z))

def box(name,center,size,index,bevel=.0015):
    ob=a.box(name,center,size,index,bevel);ob['palette_index']=index
    return ob

def front_box(name,u,v,w,h,index,y,depth_px):
    # u,v is the top left corner of the broad front face; its right edge
    # naturally rises in the orthographic view. Depth extends behind the face.
    corner=point(u,v,y);width=w*UNIT/math.cos(AZ)
    height=h*UNIT/math.cos(EL);depth=depth_px*UNIT/math.sin(AZ)
    ob=box(name,corner+Vector((width/2,depth/2,-height/2)),(width+.002,depth+.002,height+.002),index)
    ob['reference_corner']=[u,v];ob['anatomy']='crown'
    return ob

def slab(name,outline,y,depth,index,bevel=.0015):
    front=[Vector((XC+x,y,z)) for x,z in outline];n=len(front)
    tris=tessellate_polygon([front])
    def ix(p):return p if isinstance(p,int) else min(range(n),key=lambda j:(front[j]-p).length_squared)
    faces=[tuple(ix(p) for p in tri) for tri in tris]
    faces += [tuple(i+n for i in reversed(t)) for t in list(faces)]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=a.solid(name,[tuple(p) for p in front]+[tuple(p+Vector((0,depth,0))) for p in front],faces,index,bevel=bevel)
    ob['palette_index']=index;return ob

body=[(-.18,.175),(.18,.175),(.18,.205),(.245,.205),(.245,.285),(.282,.285),(.282,.545),(.245,.545),(.245,.615),(.19,.615),(.19,.665),(-.19,.665),(-.19,.615),(-.245,.615),(-.245,.545),(-.282,.545),(-.282,.285),(-.245,.285),(-.245,.205),(-.18,.205)]
body=[(x,.42+(z-.42)*.80 if z<.42 else z) for x,z in body]
slab('Rounded stepped brown body',body,FRONT,.40,0)
# A second narrower back tier rounds the profile in depth instead of ending the
# animal in a copied front plate. It has no facial marks on the back.
slab('Rounded rear tier',[(x*.87,.42+(z-.42)*.88) for x,z in body],.10,.055,3)

face_pixels=[(553,779),(602,766),(602,735),(650,722),(650,695),(700,682),(700,728),(748,715),(748,673),(799,660),(799,687),(847,674),(847,706),(894,693),(894,834),(845,847),(845,899),(799,912),(799,979),(649,1020),(649,956),(600,969),(600,930),(553,943)]
face=[(point(u,v,FRONT-.012).x-XC,point(u,v,FRONT-.012).z) for u,v in face_pixels]
slab('Tan face and lower belly',face,FRONT-.012,.019,5,.001)

def inside(x,z,poly):
    hit=False
    for p,q in zip(poly,poly[1:]+poly[:1]):
        if (p[1]>z)!=(q[1]>z) and x<(q[0]-p[0])*(z-p[1])/(q[1]-p[1])+p[0]:hit=not hit
    return hit

rng=random.Random(82)
# Uneven bark plates wrap the full volume. Front plates stay outside the tan
# facial field; they are individual cubes with physical side faces.
front_bark=[(505,715,46,57,1),(552,700,48,63,0),(601,670,48,49,1),
 (650,653,49,51,1),(699,641,50,40,1),(749,628,49,43,1),(799,630,49,41,0),
 (849,613,48,63,1),(900,650,40,54,0),(506,779,46,118,0),
 (506,897,46,61,1),(552,944,48,56,0),(601,971,48,51,1),
 (894,707,46,81,0),(895,786,46,59,1),(850,853,44,40,1),
 (847,899,46,59,0),(800,925,47,59,1)]
for row in front_bark:front_box('Front bark course',*row[:5],FRONT-.017,12)
front_box('Forehead brown peak',672,574,84,105,2,FRONT-.026,34)
for side in [-1,1]:
    for iz in range(7):
        z=.295+iz*.049
        half=.282 if .285<z<.545 else .245
        for iy in range(6):
            y=-.24+iy*.066
            if (iy+2*iz+(1 if side==1 else 0))%5==0:continue
            depth=rng.choice([.010,.017,.024])
            box('Side bark plates',(XC+side*(half+depth/2-.004),y,z),(depth,.068,.059),rng.choice([0,1,3]))
for ix in range(-3,4):
    for iz in range(6):
        box('Back bark course',(XC+ix*.058,.159,.295+iz*.049),(.060,.025,.061),rng.choice([0,1,3]))
# Four conspicuous front-edge burrs, corresponding to the concept's silhouette.
for dx,z in [(-.25,.38),(-.245,.52),(.25,.34),(.25,.48)]:
    box('Bark edge bump',(XC+dx,FRONT-.031,z),(.049,.041,.049),1)

# The two eyes are shallow dark inserts, not a texture pasted onto the head.
for name,u,v,w,h in [('Left eye',626,811,46,66),('Right eye',822.5,770,45,65)]:
    front=point(u,v,FRONT-.021)
    ob=box(name,front+Vector((0,.005,0)),(w*UNIT/math.cos(AZ),.010,h*UNIT/math.cos(EL)),7,.001)
    ob['reference_center']=[u,v];ob['anatomy']='face'
front=point(746,819,FRONT-.053)
box('Small charcoal nose',front+Vector((0,.021,0)),(.069,.042,.038),7,.0015)['anatomy']='face'
# Small tan/ochre planes at the lower muzzle and belly are physical shallow steps.
for u,v,w,h,idx in [(649,953,75,43,4),(724,934,74,43,4),(602,936,47,26,6)]:
    front_box('Tan belly step',u,v,w,h,idx,FRONT-.019,8)

# Squat feet have broad flat support surfaces and dark tips. The rear pair is
# modeled too, even though the concept hides most of the far rear foot.
for x in [XC-.202,XC+.202]:
    for y in [-.225,.087]:
        leg=box('Stump leg',(x,y,.178),(.108,.114,.147),1,.002);leg['anatomy']='leg'
        foot=box('Dark foot',(x,y-.006,.1165),(.111,.122,.047),7,.0015);foot['anatomy']='foot'

# A broad, stepped moss cap sits on the brown volume. Course heights are set
# from an ellipsoidal crown, while blocks remain square and visibly stepped.
for ix in range(-4,5):
    for iy in range(7):
        x=ix*.060;y=-.251+iy*.061
        radial=(x/.285)**2+((y+.07)/.235)**2
        if radial>1.22:continue
        top=.675+.105*max(0,1-radial)
        top=round(top/.027)*.027
        if y>.02 and XC+x<-.12:top=min(top,.651)
        elif y>.02 and XC+x>-.09:top=min(top,.699)
        bottom=.616 if abs(x)>.20 or iy==0 else .622
        idx=[8,9,10,11,12,13][(ix*13+iy*7)%6]
        # The original includes a small warm-brown saddle between green courses.
        if ix in [0,1] and iy in [3,4]:idx=14
        box('Moss crown block',(XC+x,y,(top+bottom)/2),(.063,.064,top-bottom+.003),idx,.0018)['anatomy']='moss'

# Each shoot follows explicit visible cube corners, with independent thickness.
central=[(619,109,48,77,10,44),(583,181,40,59,9,44),(623,198,45,67,8,40),
 (668,213,42,63,9,41),(547,250,39,49,8,44),(585,240,39,51,9,39),
 (623,264,45,52,8,41),(668,254,45,58,9,40),(712,242,33,48,10,34),
 (547,299,40,40,11,44),(585,289,39,44,8,39),(623,314,71,62,11,43)]
for row in central:front_box('Central shoot leaves',*row[:5],.06,row[5])
front_box('Central shoot stem',622,375,46,69,14,.06,39)
left=[(378,272,47,73,9,44),(346,339,40,55,9,42),(385,356,42,64,8,38),
 (427,369,41,57,9,38),(469,387,41,45,9,39),(347,393,42,49,11,42),
 (389,419,41,44,11,39),(430,407,39,49,8,39)]
for row in left:front_box('Left shoot leaves',*row[:5],.10,row[5])
front_box('Left shoot stem',427,455,44,66,14,.10,39)
right=[(950,329,52,57,10,54),(897,377,54,59,9,51),(925,435,47,54,8,47),
       (895,427,31,48,11,43)]
for row in right:front_box('Right shoot leaves',*row[:5],-.24,row[5])
front_box('Right shoot stem',848,474,46,53,8,-.24,38)
front_box('Central shoot inner join',620,184,48,22,9,.085,32)
front_box('Central shoot lower join',669,265,42,25,9,.085,32)
front_box('Left shoot inner join',379,337,45,24,9,.125,31)
front_box('Left shoot lower join',427,414,42,24,8,.125,31)
front_box('Right shoot inner join',900,427,30,22,8,-.215,31)

for ob in a.parts:
    idx=ob['palette_index'];uv=((idx%8+.5)/8,(idx//8+.5)/8)
    for loop in ob.data.uv_layers.active.data:loop.uv=uv

construction=bpy.data.collections.new('Editable construction blocks')
a.scene.collection.children.link(construction)
construction_count=len(a.parts)
def join_volume(label,sources):
    """Resolve shared faces while retaining the authored cubes as source data."""
    temp=bpy.data.collections.new(label+' operands');a.scene.collection.children.link(temp)
    operands=[]
    for source in sources:
        ob=source.copy();ob.data=source.data.copy();ob.modifiers.clear()
        temp.objects.link(ob);operands.append(ob)
    base=operands[0];temp.objects.unlink(base);a.scene.collection.objects.link(base)
    modifier=base.modifiers.new('Physical union','BOOLEAN')
    modifier.operation='UNION';modifier.operand_type='COLLECTION';modifier.collection=temp;modifier.solver='EXACT'
    bpy.context.view_layer.objects.active=base;bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.batch_remove(ids=operands[1:]);bpy.data.collections.remove(temp)
    base.name=label;base['part']=label;base['construction_count']=len(sources)
    for key in ['palette_index','reference_corner','reference_center','anatomy']:
        if key in base:del base[key]
    modifier=base.modifiers.new('Soft voxel edges','BEVEL');modifier.width=.0015;modifier.segments=2
    for source in sources:
        source['construction_part']=source['part'];del source['part']
        for coll in list(source.users_collection):coll.objects.unlink(source)
        construction.objects.link(source);source.hide_render=True;source.hide_set(True);a.parts.remove(source)
    a.parts.append(base)

for name in ['Central','Left','Right']:
    join_volume(name+' leafy shoot',[ob for ob in a.parts if ob.name.startswith(name+' shoot')])
join_volume('Joined moss crown',[ob for ob in a.parts if ob.name.startswith('Moss crown block')])
join_volume('Joined body face and feet',[ob for ob in a.parts if not ob.name.endswith('leafy shoot') and ob.name!='Joined moss crown'])
focus=(0,0,(V0-627)*UNIT/math.cos(EL))
camera=Vector(focus)+Vector((-math.sin(AZ)*5,-math.cos(AZ)*5,math.tan(EL)*5))
a.studio(focus,camera,1254*UNIT)
s=a.scene;s.render.resolution_x=s.render.resolution_y=1254;s.cycles.samples=64
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=-.15
s['reference_focus']=focus;s['reference_azimuth_deg']=37;s['reference_elevation_deg']=20
s['editable_construction_blocks']=construction_count
for ob in s.objects:
    if ob.type=='LIGHT' and ob.name.startswith('Key'):
        ob.location=(-3,-5,7);ob.data.energy=650;ob.data.color=(1,.97,.90)
        ob.rotation_euler=(Vector(focus)-ob.location).to_track_quat('-Z','Y').to_euler()
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'revision':'r3_joined_physical_volumes','source':s['concept'],'source_sha256':hashlib.sha256((ROOT/s['concept']).read_bytes()).hexdigest(),'method':'Five closed Boolean-unioned volumes retain 240 hidden editable construction blocks. Coplanar leaf and bark overlaps have been removed from the visible geometry. A shortened stepped body with a rounded rear tier, inset tan face, physical dark eyes and nose, wrapping bark plates, four stump legs and dark feet, volumetric moss cap and three asymmetric leafy shoots assembled from measured visible cube corners. Flat pigment and roughness atlases; no source-image projection.','inferred':'Back surfaces, hidden fourth leg, depth and underside are inferred from the single concept. Static model only; not yet rigged or animated.','status':'pending_export_and_visual_refinement','accepted_fidelity':False},indent=2))
result={'asset':'Brambit','parts':len(a.parts),'file':str(a.out/'Brambit.blend')}
