"""Author Storm as a solid lightning extrusion, cloud blocks and separate sparks."""
import bpy,sys,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon,delaunay_2d_cdt
ROOT=Path('C:/Users/hello/Projects/Terrarium')
assert Path(bpy.context.scene.get('terrarium_project',''))==ROOT
sys.path.insert(0,str(ROOT/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset,linear
P=[('ffc51b',.44,0),('efac16',.48,0),('d99a14',.52,0),('ffe8a4',.4,0),('ffe29b',.44,0),('697486',.69,0),('566173',.72,0),('a09783',.72,0)]
class StormAsset(PaletteAsset):
    def make_material(self):
        super().make_material()
        colors=[[linear(int(h[j:j+2],16)/255) for j in (0,2,4)]+[1] for h,_,_ in self.palette]
        pixels=[channel for y in range(512) for x in range(512) for channel in colors[min(y//64*8+x//64,len(colors)-1)]]
        self.images[0].pixels.foreach_set(pixels);self.images[0].save();self.images[0].pack()
a=StormAsset('Storm','storm.png',P)
a.material.name='M_Storm_Cloud'
a.material.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0
bolt=a.shader('Lightning',metallic=0)
az=math.radians(45);el=math.radians(30);unit=.0012;origin_v=1160

def point(u,v,x):
    y=(math.cos(az)*x-(u-627)*unit)/math.sin(az)
    z=((origin_v-v)*unit-math.sin(el)*(math.sin(az)*x+math.cos(az)*y))/math.cos(el)
    return Vector((x,y,z))

def prism(label,outline,x,depth,index):
    # Intentional planar caps keep the lightning face clean. Random per-vertex
    # offsets produced diagonal creases absent from the painted concept.
    front=[point(u,v,x) for u,v in outline]
    # Preserve the physical side walls of the connected core. Taper the last
    # 140 source pixels into the narrower lower wedge visible in the concept.
    rear=[]
    for (u,v),p in zip(outline,front):
        taper=max(0.,min(1.,(v-982)/140))
        d=depth*(1-taper)+.056*taper
        rear.append(p+Vector((d,0,0)))
    n=len(front)
    # Concave caps are explicitly triangulated; the side walls close the volume.
    triangles=tessellate_polygon([front])
    def idx(p):return p if isinstance(p,int) else min(range(n),key=lambda i:(front[i]-p).length_squared)
    cap=[tuple(idx(p) for p in tri) for tri in triangles]
    # A continuous longitudinal ridge gives the inferred back a sculpted volume.
    # Its crease follows the cream spine's change of direction and tapers with
    # the lower gold point. Boundary depths remain unchanged, preserving the
    # cloud connections and the source-visible side-wall outline.
    ridge=[(590,446,.145),(630,535,.16),(618,596,.17),(590,710,.17),
           (566,807,.15),(544,898,.13),(530,964,.105),(512,1044,.09),(490,1090,.075)]
    ridge=[node for node in ridge if node[1]>min(v for _,v in outline)+4]
    coords=[Vector((u,v)) for u,v in outline]+[Vector((u,v)) for u,v,_ in ridge]
    crease=[(n+i,n+i+1) for i in range(len(ridge)-1)]
    ring=list(range(n))
    if sum(coords[i].x*coords[(i+1)%n].y-coords[(i+1)%n].x*coords[i].y for i in range(n))<0:ring.reverse()
    cdt=delaunay_2d_cdt(coords,crease,[ring],1,.00001,True)
    rear.extend(point(u,v,x)+Vector((back_x-x,0,0)) for u,v,back_x in ridge)
    remap=[]
    for ids in cdt[3]:
        assert len(ids)==1,('Unexpected merged/intersection vertex in back ridge',ids)
        remap.append(ids[0])
    faces=cap+[tuple(n+remap[i] for i in reversed(t)) for t in cdt[2]]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=a.solid(label,[tuple(p) for p in front+rear],faces,index,material=bolt,bevel=.002)
    o['reference_outline']=json.dumps(outline);o['physical_depth_m']=depth
    o['palette_index']=index
    o['inferred_back_ridge']=json.dumps(ridge)
    return o

gold=[(610,440),(658,557),(803,557),(787,598),(756,665),(734,719),(711,766),(678,812),(658,848),(623,889),(602,918),(580,1025),(499,1122),(481,1114),(480,958),(499,911),(463,884),(463,788),(479,768),(479,698),(392,702),(392,580),(432,554),(432,493),(469,477),(470,445),(500,429),(501,354),(539,335)]
cream=[(555,338),(618,359),(618,440),(547,468),(547,582),(687,590),(602,810),(548,918),(532,981),(482,957),(511,864),(531,811),(545,783),(545,653),(441,654),(441,591),(477,574),(490,460),(547,434)]
# The upper body is built from complete stepped blocks below, so remove the
# old sheet behind them. Keep the lower angular core below this shoulder line.
clipped=[]
for start,end in zip(gold,gold[1:]+gold[:1]):
    inside_a=start[1]>=440;inside_b=end[1]>=440
    if inside_a:clipped.append(start)
    if inside_a!=inside_b:
        t=(440-start[1])/(end[1]-start[1]);clipped.append((start[0]+t*(end[0]-start[0]),440))
clipped=[p for i,p in enumerate(clipped) if (Vector(p)-Vector(clipped[i-1])).length>.00001]
prism('Golden lightning body',clipped,.015,.075,0)

def cube(u,v,w,h,index,x=.04,spark=False,depth_pixels=None):
    seam=[u,v]
    # v names the top of the front seam. Correct for the actual camera slope;
    # using w/2 here shifted every cube upward relative to its measured anchor.
    v-=w*math.sin(el)*.5
    width=w*unit/math.cos(az);height=h*unit/math.cos(el)
    depth=(depth_pixels if depth_pixels is not None else w)*unit/math.cos(az)
    # Reference rectangle measures the right visible face from its left seam.
    uc=u+w/2;vc=v+h/2
    y=(math.cos(az)*x-(uc-627)*unit)/math.sin(az)
    z=((origin_v-vc)*unit-math.sin(el)*(math.sin(az)*x+math.cos(az)*y))/math.cos(el)
    join=.002 if not spark else 0
    o=a.box('Spark' if spark else ('Cloud cube' if index>=5 else 'Lightning cube'),(x,y+depth/2,z),(width+join,depth+join,height+join),index,.0015)
    if index<5:o.data.materials[0]=bolt
    o['reference_rect']=[u,v,w,h];o['reference_seam']=seam;o['palette_index']=index
    if spark:o['detached_reference_feature']=True
    return o

def close_gold_surface(front,triangles,boundary_count):
    """Close the visible gold surface at its silhouette, without a copied rim.

    Front and rear share boundary vertices. Interior rear vertices move along
    the reference ray; positive depth on every internal edge creates one volume.
    Matching front/rear triangulations make their order explicit throughout.
    """
    from collections import Counter
    edges=Counter(tuple(sorted((t[i],t[(i+1)%3]))) for t in triangles for i in range(3))
    assert all(count in (1,2) for count in edges.values())
    vertices=list(front);boundary=set(range(boundary_count));midpoints={}
    for edge,count in edges.items():
        idx=len(vertices);midpoints[edge]=idx;vertices.append((front[edge[0]]+front[edge[1]])*.5)
        if count==1:boundary.add(idx)
    refined=[]
    for tri in triangles:
        center=len(vertices);vertices.append(sum((front[i] for i in tri),Vector())/3)
        for i in range(3):
            a0=tri[i];b0=tri[(i+1)%3];mid=midpoints[tuple(sorted((a0,b0)))]
            refined.extend([(a0,mid,center),(mid,b0,center)])
    def project(p):
        return Vector((627+(math.cos(az)*p.x-math.sin(az)*p.y)/unit,
                       origin_v-(math.cos(el)*p.z+math.sin(el)*(math.sin(az)*p.x+math.cos(az)*p.y))/unit))
    rim=[project(p) for p in front[:boundary_count]]
    def distance_to_rim(p):
        uv=project(p);distances=[]
        for a0,b0 in zip(rim,rim[1:]+rim[:1]):
            edge=b0-a0;t=max(0.,min(1.,(uv-a0).dot(edge)/max(edge.length_squared,1e-12)))
            distances.append((uv-a0-edge*t).length)
        return min(distances)
    back={}
    for i in range(len(vertices)):
        if i in boundary:back[i]=i
        else:
            depth=.10*min(1.,distance_to_rim(vertices[i])/30)
            offset=Vector((depth,depth,-math.sqrt(2)*math.tan(el)*depth))
            back[i]=len(vertices);vertices.append(vertices[i]+offset)
    return vertices,refined+[tuple(back[i] for i in reversed(t)) for t in refined]

def relief(label,outline,depths,patches,index=0,boundary_count=None):
    """Faceted solid with the source outline shared by front and inferred back.

    Rear vertices share the front's reference coordinates, with an inferred
    depth plane enclosing the visible facets. Gold corners retain their authored
    depths; the broader cream patches are fitted to planes.
    """
    # Enforce planar artist-defined patches. This prevents triangulation from
    # adding spurious creases through a broad facet when four corners differ.
    constraints=[]
    for patch in patches if index==3 else []:
        basis=np.array([[outline[i][0],outline[i][1],1] for i in patch[:3]],dtype=float).T
        for i in patch[3:]:
            weights=np.linalg.solve(basis,np.array([*outline[i],1],dtype=float))
            row=np.zeros(len(outline));row[i]=1
            for j,w in zip(patch[:3],weights):row[j]-=w
            constraints.append(row)
    matrix=np.vstack((np.eye(len(outline)),np.array(constraints).reshape((-1,len(outline)))*1000))
    depths=np.linalg.lstsq(matrix,np.concatenate((np.array(depths),np.zeros(len(constraints)))),rcond=None)[0].tolist()
    front=[point(u,v,x) for (u,v),x in zip(outline,depths)]
    n=len(front)
    # Cream wedge backs terminate within the gold core's rear plane. A uniform
    # offset of the sculpted front made a white duplicate poke through the back.
    cream_back=.01 if label=='Cream tip facets' else (.025 if label=='Cream lower angled face' else .075)
    gold_back=.21 if label=='Gold upper diagonal ledge' else .15
    rear=[point(u,v,cream_back if index==3 else gold_back) for u,v in outline]
    faces=[]
    for patch in patches:
        # Triangulate within each deliberate facet, not across the whole ledge.
        poly=[front[i] for i in patch]
        for triangle in tessellate_polygon([poly]):
            faces.append(tuple(patch[p] if isinstance(p,int) else min(patch,key=lambda j:(front[j]-p).length_squared) for p in triangle))
    boundary_count=boundary_count or n
    if index==0:
        vertices,faces=close_gold_surface(front,faces,boundary_count)
    else:
        vertices=front+rear
        faces += [tuple(i+n for i in reversed(face)) for face in list(faces)]
        faces += [(i,(i+1)%boundary_count,(i+1)%boundary_count+n,i+n) for i in range(boundary_count)]
    ob=a.solid(label,[tuple(p) for p in vertices],faces,index,material=bolt,bevel=.0015)
    ob['reference_outline']=json.dumps(outline);ob['sculpted_facet_depths']=depths
    ob['palette_index']=index
    return ob

def cream_block(label,outline,depths,index=3):
    """Seven visible corners complete a real eight-corner block.

    The three visible faces share corner 6. Infer the hidden corner from the
    three opposite-face completions, instead of extruding those visible faces
    and introducing a second, oversized block behind them.
    """
    p=[point(u,v,x) for (u,v),x in zip(outline,depths)]
    hidden=((p[1]+p[4]-p[6])+(p[3]+p[0]-p[6])+(p[5]+p[2]-p[6]))/3
    ob=a.solid(label,[tuple(v) for v in p+[hidden]],[(0,1,2,6),(0,6,4,5),(6,2,3,4),(0,5,7,1),(1,7,3,2),(3,7,5,4)],index,material=bolt,bevel=.0015)
    ob['reference_outline']=json.dumps(outline);ob['inferred_hidden_corner']=list(hidden)
    ob['palette_index']=index
    return ob

# The cream is built from raised, faceted volumes. Each explicit patch denotes
# a visible top/front/side face in the concept, with a complete inferred back.
cream_block('Cream upper block',[(553,322),(579,307),(650,328),(650,421),(618,439),(548,438),(618,348)],[-.06,-.0235,-.0057,-.0057,-.06,-.06,-.06])
cream_block('Cream middle block',[(490,460),(547,436),(591,446),(591,555),(548,588),(479,579),(548,471)],[x+.025 for x in [-.07,-.0115,.0089,.003,-.07,-.07,-.07]])
relief('Cream crossbar and main face',[(441,592),(547,586),(591,556),(687,556),(718,579),(688,650),(602,811),(546,783),(546,652),(441,654),(687,594),(546,594)],[-.055,-.04,.025,.025,.025,.025,-.055,-.055,-.055,-.055,-.055,-.055],[(8,9,0,11,10,6,7),(0,1,11),(1,2,3,4,10,11),(4,5,6,10)],index=3,boundary_count=10)
relief('Cream lower angled face',[(546,781),(604,810),(548,919),(499,911),(512,864),(530,811)],[-.055,-.055,-.035,-.06,-.075,-.06],[(0,1,2,5),(5,2,3,4)],index=3)
relief('Cream tip facets',[(499,909),(550,916),(533,981),(482,958)],[-.06,-.035,-.07,-.055],[(0,1,2),(0,2,3)],index=3)

# Upper stepped crest. Each cube has six faces and independent editable volume.
cube(687,147,45,78,3,.085,depth_pixels=49)
cube(687,225,45,77,0,.085,depth_pixels=49)
for row in [(731,332,45,66,0,.122),(514,514,34,64,1,.005)]:cube(*row)
# One broad column follows the seven visible corners of the source. The old
# pair of narrow boxes overlapped in projection but exposed two thin ribs.
cream_block('Gold upper broad column',[(618,348),(688,310),(731,332),(731,470),(658,508),(618,486),(658,370)],[-.04,.0839,.0864,.0864,-.0434,-.04,-.0434],index=0)
cube(650,250,38,78,3,.02,depth_pixels=74)
cube(650,328,38,40,0,.02,depth_pixels=74)
# Source-visible gold courses around the raised cream spine. These are full
# blocks, with their front corners and heights measured from the concept.
for row in [(578,315,38,57,0,-.005),(545,376,44,73,0,.04),(479,516,47,60,0,.03),(442,615,48,88,0,.02)]:cube(*row)
cube(657,471,42,85,0,.015,depth_pixels=64)
cube(735,395,38,72,1,.16)
cube(531,814,43,85,0,.015,depth_pixels=69)
cube(490,461,30,63,0,.015,depth_pixels=27)
# Broad angular gold ledges along the bolt's right edge. Their contours follow
# the large painted facet boundaries instead of arbitrary triangulation.
relief('Gold upper diagonal ledge',[(658,509),(735,468),(782,469),(831,433),(848,432),(889,450),(887,507),(874,527),(874,570),(835,600),(830,628),(787,598),(721,569),(721,556),(658,556),(724,512),(801,510),(863,469),(803,557)],[-.03,.075,.08,.15,.17,.12,.12,.10,.10,.06,.06,-.03,-.03,-.03,-.03,-.03,-.03,.075,-.03],[(0,1,2,3,4,5,17,16,15),(17,5,6,7),(16,17,7,18),(18,7,8,9),(18,9,10,11),(15,16,18,11,12),(0,15,12,13,14)],boundary_count=15)
relief('Gold middle bevel',[(721,569),(787,598),(816,628),(778,661),(778,701),(734,719),(689,698),(718,644),(756,665)],[-.03,-.03,.10,.10,.10,.015,.015,-.03,-.03],[(0,1,8,7),(7,8,5,6),(1,2,3,8),(8,3,4,5)],boundary_count=8)
relief('Gold lower bevel',[(689,698),(734,719),(778,701),(778,740),(746,779),(715,800),(677,815),(657,791),(658,740),(711,766)],[.015,.015,.09,.09,.09,.045,-.035,-.035,-.035,-.035],[(0,1,9,8),(8,9,6,7),(9,1,2,3,4),(9,4,5,6)],boundary_count=9)
relief('Gold tip shoulder',[(657,791),(677,815),(705,827),(704,867),(660,891),(624,909),(611,918),(576,940),(550,920),(616,825),(658,848),(615,891)],[-.035,-.035,.06,.06,.06,.025,0,-.02,-.05,-.07,-.07,-.07],[(0,1,10,9),(10,1,2,3,4),(9,10,11),(10,4,5,6,11),(9,11,6,7,8)],boundary_count=10)
# Slate cloud accents wrap around the lightning, with inferred unseen backs.
for row in [(416,331,47,56,5,-.04),(416,387,47,57,6,-.04),(463,415,38,53,5,.015),(367,494,47,77,5,-.06),(416,476,40,62,6,0),(780,296,45,57,5,.182),(780,353,30,52,6,.182),(382,768,49,76,5,-.06),(430,741,45,53,6,-.02),(938,571,47,72,5,.13),(889,638,62,47,5,.105),(875,681,45,90,6,.065),(804,741,42,75,6,.12),(736,906,45,62,6,.06),(689,880,45,51,6,.12),(807,848,30,36,7,.16),(780,800,44,70,6,.12),(736,842,45,64,6,.06)]:cube(*row)
for row in [(481,235,30,33,0),(865,353,32,36,0),(951,425,27,30,0),(255,620,31,37,0),(335,674,28,28,0),(394,910,24,26,0),(904,821,28,30,0),(276,438,44,54,3),(984,715,47,70,3),(694,1014,33,39,4)]:cube(*row,x=.04,spark=True)

# Storm uses uniform palette cells, so sample their centers. Per-triangle UV
# rectangles were extrapolated outside the cell by bevels on narrow facets,
# making isolated gold triangles sample slate or background palette entries.
for ob in a.parts:
    index=ob['palette_index'];center=((index%8+.5)/8,(index//8+.5)/8)
    for loop in ob.data.uv_layers.active.data:loop.uv=center

focus_z=(origin_v-627)*unit/math.cos(el);focus=(0,0,focus_z)
a.studio(focus,(-7/math.sqrt(2),-7/math.sqrt(2),focus_z+7*math.tan(el)),1.5048)
s=a.scene;s.render.resolution_x=s.render.resolution_y=1254;s.cycles.samples=72
s['reference_focus']=focus;s['reference_elevation_deg']=30
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=-.1
for o in s.objects:
    if o.type=='LIGHT' and o.name.startswith('Key'):
        o.location=(-5,-3,7);o.rotation_euler=(Vector(focus)-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=700;o.data.color=(1,.98,.95)
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'revision':'r32_broad_upper_gold_column','source':s['concept'],'source_sha256':hashlib.sha256((ROOT/s['concept']).read_bytes()).hexdigest(),'method':'A broad eight-corner gold column replaces two narrow overlapping crest boxes. Adjoining gold and cloud blocks are connected in depth, and the hidden core shoulder is narrowed to prevent protrusion through the visible column. Raised cream hexahedra reconstructed from visible corners, a broad faceted cream crossbar and angled lower cream solids, stepped gold body, four gold edge volumes rebuilt from measured ledge and bevel boundaries and closed with depth that tapers to their shared silhouette, connected cloud clusters, and ten detached source sparks. Reference elevation and cube seam anchors corrected to 30 degrees. A connected faceted rear ridge follows the cream spine and tapers into the lower gold wedge. Lower cream backs terminate closer to the visible surfaces. Uniform palette cells are sampled at their centers to prevent bevel UVs from wrapping into other colors. Pigment and roughness atlases shade actual geometry; source artwork is not projected onto the mesh.','inferred':'Depth, backs, cloud connections and lighting are inferred from one concept view.','status':'pending_export_and_visual_refinement','accepted_fidelity':False},indent=2))
result={'asset':'Storm','parts':len(a.parts),'sparks':sum(bool(o.get('detached_reference_feature')) for o in a.parts)}





