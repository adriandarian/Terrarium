"""Persist an exact pre-pass component comparison after editor restart."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/VoxelPass'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
applied=json.loads((out/'applied.json').read_text())
reverse={v['new']:k for k,v in applied['replacements'].items()}
def restore():
    counts={}
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh:continue
            name=c.static_mesh.get_name()
            if name in reverse:
                counts[name]=c.get_instance_count()
                c.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/'+reverse[name]))
            if name.startswith('SM_MeadowTile'):mat='M_Pass7_Ground'
            elif name.startswith(('SM_VoxelCliff','SM_CliffColumn_v6')):mat='M_Pass7_Stone'
            elif name.startswith('SM_PathTile'):mat='M_Pass7_Path'
            elif name in ('SM_VoxelTree','SM_VoxelBush','SM_Tree_v3','SM_Bush_v2'):mat='M_SculptedPalette'
            else:continue
            c.set_material(0,unreal.load_asset('/Game/Terrarium/Materials/'+mat))
    return counts
counts=restore()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,applied['backup'])
world=None
assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
(out/'restart-check.json').write_text(json.dumps({'native_editor_restart':True,'component_swaps_persisted':False,'comparison_map_saved':applied['backup']},indent=2))
unreal.log('VOXEL_COMPARISON_RECOVERED')
