import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
rows=['HitResult: '+str(dir(unreal.HitResult))]
for cls in [unreal.SystemLibrary,unreal.GameplayStatics,unreal.MathLibrary,unreal.HitResult]:
    for name in dir(cls):
        if 'hit_result' in name.lower() or 'to_tuple'==name:rows.append(cls.__name__+'.'+name+': '+str(getattr(cls,name).__doc__))
(root/'Saved/blender-collision-api.txt').write_text('\n'.join(rows))
