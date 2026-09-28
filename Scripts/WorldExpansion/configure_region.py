"""Region-local atmosphere, named review cameras and playable-map settings."""
import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
assert not E.get_game_world()
scene={a.get_actor_label():a for a in A.get_all_level_actors()}
fog=next(a for a in scene.values() if isinstance(a,unreal.ExponentialHeightFog))
c=fog.component
c.set_fog_density(.006)
c.set_fog_height_falloff(.18)
c.set_start_distance(16000.)
c.set_fog_max_opacity(.3)
c.set_fog_inscattering_color(unreal.LinearColor(1150,1430,1650,1))
c.set_directional_inscattering_color(unreal.LinearColor(0,0,0,1))
views=[
 ('RegionOverview',[100,-850,650],[0,45,35],70),
 ('AlderwatchCity',[445,75,125],[300,265,27],57),
 ('StonegateTown',[-170,240,125],[-320,390,37],57),
 ('BrookmereVillage',[-113,75,82],[-220,180,18],57),
 ('ReedbankVillage',[385,-412,75],[280,-300,15],57),
 ('HighfieldVillage',[-218,-430,92],[-340,-310,24],57),
 ('MountainPass',[-90,400,105],[-440,705,170],65),
 ('HomeInValley',[55,-65,45],[0,12,5],65),
 ('CityStreet',[300,202,26.2],[300,290,28],74),
]
out=[]
for name,pos,target,fov in views:
 label='WX_Review_'+name
 a=scene.get(label) or A.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
 a.set_actor_label(label);a.set_folder_path('WorldExpansion/ReviewCameras')
 p=unreal.Vector(*[v*100 for v in pos]);t=unreal.Vector(*[v*100 for v in target])
 a.set_actor_location(p,False,False);a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(p,t),False)
 a.set_editor_property('auto_activate_for_player',unreal.AutoReceiveInput.DISABLED)
 a.camera_component.set_projection_mode(unreal.CameraProjectionMode.PERSPECTIVE)
 a.camera_component.set_field_of_view(fov)
 a.camera_component.set_editor_property('post_process_blend_weight',0.)
 a.camera_component.set_editor_property('constrain_aspect_ratio',False)
 out.append({'name':name,'actor':label,'position_m':pos,'target_m':target,'fov':fov})
L.pilot_level_actor(next(a for a in A.get_all_level_actors() if a.get_actor_label()=='WX_Review_AlderwatchCity'))
L.set_exact_camera_view(True);L.editor_set_game_view(True)
A.set_selected_level_actors([])
assert L.save_current_level()
(R/'Docs/WorldExpansion/views.json').write_text(json.dumps(out,indent=2))
(R/'Docs/WorldExpansion/atmosphere.json').write_text(json.dumps({'fog_density':.006,'falloff':.18,'start_cm':16000,'max_opacity':.3,'scope':'ValleyRegion light components only'},indent=2))
