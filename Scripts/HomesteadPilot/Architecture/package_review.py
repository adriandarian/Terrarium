"""Isolated packaging and textured render QA. Does not touch the live MCP editor."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium');OUT=ROOT/'SourceAssets/Blender/HomesteadPilot/Architecture';DOC=ROOT/'Docs/HomesteadPilot/Architecture'
assert bpy.app.background
old=list(bpy.data.scenes);obs=list(bpy.data.objects)
with bpy.data.libraries.load(str(OUT/'Architecture.library.blend'),link=False) as (a,b):b.scenes=['Terrarium_HomesteadArchitecture']
s=b.scenes[0];bpy.context.window.scene=s;bpy.data.batch_remove(ids=obs)
for scene in old:bpy.data.scenes.remove(scene)
manifest=json.loads((DOC/'manifest.json').read_text());checks=[]
for r in manifest['assets']:
    for lod in r['lods']:
        col=bpy.data.collections[f'HP_{r["name"]}_LOD{lod["level"]}'];points=[v.co for o in col.objects for v in o.data.vertices]
        lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
        assert all(abs(a-b)<.00001 for a,b in zip(lo,lod['bounds_m']['min']))
        assert all(abs(a-b)<.00001 for a,b in zip(hi,lod['bounds_m']['max']))
        assert all(o.data.uv_layers.active and len(o.data.uv_layers.active.data)==len(o.data.loops) for o in col.objects)
        checks.append({'asset':r['name'],'lod':lod['level'],'bounds_pass':True,'uv_coverage_pass':True,'parts':len(col.objects)})
images={n.image for o in s.objects if o.type=='MESH' for m in o.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
assert len(images)==4 and all(i.packed_file for i in images)
cam=s.camera
views=[('Cottage_front','Cottage',0,(-8,-12,8.2),(0,-.1,2.3),8),('Cottage_rear','Cottage',0,(8,11,7),(0,0,2.3),8),('Cottage_roof_close','Cottage',0,(-5,-8,8),(0,-.6,3.45),5.8),('Cottage_entry','Cottage',0,(-2.5,-8,3.5),(0,-1.9,1.4),4.7),('Fence_front','Fence',0,(4,-8,4),(0,0,.65),3.8),('Bridge_front','Bridge',0,(5,-8,5),(0,0,.6),5.1),('Cottage_LOD1','Cottage',1,(-8,-12,8.2),(0,-.1,2.3),8),('Cottage_LOD2','Cottage',2,(-8,-12,8.2),(0,-.1,2.3),8)]
for name,family,lod,position,target,scale in views:
    for c in s.collection.children:c.hide_render=c.name!=f'HP_{family}_LOD{lod}'
    cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    s.render.filepath=str(DOC/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED '+name,flush=True)
for c in s.collection.children:c.hide_render=c.name!='HP_Cottage_LOD0'
cam.data.type='PERSP';cam.data.lens=19;cam.location=(0,-1.73,1.75);cam.rotation_euler=(Vector((0,1.4,1.67))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(DOC/'Cottage_interior.png');bpy.ops.render.render(write_still=True)
cam.data.type='ORTHO';cam.data.ortho_scale=8;cam.location=(-8,-12,8.2);cam.rotation_euler=(Vector((0,-.1,2.3))-cam.location).to_track_quat('-Z','Y').to_euler()
for c in s.collection.children:c.hide_viewport=c.name!='HP_Cottage_LOD0'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HomesteadArchitecture.blend'),compress=True)
report={'source_bounds_uv_checks':checks,'packed_images':4,'normal_project_saved':True,'blender_version':bpy.app.version_string,'reopen_pending':True,'limitations':'No gameplay traversal, collision or runtime LOD transition evidence here. Static textured previews are source QA only.'}
(DOC/'verification.json').write_text(json.dumps(report,indent=2));print('ARCHITECTURE_PACKAGED',flush=True)
