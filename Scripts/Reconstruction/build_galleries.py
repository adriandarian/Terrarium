"""Create five NEW reconstruction galleries from the latest successful receipts.

Run in Terrarium's Unreal editor after all reconstruction builds complete.
Existing gallery maps are never overwritten. The current ReviewStage is saved
before switching maps and restored afterward. No recipe or existing actor is edited.
"""
import json
import math
import traceback
from pathlib import Path
import unreal

PKG='/Game/Terrarium/Reconstruction'
REVIEW=PKG+'/Maps/ReviewStage'
ROOT=Path(unreal.Paths.project_dir())
OUT=ROOT/'Docs/Reconstruction/Galleries'
LEVELS=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ACTORS=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
CURRENT_NEW_MAP=None
TOLERANCE_CM=.02

GROUPS={
    'Architecture':{'expected':7,'columns':3,'gap':210,'label_size':23,'keys':[
        ('architecture',key) for key in ('lodge','cottage','civic_hall','market_stall','lantern','sign')]+[('compound','homestead_compound')]},
    'Characters':{'expected':5,'columns':5,'gap':100,'label_size':13,'keys':[
        ('humanoids','player_front'),('humanoids','ranger_sela'),
        ('creatures_items','brambit'),('creatures_items','kindlehorn'),('creatures_items','rillip')]},
    'Collectibles':{'expected':8,'columns':4,'gap':85,'label_size':10,'keys':[
        ('creatures_items',key) for key in ('moss_tonic','trail_prism','grove','ember','tide','storm','ember_crest','deep_delver_mark')]},
    'Environment':{'expected':7,'columns':3,'gap':180,'label_size':19,'keys':[
        ('environment',key) for key in ('tree','homestead_tree_v2','meadow_shrub','rock','wheat_field','homestead_riverbank_v2','river_crossing')]},
    'Surfaces':{'expected':45,'columns':9,'gap':75,'label_size':7,'keys':[]},
}


def package_path(obj):
    return obj.get_path_name().split('.')[0]


def current_is(path):
    return path+'.' in str(LEVELS.get_current_level()) or path+':' in str(LEVELS.get_current_level())


def require_new_map():
    assert CURRENT_NEW_MAP and CURRENT_NEW_MAP in [PKG+'/Maps/'+g for g in GROUPS]
    assert current_is(CURRENT_NEW_MAP),('Refusing actor edit outside the newly created gallery',str(LEVELS.get_current_level()))


def spawn(cls,label,pos=(0,0,0),rot=(0,0,0),folder='Studio'):
    require_new_map()
    actor=ACTORS.spawn_actor_from_class(cls,unreal.Vector(*pos),unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]))
    assert actor,label
    actor.set_actor_label(label)
    actor.set_folder_path('Reconstruction/'+folder)
    return actor


def vector_list(v):
    return [v.x,v.y,v.z]


def actor_bounds(actor):
    origin,extent=actor.get_actor_bounds(False)
    return {'min':[origin.x-extent.x,origin.y-extent.y,origin.z-extent.z],
            'max':[origin.x+extent.x,origin.y+extent.y,origin.z+extent.z]}


def material_paths(mesh):
    slots=mesh.get_editor_property('static_materials')
    assert slots,('Mesh has no material slots',mesh.get_path_name())
    paths=[]
    for i,slot in enumerate(slots):
        material=slot.get_editor_property('material_interface')
        assert material,('Empty material slot',mesh.get_path_name(),i)
        path=package_path(material)
        assert unreal.EditorAssetLibrary.does_asset_exist(path),('Missing material',path)
        paths.append(path)
    return paths


