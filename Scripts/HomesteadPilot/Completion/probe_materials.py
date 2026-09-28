import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
rows=[]
for path in ['/Game/Terrarium/Blender/HomesteadCompound/SM_Blender_HomesteadCompound','/Game/Terrarium/HomesteadPilot/RemainingArt/Meshes/SM_HP_HomesteadCompound']:
 m=unreal.load_asset(path)
 rows.append({'path':path,'triangles':[m.get_num_triangles(i) for i in range(m.get_num_lods())],
  'slots':[{'name':str(s.get_editor_property('material_slot_name')),'material':str(s.get_editor_property('material_interface'))} for s in m.static_materials]})
(R/'Docs/HomesteadPilot/Completion/material-probe.json').write_text(json.dumps(rows,indent=2))
