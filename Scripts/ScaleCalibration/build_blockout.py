"""Run through Terrarium Unreal MCP. Creates one NEW isolated scale blockout.

No asset migration, original-world edits, duplicate-map call, or automatic save
of another map. A dirty editor or an existing destination aborts before edits.
"""
import json
import math
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve()
assert Path(unreal.Paths.get_project_file_path()).stem == 'Terrarium'
assert (ROOT / 'Terrarium.uproject').is_file()
OUT = ROOT / 'Docs/ScaleCalibration'
DATA = json.loads((OUT / 'targets.json').read_text(encoding='utf-8'))
PACKAGE = '/Game/Terrarium/Calibration'
LEVEL = PACKAGE + '/Maps/ConceptScaleBlockout'
ASSETS = PACKAGE + '/ScaleBlockout'
LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'Dirty maps: preserve them before running; nothing changed.'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'Dirty content: preserve it before running; nothing changed.'
assert not unreal.EditorAssetLibrary.does_asset_exist(LEVEL), 'Blockout exists: inspect it, do not overwrite.'
assert not unreal.EditorAssetLibrary.does_directory_exist(ASSETS), 'Partial blockout assets exist: inspect the previous failure before retrying.'
PREVIOUS_LEVEL = str(LEVELS.get_current_level())
assert LEVELS.new_level(LEVEL)
assert LEVEL + '.' in str(LEVELS.get_current_level())

W, H = DATA['image_size_px']
S = DATA['camera_convention']['world_units_per_pixel']
K = math.sqrt(.5)
ELEVATIONS = DATA['scale_convention']['terrace_heights']
RECORDS = []
MATERIALS = {}
PALETTE = {'stone':(.25,.22,.16), 'grass':(.24,.29,.095), 'upper':(.30,.34,.12),
           'landing':(.27,.32,.115), 'path':(.53,.39,.20), 'water':(.035,.20,.22),
           'wall':(.61,.49,.30), 'roof':(.46,.14,.055), 'teal':(.055,.26,.24),
           'wood':(.21,.105,.045), 'wheat':(.56,.40,.10), 'garden':(.16,.27,.075),
           'person':(.73,.34,.065), 'leaf':(.12,.22,.055)}


def world(px, py, z):
    right = (px-W/2)*S
    forward = ((H/2-py)*S-K*z)/K
    return (-K*right-K*forward, -K*right+K*forward, z)


def pixel(v):
    x,y,z = v
    return (W/2+(-K*x-K*y)/S, H/2-(K*(-K*x+K*y)+K*z)/S)


def spawn(cls, label, position=(0,0,0), rotation=(0,0,0)):
    assert LEVEL + '.' in str(LEVELS.get_current_level())
    a = ACTORS.spawn_actor_from_class(cls, unreal.Vector(*position),
        unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]))
    assert a, label
    a.set_actor_label('Scale_' + label)
    a.set_folder_path('Calibration/ScaleBlockout')
    return a


def material(key):
    if key in MATERIALS:
        return MATERIALS[key]
    m = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        'M_Scale_'+key, ASSETS+'/Materials', unreal.Material, unreal.MaterialFactoryNew())
    assert m
    lib = unreal.MaterialEditingLibrary
    n = lib.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -250, 0)
    n.set_editor_property('constant', unreal.LinearColor(*PALETTE[key], 1))
    assert lib.connect_material_property(n, '', unreal.MaterialProperty.MP_BASE_COLOR)
    for prop, value in [(unreal.MaterialProperty.MP_ROUGHNESS,.95), (unreal.MaterialProperty.MP_SPECULAR,0.0)]:
        n = lib.create_material_expression(m, unreal.MaterialExpressionConstant, -250, 200)
        n.set_editor_property('r', value)
        assert lib.connect_material_property(n, '', prop)
    lib.recompile_material(m)
    assert unreal.EditorAssetLibrary.save_loaded_asset(m)
    MATERIALS[key] = m
    return m


