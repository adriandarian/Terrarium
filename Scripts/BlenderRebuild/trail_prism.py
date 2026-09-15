"""Stepped amber crystal with embedded light and a four-corner bronze cage."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector,Matrix
root=Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset
P=[('d7b438',.065,0),('eac84e',.065,0),('f4d772',.075,0),('f9e393',.065,0),
   ('d9ba4b',.08,0),('f1cf59',.065,0),('fff4b1',.12,1),('fff9d2',.12,1),
   ('846a2c',.3,0),('695923',.34,0),('9b7c34',.27,0),('b79543',.24,0),
   ('eac145',.18,0),('cca23a',.22,0)]
a=PaletteAsset('TrailPrism','trail_prism.png',P)
crystal=a.shader('Crystal',transmission=.82,ior=1.12)
crystal.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.2
core=a.shader('Core',emission=1.5)

def ring(width,z,divisions=8):
    h=width/2;corners=[Vector((-h,-h,z)),Vector((h,-h,z)),Vector((h,h,z)),Vector((-h,h,z))]
    return [tuple(corners[side].lerp(corners[(side+1)%4],j/divisions)) for side in range(4) for j in range(divisions)]
def stepped_volume(label,profile,material,index,divisions=8,mosaic=False):
    count=divisions*4;verts=[v for width,z in profile for v in ring(width,z,divisions)];faces=[];cells=[]
    faces.append(tuple(range(count-1,-1,-1)));cells.append(index)
    for row in range(len(profile)-1):
        for j in range(count):
            faces.append((row*count+j,row*count+(j+1)%count,(row+1)*count+(j+1)%count,(row+1)*count+j))
            cells.append((row*3+j*7+j//3)%6 if mosaic else index)
    faces.append(tuple((len(profile)-1)*count+j for j in range(count)));cells.append(index)
    return a.solid(label,verts,faces,index,material,.0012,cells)

profile=[(.055,.0),(.055,.048),(.12,.048),(.12,.11),(.195,.11),(.195,.18),(.27,.18),(.27,.25),(.35,.25),(.39,.325),(.45,.325),(.51,.42),(.59,.45),(.59,.53),(.50,.64),(.50,.675),(.41,.675),(.41,.77),(.33,.77),(.33,.865),(.25,.865),(.25,.955),(.145,.955),(.145,1.035),(.067,1.035),(.067,1.12)]
# Raise the equator while retaining the tall upper tip and the lower stepped tail.
def raised(z):return z*.565/.465 if z<=.465 else .565+(z-.465)*(.555/.655)
profile=[(w,raised(z)) for w,z in profile]
body=stepped_volume('Continuous stepped amber crystal',profile,crystal,1,4,True)
body['physical_volume']='solid crystal with emissive inclusion'
inner=[(.18,.43),(.18,.45),(.25,.45),(.25,.515),(.18,.515),(.18,.605),(.10,.605),(.10,.69),(.052,.69),(.052,.75)]
stepped_volume('Luminous stepped inclusion',[(w*1.08,raised(z)) for w,z in inner],core,6,4)

# Four load-bearing metal rails meet four stepped corner clamps.
for sign in [-1,1]:
    for i in range(3):
        a.box('Bronze frame front rail',((i-1)*.17,sign*.31,.565),(.17,.045,.085),8 if i else 10,.0023)
        a.box('Bronze frame side rail',(sign*.31,(i-1)*.17,.565),(.045,.17,.085),9 if i else 8,.0023)
    for i in range(6):
        a.box('Upper gold rail seam',((i-2.5)*.08,sign*.308,.613),(.08,.018,.012),11,.001)
        a.box('Upper gold side seam',(sign*.308,(i-2.5)*.08,.613),(.018,.08,.012),11,.001)

for sx in [-1,1]:
    for sy in [-1,1]:
        center=Vector((sx*.32,sy*.32,.56));outward=Vector((sx,sy,0)).normalized()
        # Orthogonal L-shaped rows wrap both faces; every corner has actual depth.
        for row,length in enumerate([1,2,3,3,2]):
            z=center.z+(row-2)*.045
            for col in range(length):
                x=sx*(.34-col*.075);y=sy*.34
                a.box('Corner clamp X arm',(x,y,z),(.075,.068,.045),[9,8,8,10,8][row],.0015)
                if col:
                    a.box('Corner clamp Y arm',(sx*.34,sy*(.34-col*.075),z),(.068,.075,.045),[9,8,8,10,8][row],.0015)
        a.box('Top clamp peg',center+Vector((0,0,.138)),(.067,.067,.052),10,.0025)
        a.box('Lower clamp foot',center+Vector((0,0,-.125)),(.07,.07,.046),9,.0025)
        pos=center+outward*.062
        a.box('Golden corner stud',pos,(.065,.065,.065),12,.0032)
        # Solid metal corner under the decorative stepped front secures both rails.
        a.box('Corner rail junction',center,(.075,.075,.115),9,.002)

# The reference is a tall narrow bipyramid, with broad corner escutcheons.
for ob in a.parts:
    ob.location.x*=.70;ob.location.y*=.70
    ob.scale.x*=.70;ob.scale.y*=.70
a.studio((0,0,.57),(5,-5,4.0),1.30)
a.scene.render.resolution_x=1254;a.scene.render.resolution_y=1254
a.scene.cycles.samples=96;a.scene.cycles.transmission_bounces=12
for ob in a.scene.objects:
    if ob.type=='LIGHT':
        if ob.name.startswith('Key'):ob.data.energy=1300
        elif ob.name.startswith('Fill'):ob.data.energy=250
data=bpy.data.lights.new('Cool reflected light','AREA');data.energy=160;data.color=(.08,.7,1);data.size=3
light=bpy.data.objects.new('Cool reflected light',data);a.scene.collection.objects.link(light);light.location=(4,1,-.3);light.rotation_euler=(Vector((0,0,.45))-light.location).to_track_quat('-Z','Y').to_euler()
a.scene['fidelity_status']='raised_equator_wrapped_clamps_pending_reference_comparison';a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'source':'SourceAssets/Voxel/trail_prism.png','interpretation':'Stepped solid amber bipyramid with a separate luminous inclusion and four bronze corner clamps. Unseen rear repeats the four-sided cage. No flat icon plane.','materials':['Crystal','Core','Frame'],'status':'pending_render_and_engine_review'},indent=2))
result={'asset':a.key,'parts':len(a.parts),'scene':a.scene.name}
