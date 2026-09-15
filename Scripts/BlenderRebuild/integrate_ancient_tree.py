"""Place the ancient tree in verified open meadow north-east of the civic hall."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world_path='/Game/Terrarium/Blender/Maps/HomesteadBlender';assert world_path+'.' in str(levels.get_current_level())
key='AncientTree';folder=root/'Docs/BlenderRebuild'/key
mesh=unreal.load_asset('/Game/Terrarium/Blender/'+key+'/SM_Blender_'+key);assert mesh
site=json.loads((root/'Saved/blender-site-AncientTree.json').read_text())
ground=[p['position'] for c in site['instances'] if c['mesh']=='SM_Env_MeadowTile' for p in c['instances']]
assert ground and not site['static_actors']
# A three-by-three footprint check stays within the nominal 560 cm terrace.
checks=[]
for dx in [-90,0,90]:
    for dy in [-90,0,90]:
        p=(564+dx,1792+dy);g=min(ground,key=lambda g:math.dist(p,g[:2]))
        assert abs(g[0]-p[0])<=36 and abs(g[1]-p[1])<=36 and abs(g[2]-560)<.02
        checks.append({'xy_cm':list(p),'support_tile_cm':g})
scale=.85;base_z=560-1.1-mesh.get_bounding_box().min.z*scale;pos=(564,1792,base_z)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};label='Blender_AncientTree_NorthMeadow'
ob=scene.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));ob.set_actor_label(label)
ob.static_mesh_component.set_static_mesh(mesh);ob.static_mesh_component.set_editor_property('override_materials',[])
ob.set_actor_location(unreal.Vector(*pos),False,False);ob.set_actor_scale3d(unreal.Vector(scale,scale,scale));ob.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),False)
ob.tags=[unreal.Name('BlenderRebuild'),unreal.Name('FidelityReviewPending')];ob.set_folder_path('Blender/Environment')
center,extent=ob.get_actor_bounds(False)
camlabel='Blender_AncientTree_Review';cam=scene.get(camlabel) or actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
cam.set_actor_label(camlabel);focus=center;cam.set_actor_location(focus+unreal.Vector(850,-1150,720),False,False)
cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),focus),False)
c=cam.get_component_by_class(unreal.CameraComponent);c.set_editor_property('projection_mode',unreal.CameraProjectionMode.PERSPECTIVE);c.set_editor_property('field_of_view',32)
actors.set_selected_level_actors([]);levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);assert levels.save_current_level()
record={'asset':key,'actor':label,'mesh':mesh.get_path_name(),'location_cm':list(pos),'scale':scale,'yaw':180,'world':world_path,'camera':camlabel,'bounds_center':[center.x,center.y,center.z],'bounds_extent':[extent.x,extent.y,extent.z],'status':'placed_pending_visual_refinement','site':'Open meadow northeast of civic hall; no original ancient tree instance existed in this world; no plants moved','root_base_below_nominal_meadow_cm':1.1,'support_checks':checks}
(folder/'world-placement.json').write_text(json.dumps(record,indent=2))
p=cam.get_actor_location();r=cam.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/blender-ancient-tree-capture.json').write_text(json.dumps(args))
