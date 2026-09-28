"""Fresh background process only: package, render, independently round-trip FBXs."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium');OUT=ROOT/'SourceAssets/Blender/DetailCalibration';DOC=ROOT/'Docs/DetailCalibration'
assert bpy.app.background
factory_scenes=list(bpy.data.scenes);factory_objects=list(bpy.data.objects)
with bpy.data.libraries.load(str(OUT/'DetailCalibration.library.blend'),link=False) as (a,b):b.scenes=['Terrarium_DetailCalibration']
s=b.scenes[0];assert Path(s['terrarium_project'])==ROOT
bpy.context.window.scene=s
bpy.data.batch_remove(ids=factory_objects)
for old in factory_scenes:bpy.data.scenes.remove(old)
manifest=json.loads((DOC/'manifest.json').read_text());checks=[]
for r in manifest['specimens']:
    obs=[o for o in bpy.data.collections[r['name']].objects if o.type=='MESH']
    points=[v.co for o in obs for v in o.data.vertices]
    dimensions=[max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)]
    assert all(abs(a-b)<.00001 for a,b in zip(dimensions,r['dimensions_m'])),(r['name'],dimensions)
    checks.append({'name':r['name'],'source_dimensions_m':dimensions,'source_bounds_verified':True})

# Representative per-family same-camera images: shared person and framing, no texture changes.
person=bpy.data.collections['DC_Person'];p0={o:o.location.copy() for o in person.objects}
cam=s.camera
for r in manifest['specimens']:
    if r['family']=='Person':continue
    for c in s.collection.children:c.hide_render=c.name not in [r['name'],'DC_Person']
    center=Vector(r['placement_m'])
    for o in person.objects:o.location=center+Vector((-2.35,-.15,0))
    target=center+Vector((-.40,0,1.55))
    # 45 degree downward projection and orthographic lens are fixed across all 15 frames.
    cam.location=target+Vector((7,-10,math.sqrt(149)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=5.9;s.render.resolution_x=900;s.render.resolution_y=780;s.cycles.samples=24
    s.render.filepath=str(DOC/(r['name']+'.png'));bpy.ops.render.render(write_still=True)
    print('RENDERED '+r['name'],flush=True)
# Closeup uses same camera direction for each roof control; independent of full-frame comparison.
for r in [x for x in manifest['specimens'] if x['family']=='Cottage']:
    for c in s.collection.children:c.hide_render=c.name!=r['name']
    target=Vector(r['placement_m'])+Vector((0,.12,2.68));cam.location=target+Vector((7,-10,math.sqrt(149)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=3.2
    s.render.resolution_x=900;s.render.resolution_y=780;s.render.filepath=str(DOC/(r['name']+'_roof-close.png'));bpy.ops.render.render(write_still=True)
for o,pos in p0.items():o.location=pos
for c in s.collection.children:c.hide_render=False
target=Vector((5.5,11.5,1));cam.location=target+Vector((4,-22,34));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=32
s.render.resolution_x=1400;s.render.resolution_y=1600;s.render.filepath=str(DOC/'overview.png');bpy.ops.render.render(write_still=True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'DetailCalibration.blend'),compress=True)

# Fresh imported FBX meshes only in an independent check scene, never saved into the source.
verify=bpy.data.scenes.new('UnitRoundtrip');verify.unit_settings.system='METRIC';verify.unit_settings.scale_length=1;bpy.context.window.scene=verify
for r,check in zip(manifest['specimens'],checks):
    previous=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=r['fbx'])
    added=set(bpy.data.objects)-previous
    meshes=[o for o in added if o.type=='MESH'];assert len(meshes)==1
    ob=meshes[0];bpy.context.view_layer.update()
    dims=list(ob.dimensions)
    assert all(abs(a-b)<.0001 for a,b in zip(dims,r['dimensions_m'])),(r['name'],dims)
    check['fbx_roundtrip_dimensions_m']=dims;check['expected_unreal_dimensions_cm']=[v*100 for v in dims]
    check['roundtrip_verified']=True
    bpy.data.batch_remove(ids=list(added))
report={'checks':checks,'all_16_source_bounds_and_roundtrip_dimensions_pass':True,'source_saved_as_normal_blend':str(OUT/'DetailCalibration.blend'),'original_live_file_untouched':True,'reopen_check_pending':True,'limitations':'Coarse controls reproduce construction logic, not exact canonical meshes. No Unreal import/collision/gameplay/performance test in this report. Texture density is intentionally held out. Same camera previews are studio comparisons; no final fidelity or detail setting approval.'}
(DOC/'verification.json').write_text(json.dumps(report,indent=2));print('DETAIL_CALIBRATION_REVIEW_COMPLETE',flush=True)
