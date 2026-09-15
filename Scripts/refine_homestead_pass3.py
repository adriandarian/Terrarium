"""Whole-scene pass 3: quieter terrain palette and complete portrait framing."""
import unreal,sys,math,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Scene'))
from placement import world
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Homestead.' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}

def palette(name,srgb,blend):
    path='/Game/Terrarium/Materials/'+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):return unreal.load_asset(path)
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Terrarium/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib=unreal.MaterialEditingLibrary
    vc=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-500,0)
    base=lib.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-500,160)
    rgb=[int(srgb[i:i+2],16)/255 for i in (0,2,4)]
    rgb=[((c+.055)/1.055)**2.4 for c in rgb]
    base.set_editor_property('constant',unreal.LinearColor(*rgb,1))
    mix=lib.create_material_expression(mat,unreal.MaterialExpressionLinearInterpolate,-200,0)
    mix.set_editor_property('const_alpha',blend)
    assert lib.connect_material_expressions(vc,'',mix,'A')
    assert lib.connect_material_expressions(base,'',mix,'B')
    assert lib.connect_material_property(mix,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.94,300),(unreal.MaterialProperty.MP_SPECULAR,.08,400)]:
        node=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-200,y)
        node.set_editor_property('r',value)
        assert lib.connect_material_property(node,'',prop)
    lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat

turf=palette('M_QuietMeadow','7c8446',.55)
water=palette('M_QuietRiver','2c7779',.66)
for name,a in scene.items():
    if name.startswith('Homestead_GrassTile_'):a.static_mesh_component.set_material(0,turf)
    if name.startswith('Homestead_WaterTile_'):a.static_mesh_component.set_material(0,water)
scene['Baseline_SkyLight'].light_component.set_intensity(6.0)
scene['Baseline_SkyLight'].light_component.recapture_sky()
camera=scene['Baseline_Orthographic_Review']
pitch=-45;yaw=153;distance=6500
forward=unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)),math.cos(math.radians(pitch))*math.sin(math.radians(yaw)),math.sin(math.radians(pitch)))
camera.set_actor_location(world(45,30,230)-forward*distance,False,False)
camera.camera_component.set_ortho_width(2780)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
for name,a in scene.items():
    if name.startswith('Baseline_'):a.set_folder_path('Homestead/Camera' if a==camera else 'Homestead/Lighting')
assert levels.save_current_level()
(root/'Docs/Phase3/pass-3-settings.json').write_text(json.dumps({'pass':3,'camera_pitch':pitch,'camera_yaw':yaw,'ortho_width':2780,'aspect_ratio':.66,'sky_intensity':6,'changes':['Reduced turf and water color contrast with original matte palette materials','Wider portrait includes full bridge and approach','Slightly more ambient fill']},indent=2))
