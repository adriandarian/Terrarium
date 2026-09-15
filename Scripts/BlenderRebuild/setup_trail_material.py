"""Keep authored paver UVs and use actual relief for terrain collision."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
for key in ['TrailTerrain','TrailPatch']:
    mesh=unreal.load_asset('/Game/Terrarium/Blender/'+key+'/SM_Blender_'+key);assert mesh
    body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    mat=mesh.get_material(0);assert mat.get_name()=='M_'+key
    (root/'Docs/BlenderRebuild'/key/'world-material.json').write_text(json.dumps({'asset':key,'material':mat.get_path_name(),'mapping':'Authored UVs preserve physical paver and source-albedo alignment; no world projection.','collision':'ComplexAsSimple','visual_acceptance':False},indent=2))
