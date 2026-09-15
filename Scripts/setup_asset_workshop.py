import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
path='/Game/Terrarium/Maps/ModularGallery'
assert not unreal.EditorAssetLibrary.does_asset_exist(path),'Gallery already exists; inspect it rather than resetting it.'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,path)
world=None
assert levels.load_level(path)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
for name in ['Baseline_StoneCube','Baseline_ClaySphere']:
 if name in scene:actors.destroy_actor(scene[name])
floor=scene['Baseline_Ground'];floor.set_actor_scale3d(unreal.Vector(60,55,1))
camera=scene['Baseline_Orthographic_Review']
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
levels.save_current_level()
