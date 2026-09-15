"""Author Storm as a solid lightning extrusion, cloud blocks and separate sparks."""
import bpy,sys,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
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
    rear=[p+Vector((depth,0,0)) for p in front];n=len(front)
    # Concave caps are explicitly triangulated; the side walls close the volume.
    triangles=tessellate_polygon([front])
    def idx(p):return p if isinstance(p,int) else min(range(n),key=lambda i:(front[i]-p).length_squared)
    cap=[tuple(idx(p) for p in tri) for tri in triangles]
    faces=cap+[tuple(i+n for i in reversed(t)) for t in cap]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=a.solid(label,[tuple(p) for p in front+rear],faces,index,material=bolt,bevel=.002)
    o['reference_outline']=json.dumps(outline);o['physical_depth_m']=depth
    return o

gold=[(545,317),(651,290),(776,310),(776,383),(731,411),(734,495),(817,446),(850,433),(869,454),(854,553),(810,604),(797,657),(746,692),(714,766),(665,814),(653,871),(602,918),(601,1003),(510,1104),(480,1122),(460,1114),(459,958),(473,903),(442,884),(442,788),(479,768),(479,698),(392,702),(392,580),(432,554),(432,493),(469,477),(470,445),(500,429),(501,354),(539,335)]
cream=[(555,338),(618,359),(618,440),(547,468),(547,582),(687,590),(602,810),(548,918),(532,981),(482,957),(511,864),(531,811),(545,783),(545,653),(441,654),(441,591),(477,574),(490,460),(547,434)]
# The upper body is built from complete stepped blocks below, so remove the
# old sheet behind them. Keep the lower angular core below this shoulder line.
clipped=[]
for start,end in zip(gold,gold[1:]+gold[:1]):
    inside_a=start[1]>=440;inside_b=end[1]>=440
    if inside_a:clipped.append(start)
    if inside_a!=inside_b:
        t=(440-start[1])/(end[1]-start[1]);clipped.append((start[0]+t*(end[0]-start[0]),440))
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

def relief(label,outline,depths,patches,thickness=.12,index=0,boundary_count=None):
    """Faceted solid with the source outline shared by front and inferred back.

    Unlike a sideways extrusion, the rear follows the viewing direction, so
    adding physical thickness cannot push the tip into a reference spark.
    Explicit face patches and varying corner depth sculpt the visible surface.
    """
    # Enforce planar artist-defined patches. This prevents triangulation from
    # adding spurious creases through a broad facet when four corners differ.
    constraints=[]
    for patch in patches:
        basis=np.array([[outline[i][0],outline[i][1],1] for i in patch[:3]],dtype=float).T
        for i in patch[3:]:
            weights=np.linalg.solve(basis,np.array([*outline[i],1],dtype=float))
            row=np.zeros(len(outline));row[i]=1
            for j,w in zip(patch[:3],weights):row[j]-=w
            constraints.append(row)
    matrix=np.vstack((np.eye(len(outline)),np.array(constraints).reshape((-1,len(outline)))*1000))
    depths=np.linalg.lstsq(matrix,np.concatenate((np.array(depths),np.zeros(len(constraints)))),rcond=None)[0].tolist()
    front=[point(u,v,x) for (u,v),x in zip(outline,depths)]
    back_shift=Vector((thickness,thickness,-math.sqrt(2)*math.tan(el)*thickness))
    n=len(front)
    # Cream wedge backs terminate within the gold core's rear plane. A uniform
    # offset of the sculpted front made a white duplicate poke through the back.
    rear=[point(u,v,.075) for u,v in outline] if index==3 else [p+back_shift for p in front]
    faces=[]
    for patch in patches:
        # Triangulate within each deliberate facet, not across the whole ledge.
        poly=[front[i] for i in patch]
        for triangle in tessellate_polygon([poly]):
            faces.append(tuple(patch[p] if isinstance(p,int) else min(patch,key=lambda j:(front[j]-p).length_squared) for p in triangle))
    faces += [tuple(i+n for i in reversed(face)) for face in list(faces)]
    boundary_count=boundary_count or n
    faces += [(i,(i+1)%boundary_count,(i+1)%boundary_count+n,i+n) for i in range(boundary_count)]
    ob=a.solid(label,[tuple(p) for p in front+rear],faces,index,material=bolt,bevel=.0015)
    ob['reference_outline']=json.dumps(outline);ob['sculpted_facet_depths']=depths
    return ob

