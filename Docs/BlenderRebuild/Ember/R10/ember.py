"""Grounded solid flame columns and pigment blocks matched to Ember's source view."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset,linear
reference=json.loads((root/'Docs/BlenderRebuild/Ember/reference-sampling.json').read_text())
assert hashlib.sha256((root/'SourceAssets/Voxel/ember.png').read_bytes()).hexdigest()==reference['source_sha256']
for name,expected in reference['files'].items():assert hashlib.sha256((root/'Docs/BlenderRebuild/Ember'/name).read_bytes()).hexdigest()==expected
P = [('f56b30', 0.48, 0), ('e65b25', 0.52, 0), ('ff8528', 0.44, 0), ('fa9816', 0.43, 0), ('ffb52c', 0.4, 0), ('ffd55a', 0.38, 0), ('fff0ba', 0.36, 0), ('f7ddb0', 0.4, 0)]

class EmberAsset(PaletteAsset):

    def make_material(self):
        super().make_material()
        im = self.images[0]
        colors = [[linear(int(h[j:j + 2], 16) / 255) for j in [0, 2, 4]] + [1] for h, _, _ in self.palette]
        pixels = []
        for y in range(512):
            for x in range(512):
                pixels.extend(colors[min(y // 64 * 8 + x // 64, len(colors) - 1)])
        im.pixels.foreach_set(pixels)
        im.save()
        im.pack()

rows = [(115, [(653, 47, 60, 0)]), (175, [(653, 47, 62, 1)]), (193, [(596, 51, 61, 0)]), (256, [(596, 48, 67, 1), (692, 27, 69, 1)]), (278, [(644, 48, 60, 0)]), (319, [(550, 48, 64, 0), (598, 47, 65, 2)]), (350, [(690, 49, 72, 0), (739, 46, 72, 1)]), (374, [(509, 49, 70, 1), (598, 47, 68, 3), (645, 45, 67, 2)]), (435, [(509, 49, 78, 1), (557, 43, 68, 2), (598, 47, 66, 3), (645, 47, 69, 3), (692, 47, 81, 2), (739, 46, 70, 1)]), (498, [(603, 48, 63, 4), (557, 46, 65, 3)]), (550, [(739, 49, 59, 2), (787, 43, 59, 1), (909, 46, 79, 0)]), (512, [(909, 46, 64, 0)]), (525, [(462, 47, 63, 0), (510, 48, 65, 2)]), (564, [(603, 48, 58, 4), (557, 46, 62, 3), (651, 44, 61, 3), (695, 44, 64, 2)]), (590, [(462, 47, 71, 1)]), (612, [(336, 47, 74, 0), (522, 46, 69, 4), (649, 48, 69, 5), (869, 46, 62, 2)]), (672, [(381, 48, 73, 0), (462, 47, 50, 1), (522, 46, 76, 3), (569, 36, 38, 3), (649, 48, 41, 4), (696, 60, 23, 3), (803, 46, 72, 2), (869, 46, 49, 1)]), (628, [(741, 46, 36, 2)]), (698, [(471, 48, 66, 4), (610, 49, 75, 6), (706, 49, 69, 4), (962, 47, 62, 0)]), (746, [(289, 49, 89, 0), (381, 48, 53, 2), (429, 43, 37, 3), (518, 51, 45, 3), (569, 42, 44, 4), (849, 44, 66, 2)]), (777, [(462, 46, 67, 4), (565, 45, 74, 7), (674, 39, 74, 6), (754, 49, 60, 4)]), (805, [(933, 37, 65, 1), (962, 47, 69, 0)]), (835, [(289, 49, 70, 0), (374, 41, 61, 4), (462, 46, 54, 3), (514, 45, 72, 7), (619, 46, 69, 6), (674, 39, 32, 5), (754, 49, 57, 3), (849, 44, 59, 2)]), (883, [(714, 45, 54, 6), (888, 46, 58, 0), (933, 37, 55, 1), (962, 47, 40, 1)]), (897, [(374, 41, 60, 3), (414, 48, 40, 3), (514, 45, 42, 6), (619, 46, 50, 6), (754, 49, 66, 3), (803, 44, 47, 2), (849, 39, 53, 1)]), (952, [(330, 44, 58, 0), (374, 41, 58, 0), (418, 46, 75, 0), (515, 44, 70, 3), (578, 46, 61, 6), (626, 40, 51, 4), (669, 45, 61, 6), (717, 37, 57, 3), (754, 49, 67, 2)]), (981, [(827, 49, 62, 0), (876, 49, 75, 1), (925, 44, 38, 1)]), (1018, [(515, 45, 41, 2), (560, 23, 52, 2), (626, 41, 24, 3), (714, 44, 42, 2)]), (1043, [(466, 49, 80, 0), (626, 40, 41, 5), (781, 46, 73, 0), (828, 49, 64, 1)]), (1070, [(560, 32, 63, 0), (671, 47, 57, 1), (717, 26, 42, 1)]), (1093, [(626, 46, 58, 0)])]
a=EmberAsset('Ember','ember.png',P);a.material.name='M_Ember_Flame'
bs=a.material.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.5
az=math.radians(45);el=math.radians(25);unit=.0012;origin_v=1160;course=.084
bottoms=json.loads((root/'Docs/BlenderRebuild/Ember/source-column-bottoms.json').read_text())
pigments=json.loads((root/'Docs/BlenderRebuild/Ember/source-pigment-cells.json').read_text())
def block(u,v,w,h,index,spark=False):
    height=max(h,62)*unit/math.cos(el);width=w*unit/math.cos(az)
    if spark:height=h*unit/math.cos(el)
    uc=u+w/2;vc=v+(h if spark else max(h,62))/2
    if spark:
        y=.2
        x=((uc-627)*unit+math.sin(az)*y)/math.cos(az)
        z=((origin_v-vc)*unit-math.sin(el)*math.sin(az)*x-math.sin(el)*math.cos(az)*y)/math.cos(el)
        k=None
    else:
        k=max(0,int((bottoms[round(uc)]-vc-height*math.cos(el)/unit/2)/(course*math.cos(el)/unit)))
        k+=2 if index in [6,7] else 1 if index in [3,4,5] else 0
        relief=.025*((v>=770)+(v>=880)) if index in [6,7] else .025*(v>=740) if index in [3,4,5] else 0
        z=k*course+height/2+relief
        y=math.cos(az)/math.sin(el)*((origin_v-vc)*unit-math.cos(el)*z)-math.sin(az)*(uc-627)*unit
        x=((uc-627)*unit+math.sin(az)*y)/math.cos(az)
    ob=a.box('Floating ember' if spark else 'Flame cube',(x,y+width/2,z),(width+.008,width,height+.004),index,.003)
    ob['reference_rect']=[u,v,w,h];ob['palette_index']=index
    if spark:ob['detached_reference_feature']=True
    else:ob['course']=k
    return ob
for v,cells in rows:
    for u,w,h,index in cells:
        if (v,u) in {(498,557),(564,557)}:continue
        block(u,v-12,w,h+12,index) if (v,u)==(350,739) else block(u,v,w,h,index)
for u,v,w,h,index in [(335,870,39,68,0),(803,744,46,68,2),(962,760,47,66,1),(849,949,44,53,0),(574,885,44,64,7)]:block(u,v,w,h,index)
bpy.context.view_layer.update()
authored=list(a.parts);bounds=[]
for ob in authored:
    vs=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    bounds.append(([min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]))
filled=[]
for ob in authored:
    for k in range(ob['course']):
        center=Vector((ob.location.x,ob.location.y,k*course+course/2))
        if any(all(lo[j]-.005<center[j]<hi[j]+.005 for j in range(3)) for lo,hi in bounds):continue
        if any((center-c).length<.035 for c in filled):continue
        face=Vector((center.x,center.y-ob.dimensions.y/2,center.z))
        pu=627+(math.cos(az)*face.x-math.sin(az)*face.y)/unit
        pv=origin_v-(math.sin(el)*math.sin(az)*face.x+math.sin(el)*math.cos(az)*face.y+math.cos(el)*face.z)/unit
        index=pigments[min(313,max(0,int(pv/1254*314)))][min(313,max(0,int(pu/1254*314)))]
        if index is None:continue
        if ob['palette_index']>=6 and index<6:continue
        if ob['palette_index'] in [3,4,5] and index not in [3,4]:continue
        infill=a.box('Interior flame cube',center,(ob.dimensions.x,ob.dimensions.y,course+.004),index,.003)
        infill['inferred_interior']=True;infill['palette_index']=index;infill['course']=k;filled.append(center)
for u,v,w,h in [(429,304,29,31),(801,251,27,29),(391,475,41,44),(857,397,40,43)]:block(u,v,w,h,2,True)
import ember_interior,importlib
importlib.reload(ember_interior);ember_interior.close_interior(a,max_junctions=24)
focus_z=(origin_v-627)*unit/math.cos(el);focus=(0,0,focus_z)
a.studio(focus,(-7*math.sin(az),-7*math.cos(az),focus_z+7*math.tan(el)),1.5048)
s=a.scene;s.render.resolution_x=1254;s.render.resolution_y=1254;s.cycles.samples=72
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=-.1
for ob in s.objects:
    if ob.type=='LIGHT' and ob.name.startswith('Key'):ob.data.energy=700;ob.data.color=(1,.98,.95)
bpy.context.view_layer.update()
support=[]
for ob in a.parts:
    if ob.get('course')!=0 or ob.get('detached_reference_feature'):continue
    vs=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    support.append({'part':ob.name,'center_m':list(ob.location),'bottom_m':min(v.z for v in vs),'xy_extents_m':[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in [0,1]]})
assert len(support)==30 and max(r['bottom_m'] for r in support)-min(r['bottom_m'] for r in support)<1e-6
(a.review/'base-support-source.json').write_text(json.dumps({'method':'Every authored and inferred floor-course cube has the same underside elevation; four reference sparks excluded. Includes each base footprint for center and inset-corner counter traces.','samples':support},indent=2))
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'source':s['concept'],'revision':'r10_grounded_volume','method':'Closed measured flame blocks placed in real vertical courses with a shared floor, solid interior cubes and four detached sparks. Each block uses a uniform palette pigment; the PNG is not projected onto geometry.','inferred':'Depth and hidden volume are inferred from the one-view concept. Interior cube pigments are estimated from coarse source color regions. No simulation or physical balance claim.','status':'pending_export_and_native_review'},indent=2))
result={'scene':s.name,'parts':len(a.parts),'ground_cubes':sum(o.get('course')==0 for o in a.parts)}
