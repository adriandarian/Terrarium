"""Restore the intended complex collision after reimport and refresh geometry metadata."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
mesh=unreal.load_asset('/Game/Terrarium/Blender/BridgeThreshold/SM_Blender_BridgeThreshold');assert mesh
body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
folder=root/'Docs/BlenderRebuild/BridgeThreshold';path=folder/'world-placement.json'
if path.exists():
    r=json.loads(path.read_text());s=json.loads((folder/'source-adaptation.json').read_text())
    for key in ['bank_top_cm','deck_top_cm']:r[key]=s[key]
    r['status']='updated_pending_saved_collision_contact_and_visual_review';path.write_text(json.dumps(r,indent=2))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
