"""Depth study: infer grounded cube-column elevations from the source outline."""
import bpy,sys,math,json,ast
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/hello/Projects/Terrarium');sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
from palette_asset import PaletteAsset,linear
recipe=(root/'Docs/BlenderRebuild/Ember/R9/ember.py').read_text(encoding='utf-8')
tree=ast.parse(recipe)
for node in tree.body:
    if isinstance(node,ast.ClassDef) and node.name=='EmberAsset':exec(compile(ast.Module(body=[node],type_ignores=[]),'palette','exec'))
    if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ['rows','P']:
        globals()[node.targets[0].id]=ast.literal_eval(node.value)
a=EmberAsset('EmberVolumeTrial','ember.png',P);a.material.name='M_Ember_Flame'
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
a.save()
result={'scene':s.name,'parts':len(a.parts),'ground_cubes':sum(o.get('course')==0 for o in a.parts)}
