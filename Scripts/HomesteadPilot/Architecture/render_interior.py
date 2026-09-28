"""Lit interior QA preview; review-only light, no save or geometry modification."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium');s=bpy.context.scene;assert bpy.app.background and s.name=='Terrarium_HomesteadArchitecture'
for c in s.collection.children:c.hide_render=c.name!='HP_Cottage_LOD0';c.hide_viewport=False
d=bpy.data.lights.new('QA_only_interior_softbox','AREA');d.energy=180;d.size=2.0;d.color=(1,.84,.63);o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(0,-.50,2.48)
cam=s.camera;cam.data.type='PERSP';cam.data.lens=19;cam.location=(0,-1.73,1.75);cam.rotation_euler=(Vector((0,1.4,1.67))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(ROOT/'Docs/HomesteadPilot/Architecture/Cottage_interior-lit-QA.png');bpy.ops.render.render(write_still=True)
print('LIT_INTERIOR_QA_RENDERED_NOT_SAVED',flush=True)