def cream_block(label,outline,depths):
    """Seven visible corners complete a real eight-corner block.

    The three visible faces share corner 6. Infer the hidden corner from the
    three opposite-face completions, instead of extruding those visible faces
    and introducing a second, oversized block behind them.
    """
    p=[point(u,v,x) for (u,v),x in zip(outline,depths)]
    hidden=((p[1]+p[4]-p[6])+(p[3]+p[0]-p[6])+(p[5]+p[2]-p[6]))/3
    ob=a.solid(label,[tuple(v) for v in p+[hidden]],[(0,1,2,6),(0,6,4,5),(6,2,3,4),(0,5,7,1),(1,7,3,2),(3,7,5,4)],3,material=bolt,bevel=.0015)
    ob['reference_outline']=json.dumps(outline);ob['inferred_hidden_corner']=list(hidden)
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
for row in [(731,332,45,66,0,.02),(690,353,42,135,0,.02),(650,370,42,135,0,.0),(514,514,34,64,1,.005)]:cube(*row)
cube(650,250,38,78,3,.02,depth_pixels=74)
cube(650,328,38,40,0,.02,depth_pixels=74)
# Source-visible gold courses around the raised cream spine. These are full
# blocks, with their front corners and heights measured from the concept.
for row in [(578,315,38,57,0,-.005),(545,376,44,73,0,.04),(479,516,47,60,0,.03),(442,615,48,88,0,.02)]:cube(*row)
cube(657,471,42,85,0,.015,depth_pixels=64)
cube(735,403,38,92,1,.06)
cube(531,814,43,85,0,.015,depth_pixels=69)
cube(490,461,30,63,0,.015,depth_pixels=27)
# Broad angular gold ledges along the bolt's right edge. Their contours follow
# the large painted facet boundaries instead of arbitrary triangulation.
relief('Gold upper diagonal ledge',[(658,509),(724,512),(801,510),(843,433),(869,454),(852,554),(811,586),(778,650),(748,648),(721,578),(687,556),(658,556)],[-.005,-.055,-.03,.02,.02,.015,-.005,.015,-.035,-.055,-.01,-.005],[(0,1,9,10,11),(1,2,6,8,9),(2,3,4,5,6),(6,7,8)])
relief('Gold middle bevel',[(721,591),(750,610),(777,650),(714,748),(658,771),(678,699)],[-.055,-.025,.025,.02,-.04,-.045],[(0,1,5),(1,2,3,4,5)])
relief('Gold lower bevel',[(658,771),(713,747),(730,765),(701,816),(669,842),(627,828),(602,810)],[-.045,-.01,.025,.005,.015,-.015,-.045],[(0,1,2,3,5,6),(3,4,5)])
relief('Gold tip shoulder',[(602,810),(627,828),(669,842),(650,876),(611,918),(576,940),(550,920)],[-.045,-.02,.02,.01,.025,-.01,-.045],[(0,1,5,6),(1,2,3,4,5)])
# Slate cloud accents wrap around the lightning, with inferred unseen backs.
for row in [(416,331,47,56,5,-.04),(416,387,47,57,6,-.04),(463,415,38,53,5,.015),(367,494,47,77,5,-.06),(416,476,40,62,6,0),(780,296,45,57,5,.08),(780,353,30,52,6,.08),(382,768,49,76,5,-.06),(430,741,45,53,6,-.02),(938,571,47,72,5,.14),(889,638,62,47,5,.115),(875,681,45,90,6,.075),(804,741,42,75,6,.12),(736,906,45,62,6,.06),(689,880,45,51,6,.12),(807,848,30,36,7,.16),(780,800,44,70,6,.12),(736,842,45,64,6,.06)]:cube(*row)
for row in [(481,235,30,33,0),(865,353,32,36,0),(951,425,27,30,0),(255,620,31,37,0),(335,674,28,28,0),(394,910,24,26,0),(904,821,28,30,0),(276,438,44,54,3),(984,715,47,70,3),(694,1014,33,39,4)]:cube(*row,x=.04,spark=True)

focus_z=(origin_v-627)*unit/math.cos(el);focus=(0,0,focus_z)
a.studio(focus,(-7/math.sqrt(2),-7/math.sqrt(2),focus_z+7*math.tan(el)),1.5048)
s=a.scene;s.render.resolution_x=s.render.resolution_y=1254;s.cycles.samples=72
s['reference_focus']=focus;s['reference_elevation_deg']=30
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=-.1
for o in s.objects:
    if o.type=='LIGHT' and o.name.startswith('Key'):
        o.location=(-5,-3,7);o.rotation_euler=(Vector(focus)-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=700;o.data.color=(1,.98,.95)
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'revision':'r18_cream_blocks_and_facets','source':s['concept'],'source_sha256':hashlib.sha256((ROOT/s['concept']).read_bytes()).hexdigest(),'method':'Raised cream hexahedra reconstructed from visible corners, a broad faceted cream crossbar and angled lower cream solids, stepped gold body, four sculpted gold edge solids, connected cloud clusters, and ten detached source sparks. Reference elevation and cube seam anchors corrected to 30 degrees. Pigment and roughness atlases shade actual geometry; source artwork is not projected onto the mesh.','inferred':'Depth, backs, cloud connections and lighting are inferred from one concept view.','status':'pending_export_and_visual_refinement','accepted_fidelity':False},indent=2))
result={'asset':'Storm','parts':len(a.parts),'sparks':sum(bool(o.get('detached_reference_feature')) for o in a.parts)}
