"""Place the authored market beside the upper homestead path."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world_path='/Game/Terrarium/Blender/Maps/HomesteadBlender'
assert world_path+'.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
key='MarketStall';folder=root/'Docs/BlenderRebuild'/key
mesh=unreal.load_asset('/Game/Terrarium/Blender/'+key+'/SM_Blender_'+key);assert mesh
# The central opening must remain passable; a hull around the whole stand would block it.
body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
unreal.EditorAssetLibrary.save_loaded_asset(mesh)
pos=(275,550,560);scale=.8
label='Blender_MarketStall_UpperPath'
ob=scene.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos))
ob.set_actor_label(label);ob.static_mesh_component.set_static_mesh(mesh);ob.static_mesh_component.set_editor_property('override_materials',[])
ob.set_actor_location(unreal.Vector(*pos),False,False);ob.set_actor_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0),False);ob.set_actor_scale3d(unreal.Vector(scale,scale,scale))
ob.tags=[unreal.Name('BlenderRebuild'),unreal.Name('FidelityReviewPending')]
# Relocate the seven plants/rocks that occupied this footing, keeping their transforms recorded.
receipt=folder/'site-relocations.json'
if not receipt.exists():
    moves=[]
    for actor in actors.get_all_level_actors():
        for c in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if not c.static_mesh or c.static_mesh.get_name() not in ['SM_Recon_MeadowShrub_R3','SM_RockCluster_Detail']:continue
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,world_space=True);p=t.translation
                if 105<p.x<465 and 430<p.y<655 and 550<p.z<580:
                    before=[p.x,p.y,p.z];p.x-=250;t.translation=p
                    assert c.update_instance_transform(i,t,world_space=True,mark_render_state_dirty=True,teleport=True)
                    moves.append({'actor':actor.get_actor_label(),'component':c.get_name(),'index':i,'before_cm':before,'after_cm':[p.x,p.y,p.z]})
    receipt.write_text(json.dumps(moves,indent=2))
camera=scene.get('Blender_Market_Review') or actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
camera.set_actor_label('Blender_Market_Review');focus=unreal.Vector(280,550,670)
camera.set_actor_location(focus+unreal.Vector(390,920,450),False,False);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),focus),False)
c=camera.get_component_by_class(unreal.CameraComponent);c.set_editor_property('projection_mode',unreal.CameraProjectionMode.PERSPECTIVE);c.set_editor_property('field_of_view',32)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);assert levels.save_current_level()
center,extent=ob.get_actor_bounds(False)
record={'asset':key,'actor':label,'mesh':mesh.get_path_name(),'location_cm':list(pos),'scale':scale,'yaw':0,'bounds_center':[center.x,center.y,center.z],'bounds_extent':[extent.x,extent.y,extent.z],'world':world_path,'collision':'complex_as_simple','status':'placed_pending_visual_check'}
(folder/'world-placement.json').write_text(json.dumps(record,indent=2))
p=camera.get_actor_location();r=camera.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/blender-market-capture.json').write_text(json.dumps(args))
