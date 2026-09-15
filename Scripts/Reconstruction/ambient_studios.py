"""Neutral ambient IBL for this task's six review maps, retaining direct shadows."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
base='/Game/Terrarium/Reconstruction/Maps/'
assert 'Reconstruction/Maps/ReviewStage' in str(levels.get_current_level())
levels.save_current_level()
records=[]
for name in ['ReviewStage','Architecture','Characters','Collectibles','Environment','Surfaces']:
    assert levels.load_level(base+name)
    scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
    label='StudioAmbientSky' if name=='ReviewStage' else 'GalleryAmbientSky'
    a=scene.get(label) or actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,400));a.set_actor_label(label)
    c=a.get_component_by_class(unreal.SkyLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_property('source_type',unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
    c.set_cubemap(unreal.load_asset('/Engine/EngineResources/GrayLightTextureCube'));c.set_intensity(.65);c.set_editor_property('cast_shadows',False)
    assert levels.save_current_level();records.append({'map':base+name,'ambient_intensity':.65,'cubemap':'/Engine/EngineResources/GrayLightTextureCube','direct_key_shadows_retained':True})
assert levels.load_level(base+'ReviewStage')
(root/'Docs/Reconstruction/ambient-lighting.json').write_text(json.dumps(records,indent=2))
