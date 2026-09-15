"""Place the Blender creature on sampled, unobstructed courtyard ground."""
import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/Brambit';world='/Game/Terrarium/Blender/Maps/HomesteadBlender'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert world+'.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
components=[(a,c) for a in scene.values() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and a.get_actor_label()!='Blender_Brambit_Courtyard']
terrain=[(a,c) for a,c in components if '/GrassTerrain/SM_Blender_GrassTerrain.' in c.static_mesh.get_path_name()]
assert terrain
source=json.loads((out/'base-support-source.json').read_text());assert len(source['samples'])==20
scale=.8;candidates=[]
for dx in [0,-12,12,-24,24]:
    for dy in [0,-12,12,-24,24]:
        x=500+dx;y=dy;samples=[]
        for sample in source['samples']:
            sx,sy,sz=sample['point_m'];px=x+sx*100*scale;py=y-sy*100*scale
            hits=[]
            for owner,component in terrain:
                hit=component.line_trace_component(unreal.Vector(px,py,800),unreal.Vector(px,py,500),True,False,False)
                if hit:hits.append((hit[0].z,owner.get_actor_label(),component.get_name()))
            if not hits:break
            z,owner,component=max(hits)
            samples.append({'foot':sample['foot'],'xy':[px,py],'ground_z':z,'local_bottom_m':sz,'ground_actor':owner,'ground_component':component})
        if len(samples)!=20:continue
        ground=[p['ground_z'] for p in samples];spread=max(ground)-min(ground)
        if spread>.5:continue
        blocked=False
        for px in [x-32,x-16,x,x+16,x+28]:
            for py in [y-17,y,y+17,y+28]:
                for owner,component in components:
                    if any(component==c for _,c in terrain):continue
                    hit=component.line_trace_component(unreal.Vector(px,py,max(ground)+90),unreal.Vector(px,py,max(ground)+.5),True,False,False)
                    if hit:blocked=True;break
                if blocked:break
            if blocked:break
        if not blocked:candidates.append((spread+(abs(dx)+abs(dy))*.0001,x,y,samples))
assert candidates,'No supported, unobstructed sample footprint near the courtyard location'
_,x,y,samples=min(candidates,key=lambda row:row[0]);ground=max(p['ground_z'] for p in samples)
mesh=unreal.load_asset('/Game/Terrarium/Blender/Brambit/SM_Blender_Brambit');assert mesh
mat=unreal.load_asset('/Game/Terrarium/Blender/Brambit/M_Brambit');assert len(mesh.static_materials)==1
mel=unreal.MaterialEditingLibrary
for prop in [unreal.MaterialProperty.MP_EMISSIVE_COLOR,unreal.MaterialProperty.MP_METALLIC]:
    node=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-100,400);node.r=0;mel.connect_material_property(node,'',prop)
mel.recompile_material(mat);mesh.set_material(0,mat)
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
unreal.EditorAssetLibrary.save_loaded_asset(mat);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
z=ground+.04-mesh.get_bounding_box().min.z*scale
label='Blender_Brambit_Courtyard';actor=scene.get(label)
if actor:assert actor.static_mesh_component.static_mesh==mesh
else:actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z));actor.set_actor_label(label)
actor.static_mesh_component.set_static_mesh(mesh);actor.static_mesh_component.set_editor_property('override_materials',[])
actor.set_actor_location(unreal.Vector(x,y,z),False,False);actor.set_actor_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0),False)
actor.set_actor_scale3d(unreal.Vector(scale,scale,scale));actor.static_mesh_component.set_collision_profile_name('BlockAll')
for sample in samples:sample['clearance_cm']=z+sample['local_bottom_m']*100*scale-sample['ground_z']
assert levels.save_current_level()
record={'world':world,'actor':label,'mesh':mesh.get_path_name(),'materials':[mat.get_path_name()],'location_cm':[x,y,z],'scale':scale,'yaw':0,'height_cm':(mesh.get_bounding_box().max.z-mesh.get_bounding_box().min.z)*scale,'camera':'Blender_Brambit_Review','support_probes':samples,'ground_height_spread_cm':max(p['ground_z'] for p in samples)-min(p['ground_z'] for p in samples),'max_clearance_cm':max(p['clearance_cm'] for p in samples),'source_blend_sha256':source['source_blend_sha256'],'status':'placed_pending_reload_and_visual_check','limits':'Static courtyard placement. Foot samples and vertical obstruction samples only; no rig, locomotion, rigid-body or complete collision audit.'}
(out/'world-placement.json').write_text(json.dumps(record,indent=2))
