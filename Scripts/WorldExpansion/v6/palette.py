import unreal
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
s=(R/'Scripts/WorldExpansion/materials_v5.py').read_text()
s=s[:s.index('\nbindings=[]')]
s=s.replace("DEST='/Game/Terrarium/WorldExpansion/TerrainV5'","DEST='/Game/Terrarium/WorldExpansion/V6/Terrain'")
s=s.replace("D=R/'Docs/WorldExpansion/V5'","D=R/'Docs/WorldExpansion/V6'")
s=s.replace('colorconst(.66,.82,.50)','colorconst(.72,.85,.70)').replace('colorconst(.10,.135,.028)','colorconst(.065,.115,.075)')
s=s.replace("    if kind=='ground':", "    if kind in ('ground','stone'):rock=lerp(colorconst(.26,.29,.27),rock,const(.55))\n    if kind=='ground':")
exec(compile(s,'v6_materials','exec'))
print('V6 terrain palette saved')
