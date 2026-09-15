"""Solid voxel Ember wave, measured from the supplied single-view concept."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset,linear
# Uniform per-block pigment; highlights are separate solid colored blocks.
P=[('ef5424',.48,0),('dd4518',.52,0),('ff7920',.44,0),('fa9816',.43,0),
   ('ffb52c',.40,0),('ffd55a',.38,0),('fff0ba',.36,0),('f7ddb0',.40,0)]
class EmberAsset(PaletteAsset):
    def make_material(self):
        super().make_material()
        im=self.images[0];colors=[[linear(int(h[j:j+2],16)/255) for j in [0,2,4]]+[1] for h,_,_ in self.palette]
        pixels=[]
        for y in range(512):
            for x in range(512):pixels.extend(colors[min(y//64*8+x//64,len(colors)-1)])
        im.pixels.foreach_set(pixels);im.save();im.pack()
a=EmberAsset('Ember','ember.png',P)
a.material.name='M_Ember_Flame';bs=a.material.node_tree.nodes.get('Principled BSDF')
bs.inputs['Metallic'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.5
az=math.radians(45);el=math.radians(25);unit=.0012;origin_v=1160
def block(u,v,w,h,index,depth=None,y=0):
    depth=depth or w*unit/math.cos(az)
    # Invert the reference camera only to position the solid cube fronts.
    # No source-image projection or image geometry is included in the model.
    y-=len(a.parts)*.000025
    x=((u+w/2-627)*unit+math.sin(az)*y)/math.cos(az)
    z=((origin_v-v-h/2)*unit-math.sin(el)*math.sin(az)*x-math.sin(el)*math.cos(az)*y)/math.cos(el)
    ob=a.box('Flame block',(x,y+depth/2,z),(w*unit/math.cos(az)+.014,depth,h*unit/math.cos(el)+.012),index,.004)
    ob['reference_rect']=[u,v,w,h];ob['palette_index']=index;return ob
# Rectified front-face extents: their upper/lower edges gain the reference's
# isometric slope from the camera. Each entry becomes a complete cuboid.
rows=[
 (115,[(653,47,60,0)]),
 (175,[(653,47,62,1)]),
 (193,[(596,51,61,0)]),
 (256,[(596,48,67,1),(692,27,69,1)]),
 (278,[(644,48,60,0)]),
 (319,[(550,48,64,0),(598,47,65,2)]),
 (350,[(690,49,72,0),(739,46,72,1)]),
 (374,[(509,49,70,1),(598,47,68,3),(645,45,67,2)]),
 (435,[(509,49,78,1),(557,43,68,2),(598,47,66,3),(645,47,69,3),(692,47,81,2),(739,46,70,1)]),
 (498,[(603,48,63,4),(557,46,65,3)]),
 (550,[(739,49,59,2),(787,43,59,1),(909,46,79,0)]),
 (512,[(909,46,64,0)]),
 (525,[(462,47,63,0),(510,48,65,2)]),
 (564,[(603,48,58,4),(557,46,62,3),(651,44,61,3),(695,44,64,2)]),
 (590,[(462,47,71,1)]),
 (612,[(336,47,74,0),(522,46,69,4),(649,48,69,5),(869,46,62,2)]),
 (672,[(381,48,73,0),(462,47,50,1),(522,46,76,3),(569,36,38,3),(649,48,41,4),(696,60,23,3),(803,46,72,2),(869,46,49,1)]),
 (628,[(741,46,36,2)]),
 (698,[(471,48,66,4),(610,49,75,6),(706,49,69,4),(962,47,62,0)]),
 (746,[(289,49,89,0),(381,48,53,2),(429,43,37,3),(518,51,45,3),(569,42,44,4),(849,44,66,2)]),
 (777,[(462,46,67,4),(565,45,74,7),(674,39,74,6),(754,49,60,4)]),
 (805,[(933,37,65,1),(962,47,69,0)]),
 (835,[(289,49,70,0),(374,41,61,4),(462,46,54,3),(514,45,72,7),(619,46,69,6),(674,39,32,5),(754,49,57,3),(849,44,59,2)]),
 (883,[(714,45,54,6),(888,46,58,0),(933,37,55,1),(962,47,40,1)]),
 (897,[(374,41,60,3),(414,48,40,3),(514,45,42,6),(619,46,50,6),(754,49,66,3),(803,44,47,2),(849,39,53,1)]),
 (952,[(330,44,58,0),(374,41,58,0),(418,46,75,0),(515,44,70,3),(578,46,61,6),(626,40,51,4),(669,45,61,6),(717,37,57,3),(754,49,67,2)]),
 (981,[(827,49,62,0),(876,49,75,1),(925,44,38,1)]),
 (1018,[(515,45,41,2),(560,23,52,2),(626,41,24,3),(714,44,42,2)]),
 (1043,[(466,49,80,0),(626,40,41,5),(781,46,73,0),(828,49,64,1)]),
 (1070,[(560,32,63,0),(671,47,57,1),(717,26,42,1)]),
 (1093,[(626,46,58,0)])
]
for v,cells in rows:
    for u,w,h,index in cells:
        relief=-.06 if index in [6,7] else -.025 if index in [4,5] else 0 if index==3 else .015
        block(u,v,w,max(h,62),index,y=relief,depth=.13 if index in [3,4,5,6,7] else None)
# Missing orange courses join the side tongues into the flame body.
for u,v,w,h,index in [(335,870,39,68,0),(803,744,46,68,2),(962,760,47,66,1),(849,949,44,53,0)]:block(u,v,w,h,index,y=.015)
# Four detached solid embers are intentional reference features, not missing
# connections in the flame body. They share its same physical block material.
for u,v,w,h in [(429,304,29,31),(801,251,27,29),(391,475,41,44),(857,397,40,43)]:
    ob=block(u,v,w,h,2,y=.01);ob['part']='Floating ember';ob['detached_reference_feature']=True
from ember_interior import close_interior
close_interior(a)
focus_z=(origin_v-627)*unit/math.cos(el);focus=(0,0,focus_z)
a.studio(focus,(-7*math.sin(az),-7*math.cos(az),focus_z+7*math.tan(el)),1.5048)
s=a.scene;s.render.resolution_x=1254;s.render.resolution_y=1254;s.cycles.samples=72
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=-.1
for ob in s.objects:
    if ob.type=='LIGHT' and ob.name.startswith('Key'):ob.data.energy=700;ob.data.color=(1,.98,.95)
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'source':s['concept'],'method':'Measured beveled flame cuboids with raised yellow/cream core and four detached solid sparks. No source-image projection.','inferred':'Rear volume and hidden block arrangement inferred from one view. Sparks are static stylized floating geometry; no particle simulation or gameplay behavior.','status':'pending_studio_and_engine_review'},indent=2))
result={'asset':a.key,'parts':len(a.parts),'scene':s.name}
