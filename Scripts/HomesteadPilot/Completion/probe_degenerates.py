import unreal,json
from pathlib import Path
R=Path(unreal.Paths.project_dir()).resolve();assert R==Path('C:/Users/hello/Projects/Terrarium')
S=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
rows=[]
for key in ['DeepDelverMark','Storm']:
 old=unreal.load_asset('/Game/Terrarium/Blender/'+key+'/SM_Blender_'+key)
 new=unreal.load_asset('/Game/Terrarium/HomesteadPilot/RemainingArt/Meshes/SM_HP_'+key)
 rows.append({'name':key,'baseline_lod0_triangles':old.get_num_triangles(0),'new_triangles':[new.get_num_triangles(i) for i in range(3)],
 'remove_degenerates':[S.get_lod_build_settings(new,i).get_editor_property('remove_degenerates') for i in range(3)]})
(R/'Docs/HomesteadPilot/Completion/degenerate-probe.json').write_text(json.dumps(rows,indent=2))
