import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve()
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not E.get_game_world()
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label() in ['WX_AlderRiver','WX_HomeTributary']:
  a.modify();c=a.static_mesh_component;c.modify();c.set_collision_profile_name('NoCollision')
  c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
  rows.append(a.get_actor_label())
assert len(rows)==2
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(R/'Docs/WorldExpansion/water-profile-repair.json').write_text(json.dumps({'actors':rows,'profile':'NoCollision','reason':'Named profile persists through reload; transient custom collision enable flag alone reverted'},indent=2))
