"""Bind the latest saved Deep Delver mesh in Collectibles and verify the saved map."""
import json,sys
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir())
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import build_galleries as g
assert g.current_is(g.REVIEW)
rows=[json.loads(p.read_text()) for p in (root/'Docs/Reconstruction/Builds').glob('SM_Recon_DeepDelverMark*.json')]
row=max(rows,key=lambda r:r['revision'])
assert row['saved_normal_errors']==0
for view in ('front','back'):
    assert (root/'Docs/Reconstruction/Renders'/(row['name']+'-'+view+'.png')).is_file()
# The studio's per-asset lighting and capture setup are temporary; don't save it.
path=g.PKG+'/Maps/Collectibles'
assert g.LEVELS.load_level(path)
scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
before={label:g.package_path(a.static_mesh_component.static_mesh) for label,a in scene.items() if label.startswith('Model_')}
report_path=g.OUT/'Collectibles.json';report=json.loads(report_path.read_text())
record=next(r for r in report['models'] if r['key']=='deep_delver_mark')
old_label=record['label'];a=scene[old_label]
assert before[old_label]==record['mesh']
old_bounds=g.actor_bounds(a)
center=[(old_bounds['min'][i]+old_bounds['max'][i])/2 for i in (0,1)]
a.static_mesh_component.set_static_mesh(unreal.load_asset(row['asset']))
bounds=g.actor_bounds(a);pos=a.get_actor_location()
pos.x+=center[0]-(bounds['min'][0]+bounds['max'][0])/2
pos.y+=center[1]-(bounds['min'][1]+bounds['max'][1])/2
pos.z-=bounds['min'][2];a.set_actor_location(pos,False,False)
label='Model_deep_delver_mark_R'+str(row['revision']);a.set_actor_label(label)
caption='deep delver mark  |  R'+str(row['revision'])
scene[record['text_actor']].text_render.set_text(caption)
record.update({'label':label,'text':caption,'mesh':row['asset'],'revision':row['revision'],
 'receipt':'Docs/Reconstruction/Builds/'+row['name']+'.json',
 'materials':g.material_paths(a.static_mesh_component.static_mesh),
 'location_cm':g.vector_list(pos),'world_bounds_cm':g.actor_bounds(a),'triangles':row['triangles']})
assert g.LEVELS.save_current_level();assert g.LEVELS.load_level(path)
scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
assert len([n for n in scene if n.startswith('Model_')])==8
for name,asset in before.items():
    expected=row['asset'] if name==old_label else asset
    assert g.package_path(scene[label if name==old_label else name].static_mesh_component.static_mesh)==expected
a=scene[label]
assert abs(g.actor_bounds(a)['min'][2])<.02
assert g.material_paths(a.static_mesh_component.static_mesh)==record['materials']
record['ground_error_cm']=record['reopened_ground_error_cm']=g.actor_bounds(a)['min'][2]
report_path.write_text(json.dumps(report,indent=2))
validation={'project':unreal.Paths.get_project_file_path(),'asset':row['asset'],'revision':row['revision'],
 'saved_and_reopened_gallery':True,'other_seven_gallery_mesh_bindings_unchanged':True,
 'saved_normal_errors':row['saved_normal_errors'],'triangles':row['triangles'],
 'ground_error_cm':record['ground_error_cm'],'front_back_native_renders_inspected':True,
 'pixel_parity':'not_claimed; material finish and exact block placement still differ',
 'user_acceptance':'pending','gameplay_collision_tested':False}
(root/'Docs/Reconstruction/deep-delver-verification.json').write_text(json.dumps(validation,indent=2))
(root/'Saved/gallery-capture.json').write_text(json.dumps({'category':'Collectibles','mode':'capture','restore':False}))
