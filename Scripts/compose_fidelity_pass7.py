"""Integrate all eighteen reference-fidelity assignments in native Unreal."""
import unreal, sys, importlib, json, math
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert unreal.EditorAssetLibrary.does_asset_exist('/Game/Terrarium/Maps/HomesteadBeforePass7')
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
levels.eject_pilot_level_actor()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
    if isinstance(a,(unreal.StaticMeshActor,unreal.InstancedFoliageActor)):
        actors.destroy_actor(a)
sys.path.insert(0,str(root/'Scripts/Fidelity'))
names=['reference','placement','homestead','vegetation','vegetation_v6','vegetation_v7',
       'terrain_v7','terrain_v8','water_v7','paths_v7','homestead_v7','moss_v7','ground_plants_v7',
       'shoreline_v7','materials_v7','lighting_v7','atmosphere_v7','water_material_v7','prop_transitions_v7']
for name in names:sys.modules.pop(name,None)
import reference as ref, placement
# Use placement's normal geometry-and-visual-review gate for the accepted assets.
def smooth(points):
    out=[]
    for i in range(len(points)-1):
        a,b,c,d=points[max(0,i-1)],points[i],points[i+1],points[min(len(points)-1,i+2)]
        for j in range(6):
            t=j/6
            out.append(tuple(.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in (0,1)))
    return out+[points[-1]]
ref.PATHS=[(h,smooth(p),w) for h,p,w in ref.PATHS]
import terrain_v8,paths_v7,homestead_v7,vegetation_v7,moss_v7,ground_plants_v7,shoreline_v7
cells=terrain_v8.build()
(root/'Docs/Fidelity/Pass7/terrain.json').write_text(json.dumps(terrain_v8.LAST_REPORT,indent=2))
paths_v7.build();homestead_v7.build();vegetation_v7.build(cells)
moss_v7.build(cells);ground_plants_v7.build(cells);shoreline_v7.build(cells)
import prop_transitions_v7
prop_transitions_v7.build(cells)
(root/'Docs/Fidelity/Pass7/prop-transitions.json').write_text(json.dumps(prop_transitions_v7.LAST_REPORT,indent=2))
placement.place('Traveler_v2',177,393,566,1.0,-20,'StaticDetails',False)
placement.flush()
import materials_v7
surface_report=materials_v7.apply()
(root/'Docs/Fidelity/Pass7/materials.json').write_text(json.dumps(surface_report,indent=2))
import water_material_v7
water_report=water_material_v7.apply()
(root/'Docs/Fidelity/Pass7/water-material.json').write_text(json.dumps(water_report,indent=2))
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
camera=scene['Baseline_Orthographic_Review'];cc=camera.camera_component
p=math.radians(ref.PITCH);y=math.radians(ref.YAW)
f=unreal.Vector(math.cos(p)*math.cos(y),math.cos(p)*math.sin(y),math.sin(p))
camera.set_actor_location(-f*6500,False,False)
camera.set_actor_rotation(unreal.Rotator(pitch=ref.PITCH,yaw=ref.YAW,roll=0),False)
cc.set_ortho_width(ref.WIDTH*ref.CM_PER_PIXEL)
cc.set_editor_property('aspect_ratio',ref.WIDTH/ref.HEIGHT)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
import lighting_v7,atmosphere_v7
(root/'Docs/Fidelity/Pass7/lighting.json').write_text(json.dumps(lighting_v7.apply(),indent=2))
(root/'Docs/Fidelity/Pass7/atmosphere.json').write_text(json.dumps(atmosphere_v7.apply(),indent=2))
assert levels.save_current_level()
report={'broad_visual_pass':7,'map':'/Game/Terrarium/Maps/HomesteadFidelity',
        'counts':dict(placement.counts),'terrain_cells':len(cells),'reference_size':[ref.WIDTH,ref.HEIGHT],
        'visual_acceptance':'pending direct rendered comparison',
        'camera':{'pitch':ref.PITCH,'yaw':ref.YAW,'cm_per_pixel':ref.CM_PER_PIXEL},'anchors':ref.BUILDINGS}
(root/'Docs/Fidelity/Pass7/layout.json').write_text(json.dumps(report,indent=2))
unreal.log('PASS7_COMPOSITION_SAVED')