def select_receipts():
    source_rows=json.loads((ROOT/'Docs/Reconstruction/surfaces-source.json').read_text())
    names=sorted(row['name'] for row in source_rows)
    assert len(names)==45 and len(set(names))==45,('Expected 45 distinct surface sources',len(names))
    GROUPS['Surfaces']['keys']=[('surfaces',name) for name in names]
    expected={pair for config in GROUPS.values() for pair in config['keys']}
    assert len(expected)==72
    latest={}
    for path in sorted((ROOT/'Docs/Reconstruction/Builds').glob('*.json')):
        row=json.loads(path.read_text())
        pair=(row.get('module'),row.get('key'))
        if pair not in expected:continue
        revision=int(row.get('revision',1))
        assert revision>0 and row.get('saved_normal_errors')==0,('Invalid build receipt',str(path))
        asset=row.get('asset','')
        assert asset.startswith(PKG+'/Meshes/SM_Recon_'),('Unexpected asset path',asset)
        assert int(row.get('triangles',0))>0,('Empty mesh receipt',str(path))
        row=dict(row,receipt=str(path.relative_to(ROOT)),revision=revision)
        previous=latest.get(pair)
        if previous and previous['revision']==revision:
            assert previous['asset']==asset,('Ambiguous same-revision receipts',pair,revision)
        if not previous or revision>previous['revision']:latest[pair]=row
    missing=sorted(expected-set(latest))
    assert not missing,('Required reconstruction receipts are missing; no maps created',missing)
    selected={}
    for category,config in GROUPS.items():
        rows=[latest[pair] for pair in config['keys']]
        assert len(rows)==config['expected']
        for row in rows:
            assert unreal.EditorAssetLibrary.does_asset_exist(row['asset']),row['asset']
            asset=unreal.load_asset(row['asset'])
            assert isinstance(asset,unreal.StaticMesh),row['asset']
            row['preflight_materials']=material_paths(asset)
        selected[category]=rows
    return selected


def add_label(text,actor_label,pos,size):
    # Text is flat on the studio floor, facing the front viewing side.
    actor=spawn(unreal.TextRenderActor,actor_label,pos,(90,-90,0),'Labels')
    actor.text_render.set_text(text)
    actor.text_render.set_world_size(size)
    actor.text_render.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    actor.text_render.set_text_render_color(unreal.Color(225,222,211,255))
    return actor


