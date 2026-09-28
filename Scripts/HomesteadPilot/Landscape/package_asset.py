"""Repackage one isolated scene library as a normal independently openable .blend."""
import bpy,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];path=Path(args[0]);name=args[1]
assert path.resolve().is_relative_to(Path('C:/Users/hello/Projects/Terrarium/SourceAssets/Blender/HomesteadPilot/Landscape').resolve())
with bpy.data.libraries.load(str(path),link=False) as (src,dst):
    assert name in src.scenes;dst.scenes=[name]
scene=dst.scenes[0];assert Path(scene.get('terrarium_project','')).resolve()==Path('C:/Users/hello/Projects/Terrarium').resolve()
bpy.context.window.scene=scene
for other in list(bpy.data.scenes):
    if other!=scene:bpy.data.scenes.remove(other)
packaged=path.with_name(path.stem+'_packaged.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(packaged),compress=True)
packaged.replace(path)
assert path.stat().st_size>10000
print('PACKAGED_LANDSCAPE '+name)
