"""Bake environment-only parts using native Geometry Script and validate saved geometry."""
import unreal,sys,json,importlib,hashlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Assets'));sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import meshkit
meshkit.ROOT='/Game/Terrarium/Environment'
r=json.loads((root/'Saved/environment-build.json').read_text());assert r['module'] in ['environment_props','environment_ground','environment_water','environment_wheat','environment_cliffs']
mod=importlib.import_module(r['module']);importlib.reload(mod)
out=root/'Docs/Environment/Builds';out.mkdir(exist_ok=True)
for key in r.get('keys',list(mod.BUILDERS)):
    m=mod.BUILDERS[key]()
    if r.get('revision',1)>1:m.name+='_R'+str(r['revision'])
    path=meshkit.ROOT+'/Meshes/'+m.name
    assert not unreal.EditorAssetLibrary.does_asset_exist(path),path
    sm=m.save();sm.set_material(0,unreal.load_asset('/Game/Terrarium/Environment/Materials/M_EnvironmentPigment'));assert unreal.EditorAssetLibrary.save_loaded_asset(sm)
    v=json.loads((root/'Docs/Phase1/Validation'/(m.name+'.json')).read_text());assert v['saved_normal_errors']==0
    row={'key':key,'asset':path,'module':r['module'],'revision':r.get('revision',1),'bounds':{'min':[min(v[i] for v in m.vertices) for i in range(3)],'max':[max(v[i] for v in m.vertices) for i in range(3)]},'triangles':len(m.triangles),'saved_normal_errors':v['saved_normal_errors'],'recipe_sha256':hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest()}
    (out/(m.name+'.json')).write_text(json.dumps(row,indent=2));unreal.log('ENVIRONMENT_PART_BUILT '+m.name)
