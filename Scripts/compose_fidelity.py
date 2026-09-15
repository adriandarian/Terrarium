"""Broad visual pass 4: reference-derived layout, detailed replacement assets.

The earlier approved Homestead map remains intact for comparison.
"""
import unreal,sys,importlib,math,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
path='/Game/Terrarium/Maps/HomesteadFidelity'
if not unreal.EditorAssetLibrary.does_asset_exist(path):
    assert levels.load_level('/Game/Terrarium/Maps/RenderBaseline')
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(w,path)
    w=None
assert levels.load_level(path)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
    if isinstance(a,(unreal.StaticMeshActor,unreal.InstancedFoliageActor)):actors.destroy_actor(a)
sys.path.insert(0,str(root/'Scripts/Fidelity'))
for name in ['reference','placement','terrain','paths','homestead','vegetation']:
    sys.modules.pop(name,None)
import reference,placement,terrain,paths,homestead,vegetation
cells=terrain.build();paths.build();homestead.build();vegetation.build(cells)
placement.flush()
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
sun=scene['Baseline_WarmSun'];sun.set_actor_rotation(unreal.Rotator(pitch=-50,yaw=145,roll=0),False)
sun.light_component.set_intensity(18000)
sun.light_component.set_light_color(unreal.LinearColor(1,.9,.70,1))
sun.light_component.set_editor_property('light_source_angle',16.0)
sky=scene['Baseline_SkyLight'].light_component;sky.set_intensity(5.0);sky.recapture_sky()
pp=scene['Baseline_FixedExposure_EV12'];settings=pp.settings
for key,value in [('color_saturation',unreal.Vector4(.95,.95,.95,1)),('lumen_scene_lighting_quality',4.0),('lumen_final_gather_quality',4.0)]:
    settings.set_editor_property('override_'+key,True);settings.set_editor_property(key,value)
pp.set_editor_property('settings',settings)
camera=scene['Baseline_Orthographic_Review'];cc=camera.camera_component
p=math.radians(reference.PITCH);y=math.radians(reference.YAW)
f=unreal.Vector(math.cos(p)*math.cos(y),math.cos(p)*math.sin(y),math.sin(p))
camera.set_actor_location(-f*6500,False,False)
camera.set_actor_rotation(unreal.Rotator(pitch=reference.PITCH,yaw=reference.YAW,roll=0),False)
cc.set_ortho_width(reference.WIDTH*reference.CM_PER_PIXEL)
cc.set_editor_property('aspect_ratio',reference.WIDTH/reference.HEIGHT)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
assert levels.save_current_level()
out=root/'Docs/Fidelity';out.mkdir(parents=True,exist_ok=True)
(out/'pass-4-layout.json').write_text(json.dumps({'broad_visual_pass':4,'map':path,'counts':dict(placement.counts),'terrain_cells':len(cells),'reference_size':[reference.WIDTH,reference.HEIGHT],'camera':{'pitch':reference.PITCH,'yaw':reference.YAW,'cm_per_pixel':reference.CM_PER_PIXEL},'anchors':reference.BUILDINGS,'pixel_parity':'unproven; requires direct rendered comparison'},indent=2))
unreal.log('FIDELITY_LAYOUT_COMPLETE')
