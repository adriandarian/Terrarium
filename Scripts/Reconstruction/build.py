"""Build selected reconstruction recipes serially in the verified editor."""
import hashlib,importlib,json,sys,time
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Assets'));sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import meshkit
importlib.reload(meshkit)
r=json.loads((root/'Saved/reconstruction-build.json').read_text())
assert r['module'] in ['humanoids','architecture','creatures_items','environment','surfaces','compound']
module=importlib.import_module(r['module']);importlib.reload(module)
meshkit.ROOT='/Game/Terrarium/Reconstruction'
records=[];out=root/'Docs/Reconstruction/Builds';out.mkdir(parents=True,exist_ok=True)
for key in r['keys']:
    started=time.monotonic();revision=r.get('revision',1)
    if key=='civic_hall' and r['module']=='architecture':
        m=module.civic_hall(rear_center_windows=revision>=5,entrance_details=revision>=6)
    else:
        m=module.BUILDERS[key]()
    if revision>1:m.name+='_R'+str(revision)
    path=meshkit.ROOT+'/Meshes/'+m.name
    assert not unreal.EditorAssetLibrary.does_asset_exist(path),'Use a new explicit revision after inspecting prior result'
    bounds={'min':[min(v[i] for v in m.vertices) for i in range(3)],'max':[max(v[i] for v in m.vertices) for i in range(3)]}
    # Set a stable contact pivot for reconstructed objects, regardless of bevel inset.
    zmin=bounds['min'][2]
    if abs(zmin)>1e-7:
        m.vertices=[(v[0],v[1],v[2]-zmin) for v in m.vertices]
        for part in m.parts:part['center']=(part['center'][0],part['center'][1],part['center'][2]-zmin)
        bounds['max'][2]-=zmin;bounds['min'][2]=0
    mesh=m.save()
    if key=='civic_hall' and r['module']=='architecture' and revision>=5:
        mat=unreal.load_asset('/Game/Terrarium/Reconstruction/Materials/M_CivicHall_Warm_R4')
        assert mat,'Build the civic hall warm palette before subsequent geometry revisions'
        mesh.set_material(0,mat)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    if key=='kindlehorn' and hasattr(m,'vertex_alphas'):
        import kindlehorn_material
        importlib.reload(kindlehorn_material)
        kindlehorn_material.apply(mesh)
    if key=='ember_crest' and r['module']=='creatures_items' and hasattr(m,'vertex_alphas'):
        import crest_material
        importlib.reload(crest_material)
        crest_material.apply(mesh)
    if r['module']=='surfaces':
        mat=unreal.load_asset('/Game/Terrarium/Migration/Materials/MI_Surface_'+key)
        assert mat;mesh.set_material(0,mat);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    validation=json.loads((root/'Docs/Phase1/Validation'/(m.name+'.json')).read_text())
    row={'source':key+'.png','key':key,'module':r['module'],'revision':revision,'asset':path,'name':m.name,'bounds_cm':bounds,'triangles':validation['triangles'],'saved_normal_errors':validation['saved_normal_errors'],'recipe_sha256':hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),'seconds':round(time.monotonic()-started,2),'visual_acceptance':'pending_independent_comparison'}
    if hasattr(m,'surface_geometry'):row['surface_geometry']=m.surface_geometry
    if hasattr(m,'surface_details'):row['surface_details']=m.surface_details
    if hasattr(m,'entrance_foundation_details'):
        row['entrance_foundation_details']=m.entrance_foundation_details
    if key=='civic_hall' and r['module']=='architecture' and revision>=5:
        row.update(material='/Game/Terrarium/Reconstruction/Materials/M_CivicHall_Warm_R4',
                   added_rear_center_windows=4, rear_center_window_x_cm=[-71.5,71.5],
                   rear_window_story_centers_z_cm=[206,443],
                   visual_review_document='Docs/Reconstruction/civic-hall-windows-review.md')
        if revision>=6:
            row['visual_review_document']='Docs/Reconstruction/civic-hall-entrance-review.md'
    (out/(m.name+'.json')).write_text(json.dumps(row,indent=2));records.append(row)
    unreal.log('RECON_BUILT '+m.name)
(root/'Saved/reconstruction-last-build.json').write_text(json.dumps(records,indent=2))
