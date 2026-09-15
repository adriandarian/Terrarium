"""A small persistent core light supports the emissive crystal at world EV12."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};prism=scene['Blender_TrailPrism_MarketCounter']
label='Blender_TrailPrism_CoreLight';position=prism.get_actor_location()+unreal.Vector(0,0,12)
light=scene.get(label) or actors.spawn_actor_from_class(unreal.PointLight,position)
assert isinstance(light,unreal.PointLight);light.set_actor_label(label);light.set_actor_location(position,False,False)
c=light.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE)
c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS)
c.set_intensity(150);c.set_attenuation_radius(40);c.set_light_color(unreal.LinearColor(1,.78,.29,1))
c.set_editor_property('source_radius',2.5);c.set_editor_property('cast_shadows',False)
assert levels.save_current_level()
(root/'Docs/BlenderRebuild/TrailPrism/core-light.json').write_text(json.dumps({'actor':label,'location_cm':[position.x,position.y,position.z],'intensity_lumens':150,'attenuation_radius_cm':40,'source_radius_cm':2.5,'color_linear':[1,.78,.29],'cast_shadows':False,'purpose':'Small local approximation of the luminous inclusion. Scene exposure is unchanged; shadowless point light approximates light passing through the crystal.'},indent=2))
