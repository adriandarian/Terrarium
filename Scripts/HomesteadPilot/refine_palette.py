"""Scene-tested family tinting and local cottage illumination; pilot assets only."""
import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadPilot/Maps/StartingHome.' in str(L.get_current_level())
mel=unreal.MaterialEditingLibrary;dest='/Game/Terrarium/HomesteadPilot/Landscape';rows=[]
tints={key:(.55,.52,.43) for key in ('Stone','StoneLight','StoneShade')}
tints.update({key:(.72,.78,.52) for key in ('Leaf','LeafLight','LeafShade')})
tints.update({key:(.80,.85,.65) for key in ('Moss','Grass')})
for key,tint in tints.items():
 name='M_PilotLandscape_'+key;m=unreal.load_asset(dest+'/Materials/'+name);tex=unreal.load_asset(dest+'/Textures/T_'+name+'_BaseColor');assert m and tex
 mel.delete_all_material_expressions(m)
 sample=mel.create_material_expression(m,unreal.MaterialExpressionTextureSample,-650,0);sample.texture=tex
 color=mel.create_material_expression(m,unreal.MaterialExpressionVectorParameter,-650,220);color.set_editor_property('parameter_name','ArtDirectionTint');color.set_editor_property('default_value',unreal.LinearColor(*tint,1))
 mult=mel.create_material_expression(m,unreal.MaterialExpressionMultiply,-300,0)
 mel.connect_material_expressions(sample,'RGB',mult,'A');mel.connect_material_expressions(color,'RGB',mult,'B');mel.connect_material_property(mult,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,value,y in ((unreal.MaterialProperty.MP_ROUGHNESS,.92,300),(unreal.MaterialProperty.MP_SPECULAR,.12,400)):
  n=mel.create_material_expression(m,unreal.MaterialExpressionConstant,-300,y);n.r=value;mel.connect_material_property(n,'',prop)
 mel.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m)
 rows.append({'material':m.get_path_name(),'linear_tint':tint})
scene={a.get_actor_label():a for a in A.get_all_level_actors()}
lamp=scene.get('HP_InteriorWarmLight')
if not lamp:
 lamp=A.spawn_actor_from_class(unreal.PointLight,unreal.Vector(-205,53,810));lamp.set_actor_label('HP_InteriorWarmLight');lamp.set_folder_path('HomesteadPilot/Lighting')
c=lamp.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(350.);c.set_editor_property('attenuation_radius',450.)
c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3200.);c.set_editor_property('source_radius',12.)
assert L.save_current_level()
(R/'Docs/HomesteadPilot/palette-refinement.json').write_text(json.dumps({'materials':rows,'interior_light':{'actor':lamp.get_actor_label(),'intensity':350,'radius_cm':450,'temperature_k':3200},'reason':'Native viewport showed pale stone and sage foliage competing with cottage; local family tint preserves cottage and global exposure'},indent=2))
