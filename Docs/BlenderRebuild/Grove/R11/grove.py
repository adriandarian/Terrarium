"""Physical two-leaf Grove statuette from the supplied voxel concept."""
import bpy,sys,math,json,random
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset,linear
P=[('3c7108',.65,0),('4e8b0d',.60,0),('609b12',.59,0),('76b21c',.55,0),
   ('a9d637',.49,0),('cbe957',.45,0),('e0f184',.45,0),('32620b',.68,0),
   ('6d8217',.70,0),('7e9023',.68,0),('8b9a2c',.64,0),('4c6613',.73,0),
   ('735022',.85,0),('80592a',.86,0),('67421a',.89,0),('936532',.84,0),
   ('638d15',.74,0),('82ad23',.71,0),('95bc32',.65,0),('425c13',.76,0)]
class GroveAsset(PaletteAsset):
    def make_material(self):
        super().make_material()
        # The reference has smooth colored blocks, not the shared atlas's
        # coarse checker variation. Keep each physical block's color uniform.
        image=self.images[0];pixels=[]
        colors=[[linear(int(hx[j:j+2],16)/255) for j in [0,2,4]]+[1] for hx,_,_ in self.palette]
        for y in range(512):
            for x in range(512):pixels.extend(colors[min(y//64*8+x//64,len(colors)-1)])
        image.pixels.foreach_set(pixels);image.save();image.pack()
        # Explicit 8-bit PNGs retain the sRGB sampling path in this Unreal
        # import. Float-generated PNG16 colors sampled as encoded RGB there.
        export_scene=bpy.data.scenes.new('Grove texture export')
        try:
            export_scene.render.image_settings.file_format='PNG'
            export_scene.render.image_settings.color_mode='RGB'
            export_scene.render.image_settings.color_depth='8'
            export_scene.view_settings.look='None'
            export_scene.view_settings.exposure=0;export_scene.view_settings.gamma=1
            for image in self.images:
                export_scene.view_settings.view_transform='Raw' if image.colorspace_settings.name=='Non-Color' else 'Standard'
                path=image.filepath_raw
                image.save_render(path,scene=export_scene)
                if image.packed_file:image.unpack(method='REMOVE')
                image.source='FILE';image.filepath_raw=path;image.reload();image.pack()
        finally:bpy.data.scenes.remove(export_scene)
a=GroveAsset('Grove','grove.png',P)
leaf=a.material;leaf.name='M_Grove_Leaf';leaf.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0
stem=a.shader('Stem');soil=a.shader('Soil')
az=math.radians(20);el=math.radians(14);unit=.0012;origin_v=1120
def from_front(u,v,y):
    x=((u-627)*unit+math.sin(az)*y)/math.cos(az)
    z=((origin_v-v)*unit-math.sin(el)*math.sin(az)*x-math.sin(el)*math.cos(az)*y)/math.cos(el)
    return x,y,z
def face_block(label,box,index,material=leaf,y=0,depth=None):
    u0,v0,u1,v1=box;w=(u1-u0)*unit/math.cos(az);h=(v1-v0)*unit/math.cos(el)
    y-=len(a.parts)*.000035
    d=depth or min(w,h);x,_,z=from_front((u0+u1)/2,(v0+v1)/2,y)
    ob=a.box(label,(x,y+d/2,z),(w+.0035,d,h+.005),index,.004)
    ob.data.materials[0]=material;return ob
# Traced front block ranges retain the two leaves' distinct lengths and tips.
left=[(260,238,336,297,6),(336,234,391,299,3),(391,242,453,301,2),
      (232,306,316,374,0),(316,302,372,369,5),(372,302,426,365,1),(426,301,483,365,1),(483,299,520,368,1),
      (232,375,260,448,0),(260,377,315,438,1),(315,375,371,438,2),(371,367,425,434,5),(425,369,484,434,1),(484,368,520,435,1),(520,366,574,431,1),
      (259,441,315,507,0),(315,440,371,503,1),(371,433,425,499,3),(425,442,498,510,5),(498,435,520,493,1),(520,431,574,492,1),
      (316,505,371,564,0),(371,504,425,564,0),(425,507,500,576,2),(500,507,521,577,3),
      (355,568,425,631,7),(425,568,490,627,7)]
right=[(892,230,945,294,3),(945,224,1043,286,5),
       (821,273,890,344,1),(890,301,966,365,5),(966,298,1016,363,2),(1016,295,1063,367,1),
       (760,328,820,405,1),(820,345,890,425,1),(890,368,971,430,4),(971,368,1027,429,1),(1027,367,1063,437,0),
       (704,412,759,478,0),(760,405,819,473,1),(820,426,911,497,4),(911,432,972,496,1),(972,431,1027,491,1),
       (704,476,758,532,0),(795,492,850,565,3),(850,499,912,565,2),(912,496,977,562,1),(977,491,1027,536,0),
       (780,565,831,619,7),(831,565,888,617,7),(888,564,949,612,7)]
for boxes,label in [(left,'Left leaf blade block'),(right,'Right leaf blade block')]:
    for u0,v0,u1,v1,index in boxes:face_block(label,(u0,v0,u1,v1),index,y=.014 if index==7 else 0,depth=.13 if u0==795 and v0==492 else None)
# Small exposed side continuations close the stepped silhouette behind the blades.
for box,index in [((224,442,259,499),7),((270,505,316,552),7),((674,411,704,470),0),((674,469,704,522),0)]:
    face_block('Leaf rear edge block',box,index,y=.052)
# Fork and trunk are substantial green blocks, with two columns through the base.
branches=[(520,507,584,585,10),(523,587,588,657,9),(588,588,638,690,9),
          (704,547,780,618,10),(704,618,779,675,9),(654,628,718,682,9),
          (591,686,654,740,9),(654,682,718,738,8),
          (590,743,653,802,8),(653,739,717,800,8)]
for x0,v0,x1,v1,index in branches:face_block('Solid branching stem',(x0,v0,x1,v1),index,stem,y=-.006,depth=.089)
face_block('Right leaf to stem neck',(710,524,755,555),0,leaf,y=.04,depth=.045)
# Individually traced exposed courses replace the uniform concentric mound.
# These are solid beveled cuboids. Depth supplies the left-side silhouettes;
# unseen back volume is inferred from the same connected soil/turf courses.
base_start=len(a.parts)
soil_blocks=[
    (405,976,459,1061,14,.285),
    (475,1037,548,1106,14,.19),(548,1047,625,1117,14,.17),
    (625,1044,683,1115,12,.16),(683,1041,739,1110,13,.15),
    (739,1037,796,1105,12,.15),(796,1032,842,1086,14,.14),
    (842,1025,886,1080,14,.15),
    (461,976,493,1039,12,.16),(493,982,548,1050,12,.16),
    (548,987,574,1054,14,.17),(574,1015,625,1055,13,.15),
    (683,978,739,1044,12,.16),(739,973,796,1040,13,.16),
    (796,998,850,1037,14,.16),(850,962,895,1033,12,.18),
    (895,960,944,1032,13,.20),
]
for u0,v0,u1,v1,index,depth in soil_blocks:
    face_block('Irregular soil course',(u0,v0,u1,v1),index,soil,y=.01,depth=depth)
turf_blocks=[
    (405,912,460,978,16,.285),(405,975,459,1011,16,.18),
    (460,908,495,973,1,.21),(495,926,548,985,16,.20),
    (548,925,576,988,1,.20),(576,925,624,1020,16,.20),
    (624,891,686,985,16,.18),(686,887,741,981,16,.18),
    (741,884,796,976,1,.18),(624,984,687,1047,16,.13),
    (796,919,850,1005,16,.18),(850,894,895,966,16,.18),
    (895,891,944,965,16,.20),
    (461,840,498,903,1,.12),(498,856,555,907,16,.13),
    (556,821,649,904,16,.13),(649,799,719,861,1,.12),
    (719,794,782,857,16,.12),(782,851,819,895,1,.13),
    (819,843,877,889,16,.12),
    (527,783,588,834,16,.13),
]
for u0,v0,u1,v1,index,depth in turf_blocks:
    face_block('Irregular turf course',(u0,v0,u1,v1),index,leaf,y=0,depth=depth)
# Recessed solid cubes close the soil/turf interior behind the stepped fronts.
# They remain separate editable volumes, with small positive overlaps.
for box in [(496,892,556,944),(554,891,623,944),(622,850,681,907),(680,850,740,906),(739,848,797,904),(526,819,589,868),(782,884,848,936)]:
    face_block('Recessed turf core',box,16,leaf,y=.045,depth=.17)
# Buried root joins the visible trunk to the central turf, independent of camera.
for box in [(591,798,654,864),(654,798,718,864)]:face_block('Root block seated in turf',box,8,stem,y=.005,depth=.11)
# Export placement samples from the actual authored soil geometry.
bpy.context.view_layer.update()
support=[]
for ob in a.parts:
    if ob.get('part')=='Irregular soil course':
        support.append({'part':ob.name,'center_m':list(ob.location),'bottom_m':min((ob.matrix_world@v.co).z for v in ob.data.vertices)})
(a.review/'base-support-source.json').write_text(json.dumps({'method':'Center samples of each authored soil cuboid; physical underside heights retained, lowest cuboid establishes counter clearance.','samples':support},indent=2))
focus_z=(origin_v-627)*unit/math.cos(el)
focus=(0,0,focus_z);distance=7
camera=(-distance*math.sin(az),-distance*math.cos(az),focus_z+distance*math.tan(el))
a.studio(focus,camera,1.5048)
a.scene.render.resolution_x=1254;a.scene.render.resolution_y=1254;a.scene.cycles.samples=80
a.scene.view_settings.view_transform='Standard';a.scene.view_settings.look='Medium High Contrast';a.scene.view_settings.exposure=-.35
for ob in a.scene.objects:
    if ob.type=='LIGHT':
        if ob.name.startswith('Key'):ob.data.energy=700;ob.location=(-3,-4,5)
        elif ob.name.startswith('Fill'):ob.data.energy=220
        ob.rotation_euler=(Vector(focus)-ob.location).to_track_quat('-Z','Y').to_euler()
a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'source':a.scene['concept'],'method':'Measured asymmetric leaf block fronts, physical stem cubes and a fully modeled irregular soil/turf volume. Three packed color, emission and roughness maps; no projected concept image.','inferred':'Leaf thickness, unseen rear colors and soil footprint inferred from the single view. No gameplay or growth animation is implied.','status':'pending_studio_and_engine_review'},indent=2))
result={'asset':a.key,'parts':len(a.parts),'scene':a.scene.name}
