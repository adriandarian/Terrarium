"""Verify the saved roof relief and replace only its Surfaces gallery entry."""
import hashlib,json,sys
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir())
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import build_galleries as g
key=globals().get('ROOF_KEY','cottage_roof_tile_v5')
assert key in ('cottage_roof_tile_v5','cottage_roof_tile_v6_candidate')
doc_stem='roof-tile' if key=='cottage_roof_tile_v5' else 'roof-tile-v6'
row=json.loads((root/'Docs/Reconstruction/Builds'/('SM_Recon_'+key+'_R2.json')).read_text())
layout=json.loads((root/'Docs/Reconstruction'/(doc_stem+'-layout.json')).read_text())
assert hashlib.sha256((root/'SourceAssets/Voxel'/(key+'.png')).read_bytes()).hexdigest()==layout['source_sha256']
mesh=unreal.load_asset(row['asset'])
material='/Game/Terrarium/Migration/Materials/MI_Surface_'+key
assert g.material_paths(mesh)==[material]
texture=unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(unreal.load_asset(material),'SourceColor')
assert g.package_path(texture)=='/Game/Terrarium/Migration/References/T_'+key
check=unreal.DynamicMesh()
_,outcome=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,check,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD())
assert outcome==unreal.GeometryScriptOutcomePins.SUCCESS
assert check.get_triangle_count()==row['triangles']
assert unreal.GeometryScript_MeshQueries.get_is_closed_mesh(check)
validation=json.loads((root/'Docs/Phase1/Validation'/ (row['name']+'.json')).read_text())
assert validation['saved_normal_errors']==0
assert validation['closed_components']==layout['tile_count']+1
assert row['surface_details']['original_every_third_row_height_reset_removed']
for view in ('front','back','top'):
    assert (root/'Docs/Reconstruction/Renders'/(row['name']+'-'+view+'.png')).is_file()
assert g.current_is(g.REVIEW) or g.current_is(g.PKG+'/Maps/Surfaces')
path=g.PKG+'/Maps/Surfaces'
assert g.LEVELS.load_level(path)
scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
def transform_values(actor):
    rotation=actor.get_actor_rotation()
    return g.vector_list(actor.get_actor_location())+g.vector_list(actor.get_actor_scale3d())+[rotation.pitch,rotation.yaw,rotation.roll]

before={n:{'mesh':g.package_path(a.static_mesh_component.static_mesh),'transform':transform_values(a),
           'materials':g.material_paths(a.static_mesh_component.static_mesh)} for n,a in scene.items() if n.startswith('Model_')}
assert len(before)==45
report_path=g.OUT/'Surfaces.json';report=json.loads(report_path.read_text())
record=next(r for r in report['models'] if r['key']==key)
label='Model_'+key+'_R2'
old_label=record['label'] if record['label'] in scene else label
a=scene[old_label]
assert g.package_path(a.static_mesh_component.static_mesh) in (record['mesh'],row['asset'])
# Also check the prior gallery receipt, so resuming after a saved-map check is safe.
for previous in report['models']:
    actor=scene[old_label if previous is record else previous['label']]
    assert all(abs(x-y)<1e-5 for x,y in zip(g.vector_list(actor.get_actor_location()),previous['location_cm']))
    assert all(abs(x-y)<1e-6 for x,y in zip(g.vector_list(actor.get_actor_scale3d()),previous['scale']))
    assert all(abs(v)<1e-6 for v in transform_values(actor)[6:])
    assert g.material_paths(actor.static_mesh_component.static_mesh)==previous['materials']
    if previous is not record:
        assert g.package_path(actor.static_mesh_component.static_mesh)==previous['mesh']
a.static_mesh_component.set_static_mesh(mesh)
a.set_actor_label(label)
caption=key.replace('_',' ')+'  |  R2'
scene[record['text_actor']].text_render.set_text(caption)
assert abs(g.actor_bounds(a)['min'][2])<.02
record.update(label=label,text=caption,revision=2,mesh=row['asset'],triangles=row['triangles'],
              receipt='Docs/Reconstruction/Builds/'+row['name']+'.json',materials=[material],
              world_bounds_cm=g.actor_bounds(a),surface_geometry=row['surface_geometry'])
assert g.LEVELS.save_current_level();assert g.LEVELS.load_level(path)
scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
assert len([n for n in scene if n.startswith('Model_')])==45
for name,old in before.items():
    actor=scene[label if name==old_label else name]
    assert g.package_path(actor.static_mesh_component.static_mesh)==(row['asset'] if name==old_label else old['mesh'])
    assert all(abs(x-y)<1e-6 for x,y in zip(transform_values(actor),old['transform']))
    assert g.material_paths(actor.static_mesh_component.static_mesh)==old['materials']
assert abs(g.actor_bounds(scene[label])['min'][2])<.02
report_path.write_text(json.dumps(report,indent=2))
g.ACTORS.set_selected_level_actors([scene[label]])
verification={'project':unreal.Paths.get_project_file_path(),'asset':row['asset'],
              'source_png_sha256':layout['source_sha256'],'original_texture_and_material_preserved':True,
              'tile_count':layout['tile_count'],'closed_components':validation['closed_components'],
              'triangles':row['triangles'],'saved_normal_errors':validation['saved_normal_errors'],
              'cube_grid_and_periodic_height_reset_removed':True,
              'saved_reopened_gallery':True,'other_44_gallery_meshes_materials_transforms_unchanged':True,
              'roof_transform_unchanged':True,'ground_error_cm':g.actor_bounds(scene[label])['min'][2],
              'user_acceptance':'pending','gameplay_tested':False}
(root/'Docs/Reconstruction'/(doc_stem+'-verification.json')).write_text(json.dumps(verification,indent=2))
unreal.log('ROOF_SURFACE_VERIFIED_AND_GALLERY_SAVED')