def cross2(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def triangulate(poly):
    """Ear-clip a simple counterclockwise XY polygon, preserving concave edges."""
    indices = list(range(len(poly)))
    if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in indices)<0:
        indices.reverse()
    result=[]
    while len(indices)>3:
        for j,b in enumerate(indices):
            a,c=indices[j-1],indices[(j+1)%len(indices)]
            if cross2(poly[a],poly[b],poly[c])<=1e-7:
                continue
            if any(all(t>=-1e-7 for t in [cross2(poly[a],poly[b],poly[p]),cross2(poly[b],poly[c],poly[p]),cross2(poly[c],poly[a],poly[p])]) for p in indices if p not in (a,b,c)):
                continue
            result.append((a,b,c));indices.pop(j);break
        else:
            raise ValueError('Cannot triangulate simple terrace polygon')
    result.append(tuple(indices))
    return result


def mesh(label, verts, faces, key):
    triangles=[]
    for face in faces:
        triangles.extend((face[0], face[i], face[i+1]) for i in range(1,len(face)-1))
    dynamic = unreal.DynamicMesh()
    buffers = unreal.GeometryScriptSimpleMeshBuffers()
    buffers.vertices = [unreal.Vector(*v) for v in verts]
    # Project meshkit uses clockwise winding for Geometry Script.
    buffers.triangles = [unreal.IntVector(a,c,b) for a,b,c in triangles]
    buffers.uv0 = [unreal.Vector2D(v[0]/100,v[1]/100) for v in verts]
    dynamic.append_buffers_to_mesh(buffers)
    unreal.GeometryScript_Normals.set_per_face_normals(dynamic)
    assert unreal.GeometryScript_MeshQueries.get_is_closed_mesh(dynamic), label
    options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=False,
        enable_recompute_normals=False, enable_recompute_tangents=False)
    asset,outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(
        dynamic, ASSETS+'/Meshes/SM_'+label, options)
    assert asset and outcome == unreal.GeometryScriptOutcomePins.SUCCESS, label
    asset.set_material(0, material(key))
    assert unreal.EditorAssetLibrary.save_loaded_asset(asset)
    actor = spawn(unreal.StaticMeshActor, label)
    actor.static_mesh_component.set_static_mesh(asset)
    points = [pixel(v) for v in verts]
    RECORDS.append({'label':label,'triangles':len(triangles),'closed':True,
        'projected_bounds_px':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]})
    return actor


def prism(label, points, top, bottom, key):
    """points are projected at top; bottom retains exactly the same world XY."""
    xy=[world(x,y,top) for x,y in points]
    if sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))<0:
        xy.reverse()
    n=len(xy)
    verts=[(x,y,bottom) for x,y,z in xy]+xy
    tris=triangulate(xy)
    faces=[tuple(reversed(t)) for t in tris]+[tuple(i+n for i in t) for t in tris]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(label,verts,faces,key)


def raised_prism(label, footprint, base, height, key):
    return prism(label,[(x,y-K*height/S) for x,y in footprint],base+height,base,key)


def ribbon(label, points, base, width_px, height, key):
    # Width is a screen-space footprint measure; inverse projection yields
    # the corresponding world-ground width for each segment orientation.
    for i,(a,b) in enumerate(zip(points,points[1:])):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        nx,ny=-dy/length*width_px/2,dx/length*width_px/2
        poly=[(a[0]+nx,a[1]+ny),(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny)]
        raised_prism(label+'_'+str(i),poly,base,height,key)


prism('Water', [(-180,-180),(660,-180),(660,990),(-180,990)], 0, -30, 'water')
for terrace in DATA['terraces']:
    name=terrace['id'];top=terrace['top'];poly=terrace['polygon_px']
    prism('Terrace_'+name,poly,top-2,terrace['bottom']-1,'stone')
    prism('Turf_'+name,poly,top,top-3,name if name in ('upper','landing') else 'grass')
