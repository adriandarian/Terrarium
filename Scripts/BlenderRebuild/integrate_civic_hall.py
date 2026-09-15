"""Place the civic hall facing the northern path, preserving the walking route."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world_path='/Game/Terrarium/Blender/Maps/HomesteadBlender';assert world_path+'.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};key='CivicHall';folder=root/'Docs/BlenderRebuild'/key
mesh=unreal.load_asset('/Game/Terrarium/Blender/CivicHall/SM_Blender_CivicHall');assert mesh
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
pos=(-450,1400,560);scale=.85;label='Blender_CivicHall_NorthPath'
ob=scene.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));ob.set_actor_label(label)
ob.static_mesh_component.set_static_mesh(mesh);ob.static_mesh_component.set_editor_property('override_materials',[])
ob.set_actor_location(unreal.Vector(*pos),False,False);ob.set_actor_scale3d(unreal.Vector(scale,scale,scale));ob.set_actor_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0),False)
ob.tags=[unreal.Name('BlenderRebuild'),unreal.Name('FidelityReviewPending')]
center,extent=ob.get_actor_bounds(False);assert abs(center.z-extent.z-560)<.02
# Keep grass and shrub instances, moving the ones under the new footprint into two front pockets.
receipt=folder/'site-relocations.json'
if not receipt.exists():
    moves=[];counts=[0,0]
    eligible={'SM_MeadowGrass_v2_Detail','SM_GroundPlants_v2_Detail','SM_MeadowFlowers_v2_Detail','SM_Recon_MeadowShrub_R3','SM_RockCluster_Detail'}
    for actor in actors.get_all_level_actors():
        for c in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if not c.static_mesh or c.static_mesh.get_name() not in eligible:continue
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,world_space=True);p=t.translation
                if -790<p.x<-110 and 1235<p.y<1560 and 550<p.z<580:
                    before=[p.x,p.y,p.z];side=0 if p.x<-450 else 1;k=counts[side];counts[side]+=1
                    p.x=(-690 if side==0 else -205)+(k%4-1.5)*22;p.y=1558+(k//4)*18;t.translation=p
                    assert c.update_instance_transform(i,t,world_space=True,mark_render_state_dirty=True,teleport=True)
                    moves.append({'actor':actor.get_actor_label(),'component':c.get_name(),'index':i,'before_cm':before,'after_cm':[p.x,p.y,p.z]})
    receipt.write_text(json.dumps(moves,indent=2))
camera=scene.get('Blender_CivicHall_Review') or actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
camera.set_actor_label('Blender_CivicHall_Review');focus=unreal.Vector(center.x,center.y,center.z)
camera.set_actor_location(focus+unreal.Vector(850,2700,1250),False,False);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),focus),False)
c=camera.get_component_by_class(unreal.CameraComponent);c.set_editor_property('projection_mode',unreal.CameraProjectionMode.PERSPECTIVE);c.set_editor_property('field_of_view',32)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);assert levels.save_current_level()
record={'asset':key,'actor':label,'mesh':mesh.get_path_name(),'location_cm':list(pos),'scale':scale,'yaw':0,'bounds_center':[center.x,center.y,center.z],'bounds_extent':[extent.x,extent.y,extent.z],'world':world_path,'camera':camera.get_actor_label(),'collision':'complex_as_simple','status':'placed_pending_visual_check','site':'Main terrace facing northern walking path; original path and trees retained'}
(folder/'world-placement.json').write_text(json.dumps(record,indent=2))
p=camera.get_actor_location();r=camera.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/blender-civic-capture.json').write_text(json.dumps(args))
