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
az=math.radians(45);el=math.radians(25);unit=.0012;origin_v=1160

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
prism('Cream lightning ridge',cream,-.055,.085,3)

def cube(u,v,w,h,index,x=.04,spark=False,depth_pixels=None):
    v-=w*.5
    width=w*unit/math.cos(az);height=h*unit/math.cos(el)
    depth=(depth_pixels if depth_pixels is not None else w)*unit/math.cos(az)
    # Reference rectangle measures the right visible face from its left seam.
    uc=u+w/2;vc=v+h/2
    y=(math.cos(az)*x-(uc-627)*unit)/math.sin(az)
    z=((origin_v-vc)*unit-math.sin(el)*(math.sin(az)*x+math.cos(az)*y))/math.cos(el)
    join=.002 if not spark else 0
    o=a.box('Spark' if spark else ('Cloud cube' if index>=5 else 'Lightning cube'),(x,y+depth/2,z),(width+join,depth+join,height+join),index,.0015)
    if index<5:o.data.materials[0]=bolt
    o['reference_rect']=[u,v,w,h];o['palette_index']=index
    if spark:o['detached_reference_feature']=True
    return o

def relief(label,outline,depths,patches,thickness=.12):
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
    matrix=np.vstack((np.eye(len(outline)),np.array(constraints)*1000))
    depths=np.linalg.lstsq(matrix,np.concatenate((np.array(depths),np.zeros(len(constraints)))),rcond=None)[0].tolist()
    front=[point(u,v,x) for (u,v),x in zip(outline,depths)]
    back_shift=Vector((thickness,thickness,-math.sqrt(2)*math.tan(el)*thickness))
    n=len(front);rear=[p+back_shift for p in front]
    faces=[]
    for patch in patches:
        # Triangulate within each deliberate facet, not across the whole ledge.
        poly=[front[i] for i in patch]
        for triangle in tessellate_polygon([poly]):
            faces.append(tuple(patch[p] if isinstance(p,int) else min(patch,key=lambda j:(front[j]-p).length_squared) for p in triangle))
    faces += [tuple(i+n for i in reversed(face)) for face in list(faces)]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=a.solid(label,[tuple(p) for p in front+rear],faces,0,material=bolt,bevel=.0015)
    ob['reference_outline']=json.dumps(outline);ob['sculpted_facet_depths']=depths
    return ob

# Upper stepped crest. Each cube has six faces and independent editable volume.
for row in [(687,149,45,73,3,.085),(687,222,45,73,0,.085),(731,332,45,66,0,.02),(690,353,42,135,0,.02),(650,370,42,135,0,.0),(514,514,34,64,1,.005)]:cube(*row)
cube(650,259,38,74,3,.02,depth_pixels=74)
cube(650,333,38,35,0,.02,depth_pixels=74)
# Source-visible gold courses around the raised cream spine. These are full
# blocks, with their front corners and heights measured from the concept.
for row in [(578,315,38,57,0,-.005),(545,380,44,73,0,-.025),(482,481,38,63,0,-.025),(479,557,47,60,0,-.025),(442,615,48,88,0,-.025),(531,814,43,85,0,-.025)]:cube(*row)
cube(657,471,42,85,0,.015,depth_pixels=64)
cube(735,403,38,92,1,.06)
# Broad angular gold ledges along the bolt's right edge. Their contours follow
# the large painted facet boundaries instead of arbitrary triangulation.
relief('Gold upper diagonal ledge',[(658,509),(724,512),(801,510),(843,433),(869,454),(852,554),(811,586),(778,650),(748,648),(721,591),(686,590),(658,558)],[-.005,-.055,-.03,.02,.02,.015,-.005,.015,-.035,-.055,-.01,-.005],[(0,1,9,10,11),(1,2,6,8,9),(2,3,4,5,6),(6,7,8)])
relief('Gold middle bevel',[(721,591),(750,610),(777,650),(714,748),(658,771),(678,699)],[-.055,-.025,.025,.02,-.04,-.045],[(0,1,5),(1,2,3,4,5)])
relief('Gold lower bevel',[(658,771),(713,747),(730,765),(701,816),(669,842),(627,828),(602,810)],[-.045,-.01,.025,.005,.015,-.015,-.045],[(0,1,2,3,5,6),(3,4,5)])
relief('Gold tip shoulder',[(602,810),(627,828),(669,842),(650,876),(611,918),(576,940),(550,920)],[-.045,-.02,.02,.01,.025,-.01,-.045],[(0,1,5,6),(1,2,3,4,5)])
# Slate cloud accents wrap around the lightning, with inferred unseen backs.
for row in [(416,331,47,56,5,-.04),(416,387,47,57,6,-.04),(463,415,38,53,5,.015),(367,494,47,77,5,-.06),(416,476,40,62,6,0),(780,296,45,57,5,.08),(780,353,30,52,6,.08),(382,768,49,76,5,-.05),(430,741,45,53,6,-.01),(938,571,47,72,5,.14),(889,638,62,47,5,.115),(875,681,45,90,6,.075),(804,741,42,75,6,.12),(736,906,45,62,6,.06),(689,880,45,51,6,.12),(807,848,30,36,7,.16),(780,800,44,70,6,.12),(736,842,45,64,6,.06)]:cube(*row)
for row in [(481,235,30,33,0),(865,353,32,36,0),(951,425,27,30,0),(255,620,31,37,0),(335,674,28,28,0),(394,910,24,26,0),(904,821,28,30,0),(276,438,44,54,3),(984,715,47,70,3),(694,1014,33,39,4)]:cube(*row,x=.04,spark=True)

focus_z=(origin_v-627)*unit/math.cos(el);focus=(0,0,focus_z)
a.studio(focus,(-7/math.sqrt(2),-7/math.sqrt(2),focus_z+7*math.tan(el)),1.5048)
s=a.scene;s.render.resolution_x=s.render.resolution_y=1254;s.cycles.samples=72
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=-.1
for o in s.objects:
    if o.type=='LIGHT' and o.name.startswith('Key'):
        o.location=(-5,-3,7);o.rotation_euler=(Vector(focus)-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=700;o.data.color=(1,.98,.95)
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'revision':'r11_stepped_body_and_gold_facets','source':s['concept'],'source_sha256':hashlib.sha256((ROOT/s['concept']).read_bytes()).hexdigest(),'method':'Upper backing sheet removed and replaced by complete stepped gold blocks, four sculpted diagonal gold solids with deliberate planar facet boundaries, connected crest and cloud clusters, and ten detached source sparks. Pigment and roughness atlases shade actual geometry; source artwork is not projected onto the mesh.','inferred':'Depth, backs, cloud connections and lighting are inferred from one concept view.','status':'pending_export_and_visual_refinement','accepted_fidelity':False},indent=2))
result={'asset':'Storm','parts':len(a.parts),'sparks':sum(bool(o.get('detached_reference_feature')) for o in a.parts)}