def studio(category,bounds,max_height):
    floor_mat=unreal.load_asset(PKG+'/Materials/M_StudioFloor')
    assert floor_mat,'The reconstruction studio floor material must already exist'
    cx=(bounds['min'][0]+bounds['max'][0])/2;cy=(bounds['min'][1]+bounds['max'][1])/2
    width=bounds['max'][0]-bounds['min'][0]+360
    depth=bounds['max'][1]-bounds['min'][1]+360
    floor=spawn(unreal.StaticMeshActor,'GalleryStudioFloor',(cx,cy,-10))
    floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
    floor.static_mesh_component.set_material(0,floor_mat)
    floor.set_actor_scale3d(unreal.Vector(width/100,depth/100,.2))
    floor_bounds=actor_bounds(floor)
    assert abs(floor_bounds['max'][2])<TOLERANCE_CM,('Floor top is not ground zero',floor_bounds)
    # Broad key plus shadowless opposing fills retain deep window/belfry detail.
    lights=[('Key',3.2,(-42,115,0),(1.0,.96,.90),True),
            ('FrontFill',1.5,(-20,55,0),(.93,.96,1.0),False),
            ('BackFill',1.6,(-32,-65,0),(.94,.97,1.0),False),
            ('Rim',1.0,(-48,-145,0),(1.0,.98,.94),False)]
    for label,intensity,rotation,rgb,shadows in lights:
        light=spawn(unreal.DirectionalLight,'Gallery'+label,(cx,cy,max_height+500),rotation)
        component=light.light_component
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_intensity(intensity)
        component.set_light_color(unreal.LinearColor(*rgb,1))
        component.set_editor_property('light_source_angle',12.0)
        component.set_editor_property('cast_shadows',shadows)
    pp=spawn(unreal.PostProcessVolume,'GalleryFixedExposure')
    pp.set_editor_property('unbound',True)
    settings=pp.get_editor_property('settings')
    for key,value in [('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL),
                      ('auto_exposure_apply_physical_camera_exposure',False),
                      ('auto_exposure_bias',0.0),('motion_blur_amount',0.0),
                      ('bloom_intensity',0.0),('vignette_intensity',0.0),
                      ('ambient_occlusion_intensity',.25),('ambient_occlusion_radius',12.0)]:
        settings.set_editor_property('override_'+key,True)
        settings.set_editor_property(key,value)
    pp.set_editor_property('settings',settings)
    # An explicitly labeled overview camera is saved with each map.
    distance=max(width,depth,max_height*2.0)*1.45
    target=unreal.Vector(cx,cy,max_height*.24)
    pitch,yaw=-37,105
    direction=unreal.Vector(math.cos(math.radians(pitch))*math.cos(math.radians(yaw)),
                           math.cos(math.radians(pitch))*math.sin(math.radians(yaw)),math.sin(math.radians(pitch)))
    location=target-direction*distance
    camera=spawn(unreal.CameraActor,'GalleryOverviewCamera',vector_list(location),(pitch,yaw,0))
    camera.camera_component.set_editor_property('field_of_view',55.0)
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
    return {'floor_top_z_cm':floor_bounds['max'][2],'floor_material':package_path(floor_mat),
            'camera_label':camera.get_actor_label(),'lights':[{'label':'Gallery'+v[0],'intensity':v[1],'casts_shadows':v[4]} for v in lights],
            'exposure':'fixed manual, physical camera exposure disabled','visual_acceptance':'not_asserted'}


def create_category(category,rows):
    global CURRENT_NEW_MAP
    path=PKG+'/Maps/'+category
    assert not unreal.EditorAssetLibrary.does_asset_exist(path),('Map already exists',path)
    assert LEVELS.new_level(path),path
    CURRENT_NEW_MAP=path
    require_new_map()
    config=GROUPS[category]
    objects=[]
    for index,row in enumerate(rows):
        label='Model_'+row['key']+'_R'+str(row['revision'])
        actor=spawn(unreal.StaticMeshActor,label,folder=category+'/Models')
        actor.static_mesh_component.set_static_mesh(unreal.load_asset(row['asset']))
        actor.set_actor_scale3d(unreal.Vector(1,1,1))
        bounds=actor_bounds(actor)
        assert all(math.isfinite(v) for side in bounds.values() for v in side)
        size=[bounds['max'][i]-bounds['min'][i] for i in range(3)]
        assert all(v>0 for v in size),(label,size)
        objects.append({'actor':actor,'row':row,'label':label,'local_bounds':bounds,'size':size,'index':index})
    gap=config['gap'];columns=config['columns'];y_cursor=0;placement=[]
    for row_start in range(0,len(objects),columns):
        line=objects[row_start:row_start+columns]
        width=sum(v['size'][0] for v in line)+gap*(len(line)-1)
        depth=max(v['size'][1] for v in line)
        x_cursor=-width/2
        for item in line:
            local=item['local_bounds'];size=item['size'];actor=item['actor']
            x_center=x_cursor+size[0]/2;y_center=y_cursor+depth/2
            translation=(x_center-(local['min'][0]+local['max'][0])/2,
                         y_center-(local['min'][1]+local['max'][1])/2,-local['min'][2])
            require_new_map();actor.set_actor_location(unreal.Vector(*translation),False,False)
            world=actor_bounds(actor)
            assert abs(world['min'][2])<TOLERANCE_CM,(item['label'],'not grounded',world['min'][2])
            text=item['row']['key'].replace('_',' ')+'  |  R'+str(item['row']['revision'])
            label_actor='Label_'+item['row']['key']
            label_location=(x_center,world['min'][1]-32,.3)
            add_label(text,label_actor,label_location,config['label_size'])
            placement.append({'source':item['row']['source'],'key':item['row']['key'],
                'module':item['row']['module'],'revision':item['row']['revision'],
                'receipt':item['row']['receipt'],'label':item['label'],'text_actor':label_actor,
                'text':text,'mesh':item['row']['asset'],'materials':material_paths(actor.static_mesh_component.static_mesh),
                'location_cm':vector_list(actor.get_actor_location()),'scale':[1,1,1],
                'world_bounds_cm':world,'ground_error_cm':world['min'][2],
                'label_location_cm':list(label_location),'triangles':item['row']['triangles']})
            x_cursor+=size[0]+gap
        y_cursor+=depth+gap+35
    # Independent AABB separation check, including mixed-size architectural models.
    for i,left in enumerate(placement):
        for right in placement[i+1:]:
            a=left['world_bounds_cm'];b=right['world_bounds_cm']
            overlaps=all(a['min'][axis]<b['max'][axis] and b['min'][axis]<a['max'][axis] for axis in (0,1))
            assert not overlaps,('Model footprints overlap',left['label'],right['label'])
    bounds={'min':[min(r['world_bounds_cm']['min'][i] for r in placement) for i in range(3)],
            'max':[max(r['world_bounds_cm']['max'][i] for r in placement) for i in range(3)]}
    bounds['min'][1]-=70
    studio_report=studio(category,bounds,bounds['max'][2])
    assert LEVELS.save_current_level(),path
    # Validate serialized actors by reopening the new map, not just transient objects.
    objects=[]
    assert LEVELS.load_level(path),path
    require_new_map()
    all_actors=ACTORS.get_all_level_actors()
    labels=[a.get_actor_label() for a in all_actors]
    assert len(labels)==len(set(labels)),('Duplicate actor labels',path)
    scene={a.get_actor_label():a for a in all_actors}
    models=[a for a in all_actors if a.get_actor_label().startswith('Model_')]
    text_labels=[a for a in all_actors if a.get_actor_label().startswith('Label_')]
    assert len(models)==config['expected']==len(placement),(category,'model count',len(models))
    assert len(text_labels)==config['expected'],(category,'label count',len(text_labels))
    for record in placement:
        actor=scene[record['label']]
        sm=actor.static_mesh_component.static_mesh
        assert package_path(sm)==record['mesh'],record['label']
        assert record['text_actor'] in scene,record['text_actor']
        bounds=actor_bounds(actor)
        assert abs(bounds['min'][2])<TOLERANCE_CM,(record['label'],'reopened ground',bounds)
        assert material_paths(sm)==record['materials'],record['label']
        scale=actor.get_actor_scale3d()
        assert all(abs(v-1)<1e-6 for v in vector_list(scale)),record['label']
        record['reopened_ground_error_cm']=bounds['min'][2]
    assert unreal.EditorAssetLibrary.does_asset_exist(path),path
    report={'map':path,'category':category,'expected_models':config['expected'],
        'saved_reopened_model_count':len(models),'saved_reopened_label_count':len(text_labels),
        'all_meshes_and_materials_exist':True,'all_model_footprints_separate':True,
        'ground_tolerance_cm':TOLERANCE_CM,'all_models_grounded':True,
        'native_validation':'saved map reopened; actor counts, mesh paths, materials, scale and actual bounds verified',
        'visual_acceptance':'not_asserted','studio':studio_report,'models':placement}
    (OUT/(category+'.json')).write_text(json.dumps(report,indent=2))
    unreal.log('RECON_GALLERY_SAVED '+path+' models='+str(len(models)))
    return report


def main():
    global CURRENT_NEW_MAP
    assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
    assert current_is(REVIEW),('Open reconstruction ReviewStage before gallery creation',str(LEVELS.get_current_level()))
    # All inputs and destination conflicts are checked before any level mutation.
    selected=select_receipts()
    for category in GROUPS:
        path=PKG+'/Maps/'+category
        assert not unreal.EditorAssetLibrary.does_asset_exist(path),('Existing gallery; refusing to overwrite',path)
        assert not (OUT/(category+'.json')).exists(),('Existing gallery receipt; inspect before running',category)
    assert unreal.EditorAssetLibrary.does_asset_exist(PKG+'/Materials/M_StudioFloor')
    assert LEVELS.save_current_level(),'Could not preserve ReviewStage'
    assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(),'Other unsaved maps remain; no galleries created'
    OUT.mkdir(parents=True,exist_ok=True)
    reports=[];failure=None
    try:
        LEVELS.eject_pilot_level_actor()
        for category in GROUPS:reports.append(create_category(category,selected[category]))
    except Exception:
        failure=traceback.format_exc()
        raise
    finally:
        CURRENT_NEW_MAP=None
        restored=LEVELS.load_level(REVIEW)
        summary={'project':unreal.Paths.get_project_file_path(),'review_stage_preserved_first':True,
            'review_stage_restored':bool(restored),'maps':[r['map'] for r in reports],
            'model_count':sum(r['saved_reopened_model_count'] for r in reports),
            'expected_total_models':72,'completed':len(reports)==5 and failure is None,
            'visual_acceptance':'not_asserted','failure':failure}
        (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
        assert restored,'Gallery work finished but ReviewStage could not be restored'


if __name__=='__main__':main()
