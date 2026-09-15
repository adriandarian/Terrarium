"""Solid voxel Tide wave, measured from the supplied single-view concept."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset,linear
# Uniform per-block pigment; highlights are separate solid colored blocks.
P=[('075a8c',.52,0),('0875ab',.48,0),('1095be',.43,0),('20b9c6',.42,0),
   ('52cbd0',.39,0),('9fdee0',.36,0),('c3e7df',.38,0),('287ca9',.46,0)]
class TideAsset(PaletteAsset):
    def make_material(self):
        super().make_material()
        im=self.images[0];colors=[[linear(int(h[j:j+2],16)/255) for j in [0,2,4]]+[1] for h,_,_ in self.palette]
        pixels=[]
        for y in range(512):
            for x in range(512):pixels.extend(colors[min(y//64*8+x//64,len(colors)-1)])
        im.pixels.foreach_set(pixels);im.save();im.pack()
a=TideAsset('Tide','tide.png',P)
a.material.name='M_Tide_Wave';bs=a.material.node_tree.nodes.get('Principled BSDF')
bs.inputs['Metallic'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.5
az=math.radians(25);el=math.radians(12);unit=.0012;origin_v=1145
def block(u,v,w,h,index,depth=.08,y=0):
    # Invert the reference camera only to position the solid cube fronts.
    # No source-image projection or image geometry is included in the model.
    y-=len(a.parts)*.000025
    x=((u+w/2-627)*unit+math.sin(az)*y)/math.cos(az)
    z=((origin_v-v-h/2)*unit-math.sin(el)*math.sin(az)*x-math.sin(el)*math.cos(az)*y)/math.cos(el)
    ob=a.box('Wave block',(x,y+depth/2,z),(w*unit/math.cos(az)+.003,depth,h*unit/math.cos(el)+.004),index,.004)
    ob['reference_rect']=[u,v,w,h];return ob
# v, followed by front rectangles (u,width,height,pigment). Slightly uneven
# courses preserve the hand-shaped reference, including the open curl.
rows=[
 (106,[(600,50,63,3)]),
 (165,[(601,67,59,5),(668,17,54,1)]),
 (219,[(568,34,44,1),(602,66,47,5),(668,44,47,2)]),
 (268,[(535,43,47,1),(578,50,55,5),(628,46,51,1),(674,41,48,1),(715,27,44,2)]),
 (323,[(492,43,50,2),(535,43,58,5),(578,47,55,1),(625,45,51,1),(670,44,45,1)]),
 (381,[(445,45,49,1),(490,40,58,5),(530,49,55,3),(579,47,51,1),(626,33,47,1),(659,31,39,0)]),
 (441,[(405,74,60,5),(479,51,55,3),(530,48,51,1),(578,48,47,0),(626,64,43,0)]),
 (454,[(706,49,29,4),(755,57,66,6),(812,47,69,6)]),
 (486,[(650,54,51,4),(704,55,49,5)]),
 (501,[(360,73,59,5),(433,46,55,3),(479,50,51,1),(529,50,49,0),(579,46,40,0)]),
 (538,[(577,73,56,5),(650,54,54,4),(704,55,50,3),(759,53,44,3)]),
 (523,[(812,49,58,5),(861,44,55,6)]),
 (561,[(334,49,52,1),(383,53,58,3),(436,42,48,1),(478,49,45,0),(527,50,39,0)]),
 (598,[(523,76,56,5),(599,50,52,2),(649,55,49,1),(704,54,46,1),(758,54,45,1)]),
 (622,[(315,75,57,3),(390,45,55,1),(435,43,50,0),(478,45,47,0)]),
 (587,[(812,45,48,3),(857,49,51,4),(906,35,47,6)]),
 (641,[(715,58,54,7),(773,53,56,0),(826,51,49,3),(877,62,48,3),(939,30,40,5)]),
 (657,[(503,76,47,7),(579,41,46,2),(620,29,42,0)]),
 (678,[(315,80,70,3),(395,44,58,1),(439,44,53,0),(483,20,43,0)]),
 (705,[(539,41,49,1),(580,23,47,1),(603,46,56,0)]),
 (697,[(746,80,51,0),(826,54,58,3),(880,55,61,3),(935,34,70,3),(969,37,59,5)]),
 (746,[(271,73,62,3),(344,52,66,3),(396,43,42,1),(439,44,38,0),(483,56,46,0)]),
 (754,[(774,53,50,0),(827,52,53,3),(879,55,54,3),(934,35,52,3),(969,37,58,4)]),
 (794,[(398,56,62,3),(454,58,62,3),(512,52,39,0),(564,56,34,1),(738,77,57,1),(815,51,62,1)]),
 (810,[(271,73,53,1),(344,54,49,1),(867,60,55,3),(927,43,52,3),(970,36,74,3)]),
 (856,[(294,53,63,1),(347,52,59,1),(399,57,47,3),(456,54,47,3),(510,53,25,1),(563,58,28,1),(621,61,27,1),(682,76,69,1),(758,56,50,1),(814,65,70,5),(879,48,68,3),(927,43,56,3)]),
 (905,[(348,54,65,1),(402,56,61,2),(458,52,51,3),(510,81,46,3),(591,54,30,1),(645,57,27,1),(759,73,64,5),(832,47,58,2),(879,48,62,3),(927,44,68,2)]),
 (927,[(703,56,42,1)]),
 (958,[(379,79,66,1),(458,51,59,1),(509,82,45,1),(592,57,40,1),(649,54,36,1),(703,56,42,1),(759,73,23,1),(832,47,75,2),(879,48,73,1)]),
 (993,[(706,71,56,5),(777,55,49,2)]),
 (1019,[(405,54,53,0),(459,61,59,1),(520,79,52,1),(599,54,33,0),(653,53,26,0)]),
 (1052,[(599,56,57,1),(655,63,52,1),(718,60,50,0),(778,49,45,0),(827,43,34,0)]),
 (1075,[(466,57,45,0),(523,57,57,0),(580,19,63,0)]),
 (1107,[(599,59,34,0),(658,54,31,0),(712,42,25,0),(754,49,18,0)])
]
for v,cells in rows:
    for u,w,h,index in cells:
        relief=.05 if v==454 and index==6 else -.025 if index in [3,4,5,6] else .012 if index in [0,1] else 0
        block(u,v,w,min(max(h,56),1142-v),index,depth=.073 if v<200 else .08,y=relief)
# Recessed solid courses close unintended seams without filling the curl.
for u,v,w,h in [(398,729,43,40),(441,725,49,43),(490,738,50,45)]:block(u,v,w,h,0,depth=.09,y=.035)
# The current low-cube samples drive counter placement checks.
bpy.context.view_layer.update()
support=[]
for ob in a.parts:
    support.append({'part':ob.name,'center_m':list(ob.location),'bottom_m':min((ob.matrix_world@v.co).z for v in ob.data.vertices)})
lowest=min(r['bottom_m'] for r in support)
support=[r for r in support if r['bottom_m']<lowest+.025]
(a.review/'base-support-source.json').write_text(json.dumps({'method':'Center samples of authored wave cubes within 2.5 cm of the lowest point, before placement scaling.','samples':support},indent=2))
focus_z=(origin_v-627)*unit/math.cos(el);focus=(0,0,focus_z)
a.studio(focus,(-7*math.sin(az),-7*math.cos(az),focus_z+7*math.tan(el)),1.5048)
s=a.scene;s.render.resolution_x=1254;s.render.resolution_y=1254;s.cycles.samples=72
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=-.1
for ob in s.objects:
    if ob.type=='LIGHT' and ob.name.startswith('Key'):ob.data.energy=700;ob.data.color=(1,.98,.95)
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'source':s['concept'],'method':'Individually measured solid beveled wave blocks with uniform blue/aqua pigments and an open curl. Original image is a reference only.','inferred':'Unseen rear surfaces and block depth are inferred from the single-view concept. No fluid simulation or gameplay behavior is implied.','status':'pending_studio_and_engine_review'},indent=2))
result={'asset':a.key,'parts':len(a.parts),'scene':s.name}
