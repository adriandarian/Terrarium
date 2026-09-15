"""Bind the latest saved Ember Crest mesh in Collectibles and verify the saved map."""
import json,sys
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir())
assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import build_galleries as g
assert g.current_is(g.REVIEW)
rows=[json.loads(p.read_text()) for p in (root/'Docs/Reconstruction/Builds').glob('SM_Recon_EmberCrest*.json')]
row=max(rows,key=lambda r:r['revision'])
assert row['saved_normal_errors']==0
mesh=unreal.load_asset(row['asset'])
check=unreal.DynamicMesh()
_,outcome=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,check,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD())
assert outcome==unreal.GeometryScriptOutcomePins.SUCCESS
_,colors,valid,gaps=unreal.GeometryScript_VertexColors.get_mesh_per_vertex_colors(check)
assert valid and not gaps
colors=list(unreal.GeometryScript_List.convert_color_list_to_array(colors))
bronze_vertices=sum(c.a>.99 for c in colors)
nonmetal_vertices=sum(c.a<.01 for c in colors)
assert bronze_vertices>0 and nonmetal_vertices>0
assert bronze_vertices+nonmetal_vertices==len(colors)
red_vertices=[c for c in colors if c.r>.5 and c.g<.08]
assert red_vertices and all(c.a<.01 for c in red_vertices)
assert mesh.get_material(0).get_path_name().split('.')[0]=='/Game/Terrarium/Reconstruction/Materials/M_EmberCrest_Patina_R6'
for view in ('front','back'):
    assert (root/'Docs/Reconstruction/Renders'/(row['name']+'-'+view+'.png')).is_file()
# The studio's per-asset lighting and capture setup are temporary; don't save it.
path=g.PKG+'/Maps/Collectibles'
assert g.LEVELS.load_level(path)
scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
before={label:g.package_path(a.static_mesh_component.static_mesh) for label,a in scene.items() if label.startswith('Model_')}
report_path=g.OUT/'Collectibles.json';report=json.loads(report_path.read_text())
record=next(r for r in report['models'] if r['key']=='ember_crest')
old_label=record['label'];a=scene[old_label]
assert before[old_label]==record['mesh']
old_bounds=g.actor_bounds(a)
center=[(old_bounds['min'][i]+old_bounds['max'][i])/2 for i in (0,1)]
a.static_mesh_component.set_static_mesh(unreal.load_asset(row['asset']))
bounds=g.actor_bounds(a);pos=a.get_actor_location()
pos.x+=center[0]-(bounds['min'][0]+bounds['max'][0])/2
pos.y+=center[1]-(bounds['min'][1]+bounds['max'][1])/2
pos.z-=bounds['min'][2];a.set_actor_location(pos,False,False)
label='Model_ember_crest_R'+str(row['revision']);a.set_actor_label(label)
caption='ember crest  |  R'+str(row['revision'])
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
validation['saved_bronze_mask_vertices']=bronze_vertices
validation['saved_nonmetal_mask_vertices']=nonmetal_vertices
validation['red_flame_and_gem_vertices_nonmetal']=True
validation['material']='/Game/Terrarium/Reconstruction/Materials/M_EmberCrest_Patina_R6'
(root/'Docs/Reconstruction/ember-crest-verification.json').write_text(json.dumps(validation,indent=2))
(root/'Saved/gallery-capture.json').write_text(json.dumps({'category':'Collectibles','mode':'capture','restore':False}))
