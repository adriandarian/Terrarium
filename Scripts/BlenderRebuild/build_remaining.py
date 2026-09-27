"""Run one new asset through the established export, reopen, and review path."""
import bpy,sys,runpy,json
from pathlib import Path
root=Path('C:/Users/hello/Projects/Terrarium')
assert Path(bpy.context.scene.get('terrarium_project',''))==root
sys.path.insert(0,str(root/'Scripts/BlenderRebuild'))
key=(root/'Saved/blender-build-asset.txt').read_text().strip()
import remaining_models,importlib
importlib.reload(remaining_models)
a=remaining_models.build(key)
runpy.run_path(str(root/'Scripts/BlenderRebuild/export_asset.py'))
runpy.run_path(str(root/'Scripts/BlenderRebuild/verify_blend.py'))
bpy.ops.render.render(write_still=True)
result={'asset':key,'review':str(a.review/'front.png'),'exported_and_reopened':True}
