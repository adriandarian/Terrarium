"""Update only this task's five galleries to latest models; recheck and render."""
import json,sys
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import build_galleries as g
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
assert g.current_is(g.REVIEW)
assert g.LEVELS.save_current_level()
latest=g.select_receipts();reports=[]
try:
    for category,rows in latest.items():
        path=g.PKG+'/Maps/'+category
        report=json.loads((g.OUT/(category+'.json')).read_text())
        assert report['map']==path and report['all_models_grounded']
        assert g.LEVELS.load_level(path);assert g.current_is(path)
        scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
        row_by_key={r['key']:r for r in rows}
        for record in report['models']:
            row=row_by_key[record['key']];a=scene[record['label']]
            before=g.actor_bounds(a);center=[(before['min'][i]+before['max'][i])/2 for i in (0,1)]
            mesh=unreal.load_asset(row['asset']);a.static_mesh_component.set_static_mesh(mesh)
            after=g.actor_bounds(a);pos=a.get_actor_location()
            pos.x+=center[0]-(after['min'][0]+after['max'][0])/2
            pos.y+=center[1]-(after['min'][1]+after['max'][1])/2;pos.z-=after['min'][2]
            a.set_actor_location(pos,False,False)
            label='Model_'+row['key']+'_R'+str(row['revision']);a.set_actor_label(label)
            text=row['key'].replace('_',' ')+'  |  R'+str(row['revision'])
            scene[record['text_actor']].text_render.set_text(text)
            record.update({'label':label,'text':text,'mesh':row['asset'],'revision':row['revision'],'receipt':row['receipt'],
                           'materials':g.material_paths(mesh),'location_cm':g.vector_list(pos),'world_bounds_cm':g.actor_bounds(a),'triangles':row['triangles']})
            assert abs(record['world_bounds_cm']['min'][2])<.02
        scene['GalleryStudioFloor'].set_actor_scale3d(unreal.Vector(1500,1500,.2))
        assert g.LEVELS.save_current_level();assert g.LEVELS.load_level(path)
        scene={a.get_actor_label():a for a in g.ACTORS.get_all_level_actors()}
        assert len([a for label,a in scene.items() if label.startswith('Model_')])==len(rows)
        for record in report['models']:
            a=scene[record['label']];bounds=g.actor_bounds(a)
            assert g.package_path(a.static_mesh_component.static_mesh)==record['mesh']
            assert g.material_paths(a.static_mesh_component.static_mesh)==record['materials']
            assert abs(bounds['min'][2])<.02
            record['ground_error_cm']=record['reopened_ground_error_cm']=bounds['min'][2]
        for i,a in enumerate(report['models']):
            for b in report['models'][i+1:]:
                aa,bb=a['world_bounds_cm'],b['world_bounds_cm']
                assert not all(aa['min'][k]<bb['max'][k] and bb['min'][k]<aa['max'][k] for k in (0,1)),(category,a['key'],b['key'])
        camera=scene['GalleryOverviewCamera'];world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        ca=g.ACTORS.spawn_actor_from_class(unreal.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation())
        component=ca.get_component_by_class(unreal.SceneCaptureComponent2D)
        component.set_editor_property('capture_every_frame',False);component.set_editor_property('capture_on_movement',False)
        component.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        component.set_editor_property('fov_angle',55.0)
        component.set_editor_property('post_process_settings',scene['GalleryFixedExposure'].get_editor_property('settings'))
        component.set_editor_property('post_process_blend_weight',1.0)
        target=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8)
        target.set_editor_property('target_gamma',2.2);component.set_editor_property('texture_target',target)
        try:
            component.capture_scene();unreal.RenderingLibrary.export_render_target(world,target,str(g.OUT.resolve()),category+'.png')
        finally:g.ACTORS.destroy_actor(ca)
        assert g.LEVELS.save_current_level()
        report['latest_revisions_refreshed']=True;report['lit_overview']=category+'.png'
        (g.OUT/(category+'.json')).write_text(json.dumps(report,indent=2));reports.append(report)
finally:
    assert g.LEVELS.load_level(g.REVIEW)
(g.OUT/'latest-validation.json').write_text(json.dumps({'maps':len(reports),'models':sum(len(r['models']) for r in reports),'saved_reopened':True,'ground_tolerance_cm':.02,'all_latest_revisions':True,'overviews_rendered':len(reports)},indent=2))
