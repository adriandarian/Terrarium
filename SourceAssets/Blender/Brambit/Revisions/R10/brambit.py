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
        base=[];roughness=[]
        for y in range(512):
            for x in range(512):
                idx=min(y//64*8+x//64,len(self.palette)-1)
                hx,rough,_=self.palette[idx]
                # Small rectangular pigment changes, without baked illumination.
                tx=(x%64)//6;ty=(y%64)//7
                patch=((tx*37+ty*71+idx*23+tx*ty*11)%19-9)/9
                strength=.060 if idx in [4,5,6] else .020 if idx==7 else .065 if 8<=idx<=13 else .080
                rgb=[int(hx[j:j+2],16)/255 for j in (0,2,4)]
                base.extend([linear(min(1,c*(1+strength*patch))) for c in rgb]+[1])
                roughness.extend([max(0,min(1,rough+.040*patch))]*3+[1])
        for image,pixels in [(self.images[0],base),(self.images[2],roughness)]:
            image.pixels.foreach_set(pixels);image.save();image.pack()
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
body=[(x,.42+(z-.42)*.80 if z<.42 else min(z,.641)) for x,z in body]
# Successively smaller cross-sections round the back in all three axes. The
# broad front profile stays intact; the rear terminates in a small central
# mound rather than a second flat copy of the face.
body_sections=[(FRONT,.060,1.,1.),(.030,.112,.93,.97),(.088,.164,.76,.86),(.140,.182,.48,.61)]
for i,(near,far,sx,sz) in enumerate(body_sections):
    slab('Rounded stepped brown body' if i==0 else 'Rounded rear course',[(x*sx,.42+(z-.42)*sz) for x,z in body],near,far-near,0 if i<2 else 3)

def body_half_width(z):
    intersections=[]
    for p,q in zip(body,body[1:]+body[:1]):
        if (p[1]>z)!=(q[1]>z):intersections.append(p[0]+(z-p[1])*(q[0]-p[0])/(q[1]-p[1]))
    return max(intersections) if intersections else 0

def side_surface(y,z):
    return max([body_half_width(.42+(z-.42)/sz)*sx for near,far,sx,sz in body_sections if near<=y<=far] or [0])

def rear_surface(x,z):
    return max([far for near,far,sx,sz in body_sections if abs(x)<body_half_width(.42+(z-.42)/sz)*sx] or [0])

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
front_box('Forehead brown peak',672,574,84,105,2,FRONT-.026,52)
# Broad, staggered bark regions follow the visible side's quiet large planes.
# Dimensions are depth-axis center, height, depth-axis span, height span,
# outward relief and pigment. Small burrs are separate from the broad bark.
side_bark=[
 (-.212,.300,.095,.080,.013,0),(-.109,.307,.104,.094,.009,1),(.008,.316,.119,.087,.015,3),
 (-.211,.391,.098,.098,.008,1),(-.100,.400,.122,.092,.012,0),(.023,.408,.110,.102,.009,0),
 (-.216,.493,.092,.112,.012,0),(-.105,.498,.122,.101,.009,1),(.017,.501,.112,.092,.014,0),
 (-.217,.586,.091,.075,.009,1),(-.110,.589,.110,.082,.014,0),(.002,.587,.108,.077,.010,1),
 (.087,.351,.057,.073,.008,3),(.103,.454,.060,.112,.010,0),(.083,.558,.066,.087,.009,3),
]
for side in [-1,1]:
    for y,z,width,height,depth,idx in side_bark:
        half=side_surface(y,z)
        if half:
            box('Broad side bark',(XC+side*(half+depth/2-.006),y,z),(depth,width,height),idx)
    # Sparse chunky knots replace the repeated rows of narrow overlapping tiles.
    for y,z,span,depth in [(-.112,.529,.053,.050),(-.107,.389,.060,.044),(.082,.452,.057,.038)]:
        half=side_surface(y,z)
        box('Side bark knot',(XC+side*(half+depth/2-.006),y,z),(depth,span,span),1)
rear_bark=[
 (-.143,.319,.097,.100),(-.040,.309,.106,.089),(.072,.323,.115,.109),(.166,.361,.080,.096),
 (-.194,.420,.087,.107),(-.095,.431,.111,.125),(.024,.419,.119,.110),(.144,.463,.105,.107),
 (-.162,.538,.109,.118),(-.043,.552,.116,.123),(.077,.558,.112,.092),
 (-.140,.618,.110,.058),(-.020,.628,.115,.061),(.099,.620,.107,.070),
]
for i,(x,z,width,height) in enumerate(rear_bark):
    surface=rear_surface(x,z)
    if surface:
        depth=[.010,.014,.008][i%3]
        box('Broad back bark',(XC+x,surface+depth/2-.006,z),(width,depth,height),[0,1,0,3][i%4])
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
for u,v,w,h,idx in [(649,953,75,67,4),(724,934,74,66,4),(602,936,47,26,6)]:
    front_box('Tan belly step',u,v,w,h,idx,FRONT-.019,8)

# The three visible front-left lower sole corners are approximately
# (525,1155), (362,1066), and (813,1089) in the concept. These placements
# follow those landmarks while retaining a shared physical support plane.
foot_centers=[(-.286,-.231),(-.260,.075),(.060,-.250),(.034,.056)]
for x,y in foot_centers:
    leg=box('Stump leg',(x,y+.006,.200),(.096,.086,.103),1,.002);leg['anatomy']='leg'
    foot=box('Dark foot',(x,y,.1445),(.098,.090,.055),7,.0015);foot['anatomy']='foot'

# Authored crown heights replace the symmetric ellipsoid. The lower front
# courses expose the leaf stems and forehead, with a raised left shoulder and
# the warm saddle immediately in front of the central shoot's root.
# Rows run front to back; columns run left to right in world X.
crown_heights=[
 [.675,.675,.675,.675,.675,.675,.675,.684,.675],
 [.675,.702,.702,.702,.702,.675,.675,.684,.684],
 [.702,.729,.729,.729,.729,.702,.702,.702,.675],
 [.702,.702,.729,.756,.729,.702,.732,.720,.675],
 [.675,.675,.675,.702,.729,.702,.723,.710,.675],
 [.651,.651,.651,.651,.702,.699,.699,.699,.675],
 [.651,.651,.651,.651,.702,.699,.699,.699,.651],
]
for ix in range(-4,5):
    for iy in range(7):
        x=ix*.060;y=-.251+iy*.061
        radial=(x/.285)**2+((y+.07)/.235)**2
        if radial>1.22:continue
        top=crown_heights[iy][ix+4]
        bottom=.616 if abs(x)>.20 or iy==0 else .622
        idx=[8,9,10,11,12,13][(ix*13+iy*7)%6]
        if ix in [2,3] and iy in [3,4]:idx=14
        box('Moss crown block',(XC+x,y,(top+bottom)/2),(.063,.064,top-bottom+.003),idx,.0018)['anatomy']='moss'

front_box('Moss crown central shoulder',600,465,50,63,9,-.164,45)['anatomy']='moss'

# Each shoot follows explicit visible cube corners, with independent thickness.
central=[(619,109,48,77,10,44),(583,181,40,59,9,44),(623,198,45,67,8,40),
 (668,213,42,63,9,41),(547,250,39,49,8,44),(585,270,39,51,9,39),
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
    if label.endswith('leafy shoot'):
        from box_union import box_union
        base=box_union(label,sources,a.scene,a.material)
    else:
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
        # Shared planes can differ by float-rounding noise. Remove microscopic
        # slivers before beveling, while retaining the closed boundary surface.
        import bmesh
        bm=bmesh.new();bm.from_mesh(base.data)
        before=len(bm.verts)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0,label
        base['numerical_cleanup_merged_vertices']=before-len(bm.verts)
        bm.to_mesh(base.data);bm.free()
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
# Planar UV coordinates span the pigment cells. Mapping relative to the entire
# authored volume keeps texture scale consistent across adjoining grid faces.
from collections import Counter
bpy.context.view_layer.update()
vertices=[ob.matrix_world@v.co for ob in a.parts for v in ob.data.vertices]
lo=[min(v[i] for v in vertices) for i in range(3)]
hi=[max(v[i] for v in vertices) for i in range(3)]
for ob in a.parts:
    uv=ob.data.uv_layers.active
    for face in ob.data.polygons:
        counts=Counter(min(15,max(0,int(uv.data[j].uv.y*8)*8+int(uv.data[j].uv.x*8))) for j in face.loop_indices)
        pigment=counts.most_common(1)[0][0]
        axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(face.normal[i]))]
        for index in face.loop_indices:
            v=ob.matrix_world@ob.data.vertices[ob.data.loops[index].vertex_index].co
            uv.data[index].uv=tuple((pigment%8 if j==0 else pigment//8)/8+.006+.113*(v[axis]-lo[axis])/(hi[axis]-lo[axis]) for j,axis in enumerate(axes))
    ob['surface_uv_mapping']='Planar pigment-cell coverage in authored bounds'
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
(a.review/'source-adaptation.json').write_text(json.dumps({'revision':'r10_broad_bark_regions','source':s['concept'],'source_sha256':hashlib.sha256((ROOT/s['concept']).read_bytes()).hexdigest(),'method':'Five closed volumes, with planar quad unions for the shoots and Boolean unions for the body and cap, retain hidden editable construction blocks. Coplanar leaf and bark overlaps have been removed from the visible geometry. A shortened stepped body with four shrinking rear cross-sections and broad staggered bark regions and sparse chunky knots, inset tan face, physical dark eyes and nose, wrapping bark plates, four narrower stump legs and dark feet placed from the three visible sole landmarks, asymmetric moss cap with lower front courses and an offset warm saddle and three asymmetric leafy shoots assembled from measured visible cube corners. Micrometre-scale Boolean slivers are cleaned before beveling. Block-varied pigment and roughness atlases with planar UV coverage; no source-image projection or baked illumination.','inferred':'Back surfaces, hidden fourth leg, depth and underside are inferred from the single concept. Static model only; not yet rigged or animated.','status':'pending_export_and_visual_refinement','accepted_fidelity':False},indent=2))
result={'asset':'Brambit','parts':len(a.parts),'file':str(a.out/'Brambit.blend')}


