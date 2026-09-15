"""Editable bridge-only placement variant with piles extended to the existing riverbed."""
import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
root=Path('C:/Users/hello/Projects/Terrarium');source=bpy.context.scene
assert Path(source.get('terrarium_project',''))==root and source['asset_name']=='RiverCrossing'
key='RiverBridge';name='Terrarium_'+key
if name in bpy.data.scenes:
    old=bpy.data.scenes[name];bpy.data.batch_remove(ids=list(old.objects));bpy.data.scenes.remove(old)
s=bpy.data.scenes.new(name);bpy.context.window.scene=s
s['terrarium_project']=str(root);s['asset_name']=key;s['concept']=source['concept'];s['variant_of']='RiverCrossing'
s['variant_purpose']='Bridge module only; original planks and rails retained. Piles extend 0.82 m below the reference foot for the existing riverbed.'
s['deck_top_m']=.62
out=root/'SourceAssets/Blender'/key;out.mkdir(exist_ok=True);review=root/'Docs/BlenderRebuild'/key;review.mkdir(exist_ok=True)
parts=[];mat=next(o.data.materials[0] for o in source.objects if o.get('module')=='Bridge').copy();mat.name='M_'+key
for n in mat.node_tree.nodes:
    if n.type!='TEX_IMAGE' or not n.image:continue
    kind=next(k for k in ['BaseColor','Roughness','Emission'] if k in n.image.name)
    img=n.image.copy();img.name=key+'_'+kind;n.image=img
    target=out/(key+'_'+kind+'.png');shutil.copyfile(root/'SourceAssets/Blender/RiverCrossing'/('RiverCrossing_'+kind+'.png'),target)
    img.filepath=str(target);img.pack()
for o in source.objects:
    if o.get('module')!='Bridge':continue
    clone=o.copy();clone.data=o.data.copy();clone.data.materials.clear();clone.data.materials.append(mat);s.collection.objects.link(clone)
    clone.hide_set(False);clone.hide_render=False;parts.append(clone)
    if o.get('part')=='Square bridge post':
        extension=o.copy();extension.data=o.data.copy();extension.data.materials.clear();extension.data.materials.append(mat)
        extension.name='Riverbed pile extension';extension['part']='Riverbed pile extension';extension.location.z=-.41
        for v in extension.data.vertices:v.co.z*=.82/1.20
        s.collection.objects.link(extension);parts.append(extension)
# Use the same authored lighting and an isolated bridge camera for review.
for o in source.objects:
    if o.type not in ['LIGHT','CAMERA']:continue
    clone=o.copy();clone.data=o.data.copy();s.collection.objects.link(clone)
    if o.type=='CAMERA':
        s.camera=clone;clone.location=(-4,-9,12);clone.rotation_euler=(Vector((0,0,.5))-clone.location).to_track_quat('-Z','Y').to_euler();clone.data.ortho_scale=4.65
s.world=source.world;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
s.render.resolution_x=1000;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.render.film_transparent=True
s.view_settings.view_transform=source.view_settings.view_transform;s.view_settings.look=source.view_settings.look;s.view_settings.exposure=source.view_settings.exposure
s.render.image_settings.file_format='PNG'
for o in s.objects:o.select_set(False)
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.context.view_layer.update()
bpy.data.libraries.write(str(out/(key+'.blend')),{s},path_remap='RELATIVE',fake_user=True,compress=True)
result={'asset':key,'parts':len(parts),'variant_of':'RiverCrossing','status':'authored_pending_review'}
(review/'build.json').write_text(json.dumps(result,indent=2))