for path in DATA['paths']:
    ribbon('Path_'+path['id'],path['points_px'],ELEVATIONS[path['level']]+1,path['width_px'],2,'path')

OBJECTS={o['id']:o for o in DATA['objects']}
for name in ('cottage','shed'):
    obj=OBJECTS[name];foot=obj['footprint_px'];base=ELEVATIONS[obj['level']]
    height=obj['wall_height'];rise=obj['roof_rise']
    raised_prism(name+'_walls',foot,base,height,'wall' if name=='cottage' else 'wood')
    ground=[world(x,y,base) for x,y in foot]
    cx=sum(v[0] for v in ground)/4;cy=sum(v[1] for v in ground)/4
    eaves=[(cx+(x-cx)*1.13,cy+(y-cy)*1.13,base+height) for x,y,z in ground]
    ridges=[((eaves[a][0]+eaves[b][0])/2,(eaves[a][1]+eaves[b][1])/2,base+height+rise) for a,b in ((0,1),(3,2))]
    verts=eaves+ridges
    faces=[[0,1,4],[3,5,2],[0,4,5,3],[4,1,2,5],[0,3,2,1]]
    # Convex roof outward orientation independent of footprint order.
    center=[sum(v[k] for v in verts)/len(verts) for k in range(3)]
    oriented=[]
    for f in faces:
        a,b,c=[verts[i] for i in f[:3]]
        u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
        normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        oriented.append(f if sum(normal[k]*(a[k]-center[k]) for k in range(3))>0 else list(reversed(f)))
    mesh(name+'_roof',verts,oriented,'roof' if name=='cottage' else 'teal')
    if name=='cottage':
        raised_prism('cottage_chimney',[(226,288),(235,293),(244,288),(235,283)],base,505,'stone')

for name,key in [('wheat','wheat'),('garden','garden'),('bridge','wood')]:
    obj=OBJECTS[name]
    raised_prism(name,obj['footprint_px'],ELEVATIONS[obj['level']]+3,obj['height'],key)
yard=OBJECTS['fenced_yard']
ribbon('Fence',yard['footprint_px'],ELEVATIONS['main'],2.2,yard['height'],'wood')
bridge=OBJECTS['bridge']
for side in ((0,3),(1,2)):
    ribbon('BridgeRail'+str(side[0]),[bridge['footprint_px'][i] for i in side],ELEVATIONS['landing']+15,1.5,30,'wood')

stair=OBJECTS['stairs'];a,b=stair['top_edge_px'];c,d=stair['bottom_edge_px']
def lerp(p,q,t):return tuple(p[k]+(q[k]-p[k])*t for k in range(len(p)))
# Ground endpoints are independently projected at their respective elevations.
tl,tr=world(*a,560),world(*b,560);bl,br=world(*c,280),world(*d,280)
for i in range(8):
    z=560-i*35
    v=[lerp(tl,bl,i/8),lerp(tr,br,i/8),lerp(tr,br,(i+1)/8),lerp(tl,bl,(i+1)/8)]
    prism('Stair_'+str(i),[pixel((p[0],p[1],z)) for p in v],z,279,'stone')

# Person is a static scale marker, not a character or gameplay system.
person=OBJECTS['person'];px,py=person['anchor_px'];base=ELEVATIONS['main']
raised_prism('Person_body',[(px-5,py-2),(px,py+1),(px+5,py-2),(px,py-5)],base,145,'person')
raised_prism('Person_head',[(x,y-145*K/S) for x,y in [(px-5,py-2),(px,py+1),(px+5,py-2),(px,py-5)]],base+145,35,'wall')

