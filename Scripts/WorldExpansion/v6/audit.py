import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
d=json.loads((R/'Docs/WorldExpansion/settlement-layout.json').read_text());out={}
for k,p in d['assets'].items():
 m=unreal.load_asset(p);b=m.get_bounding_box()
 out[k]={'min':[b.min.x/100,b.min.y/100,b.min.z/100],'max':[b.max.x/100,b.max.y/100,b.max.z/100],'materials':[s.material_interface.get_path_name() if s.material_interface else None for s in m.static_materials]}
(R/'Docs/WorldExpansion/V6/asset-audit.json').write_text(json.dumps(out,indent=2))
print('V6 audit complete')
