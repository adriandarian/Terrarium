import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium');OUT=ROOT/'SourceAssets/Blender/HomesteadPilot/Architecture/RoofRepairV2';DOC=ROOT/'Docs/HomesteadPilot/Architecture/RoofRepairV2'
assert bpy.app.background;original_scenes=list(bpy.data.scenes);original_objects=list(bpy.data.objects)
with bpy.data.libraries.load(str(OUT/'ArchitectureRoofV2.library.blend'),link=False) as(a,b):b.scenes=['Terrarium_ArchitectureRoofRepairV2']
s=b.scenes[0];bpy.context.window.scene=s;bpy.data.batch_remove(ids=original_objects)
for old in original_scenes:bpy.data.scenes.remove(old)
assert Path(s['terrarium_project'])==ROOT
cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=8;cam.location=(-8,-12,8.2);cam.rotation_euler=(Vector((0,-.1,2.3))-cam.location).to_track_quat('-Z','Y').to_euler();s.cycles.samples=24
for level in [1,2]:
    for c in s.collection.children:c.hide_render=not any(o.get('asset')=='Cottage' and o.get('lod')==level for o in c.objects);c.hide_viewport=False
    s.render.filepath=str(DOC/f'Cottage_RoofV2_LOD{level}.png');bpy.ops.render.render(write_still=True)
for c in s.collection.children:c.hide_viewport=c.hide_render
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'HomesteadArchitecture_RoofV2.blend'),compress=True)
print('ROOF_V2_PACKAGED',flush=True)