for tree in DATA['tree_clusters']:
    px,py=tree['anchor_px'];left,top,right,bottom=tree['bounds_px'];base=ELEVATIONS[tree['level']]
    height=(py-top)*S/K
    raised_prism('Tree_'+tree['id']+'_trunk',[(px-2,py),(px,py+1),(px+2,py),(px,py-1)],base,height*.58,'wood')
    # Three low-poly ellipsoids describe a cluster envelope, no leaf microblocks.
    for j,(offset,factor) in enumerate([(-.21,.65),(.22,.67),(0,.76)]):
        cx=(left+right)/2+offset*(right-left)
        cy=top+(py-top)*(.38 if j==2 else .50)
        z=base+height*(.59 if j==2 else .45)
        a=spawn(unreal.StaticMeshActor,'Tree_'+tree['id']+'_crown_'+str(j),world(cx,cy,z))
        a.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Sphere'))
        diameter=(right-left)*S*factor
        a.set_actor_scale3d(unreal.Vector(diameter/100,diameter/100,height*.52/100))
        a.static_mesh_component.set_material(0,material('leaf'))

sun=spawn(unreal.DirectionalLight,'WarmSun',(0,0,800),(-48,-155,0))
sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sun.light_component.set_intensity(30000)
sun.light_component.set_light_color(unreal.LinearColor(1,.90,.76,1))
sun.light_component.set_editor_property('light_source_angle',6.0)
sun.light_component.set_editor_property('atmosphere_sun_light',True)
spawn(unreal.SkyAtmosphere,'SkyAtmosphere')
sky=spawn(unreal.SkyLight,'SkyLight',(0,0,500))
sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
sky.light_component.set_editor_property('real_time_capture',True)
sky.light_component.set_intensity(2.0)
pp=spawn(unreal.PostProcessVolume,'FixedExposure')
pp.set_editor_property('unbound',True)
settings=pp.get_editor_property('settings')
for key,value in [('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL),
        ('auto_exposure_apply_physical_camera_exposure',True),('camera_iso',100.0),
        ('camera_shutter_speed',64.0),('depth_of_field_fstop',8.0),('auto_exposure_bias',0.0),
        ('dynamic_global_illumination_method',unreal.DynamicGlobalIlluminationMethod.LUMEN),
        ('reflection_method',unreal.ReflectionMethod.LUMEN),('motion_blur_amount',0.0),
        ('vignette_intensity',0.0),('bloom_intensity',0.0)]:
    settings.set_editor_property('override_'+key,True)
    settings.set_editor_property(key,value)
pp.set_editor_property('settings',settings)

camera=spawn(unreal.CameraActor,'ConceptCamera',(3250,-3250,4596.1940777),(-45,135,0))
cc=camera.camera_component
cc.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC)
cc.set_ortho_width(W*S)
cc.set_editor_property('aspect_ratio',W/H)
cc.set_editor_property('constrain_aspect_ratio',True)
cc.set_editor_property('post_process_blend_weight',0.0)
LEVELS.pilot_level_actor(camera)
LEVELS.set_exact_camera_view(True)
LEVELS.editor_set_game_view(True)
ACTORS.set_selected_level_actors([])
assert LEVELS.save_current_level(), 'No completion receipt written: level save failed'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
receipt={'level':LEVEL,'previous_level':PREVIOUS_LEVEL,'camera_actor':camera.get_path_name(),
    'camera_location':[3250,-3250,4596.1940777],'camera_rotation':[-45,135,0],
    'projection':'orthographic','ortho_width':W*S,'aspect_ratio':W/H,'capture_size':[W,H],
    'person_height_convention':180,'saved':True,'visual_approval':'pending',
    'actor_count':len(ACTORS.get_all_level_actors()),'generated_meshes':RECORDS,
    'scope':'new calibration level and its own primitive assets only'}
(OUT/'blockout-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
capture={'captureTransform':{'location':{'x':3250,'y':-3250,'z':4596.1940777},
    'rotation':{'pitch':-45,'yaw':135,'roll':0},'scale':{'x':1,'y':1,'z':1}},
    'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,
        'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(OUT/'capture-args.json').write_text(json.dumps(capture,indent=2),encoding='utf-8')
unreal.log('TERRARIUM_CONCEPT_SCALE_BLOCKOUT_SAVED '+LEVEL)
