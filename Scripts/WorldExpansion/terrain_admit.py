"""Coordinator-only Unreal operation. Run sequentially on verified ValleyRegion.

Uses project-proven native Geometry Script admission, with source CCW triangles
explicitly reversed for Unreal. Re-running reuses admitted meshes. Set an optional
Docs/WorldExpansion/terrain-admit-request.json {"offset":0,"limit":16} to batch.
"""
import unreal
import json
from pathlib import Path

ROOT=Path(unreal.Paths.project_dir()).resolve()
assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
LEVEL='/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
DEST='/Game/Terrarium/WorldExpansion/Terrain'
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert E.get_editor_world().get_path_name().split('.')[0]==LEVEL
assert not E.get_game_world(),'Stop PIE before admission'
DOC=ROOT/'Docs/WorldExpansion';DOC.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'SourceAssets/WorldExpansion/Terrain/manifest.json').read_text())
T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary

def material():
    path=DEST+'/Materials/M_ValleySculpted';mat=unreal.load_asset(path)
    if mat and unreal.EditorAssetLibrary.get_metadata_tag(mat,'TerrariumComplete')=='2':return mat
    task=unreal.AssetImportTask();task.filename=str(ROOT/manifest['texture'])
    task.destination_path=DEST+'/Textures';task.destination_name='T_ValleyMineral'
    task.automated=True;task.replace_existing=False;task.save=True
    T.import_asset_tasks([task]);texture=unreal.load_asset(DEST+'/Textures/T_ValleyMineral');assert texture
    mat=mat or T.create_asset('M_ValleySculpted',DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    vc=M.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-700,0)
    tex=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-700,180);tex.texture=texture
    scale=M.create_material_expression(mat,unreal.MaterialExpressionMultiply,-450,180)
    scale.set_editor_property('const_b',.35)
    assert M.connect_material_expressions(tex,'',scale,'A')
    lift=M.create_material_expression(mat,unreal.MaterialExpressionAdd,-260,180)
    lift.set_editor_property('const_b',.65)
    assert M.connect_material_expressions(scale,'',lift,'A')
    mul=M.create_material_expression(mat,unreal.MaterialExpressionMultiply,-70,0)
    assert M.connect_material_expressions(vc,'',mul,'A')
    assert M.connect_material_expressions(lift,'',mul,'B')
    assert M.connect_material_property(mul,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,v,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.92,350),(unreal.MaterialProperty.MP_SPECULAR,.12,450)]:
        node=M.create_material_expression(mat,unreal.MaterialExpressionConstant,-150,y);node.r=v
        assert M.connect_material_property(node,'',prop)
    M.recompile_material(mat)
    unreal.EditorAssetLibrary.set_metadata_tag(mat,'TerrariumComplete','2')
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat

mat=material()
water=unreal.load_asset('/Game/Terrarium/HomesteadPilot/RemainingEnvironment/Materials/M_HP_RiverCurrent') or mat
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
request=DOC/'terrain-admit-request.json';cfg=json.loads(request.read_text()) if request.exists() else {}
rows=manifest['assets'][cfg.get('offset',0):cfg.get('offset',0)+cfg.get('limit',1000)]
records=[]
for row in rows:
    source=json.loads((ROOT/row['source']).read_text());path=DEST+'/Meshes/SM_'+row['name']
    mesh=unreal.load_asset(path)
    if mesh:
        assert unreal.EditorAssetLibrary.get_metadata_tag(mesh,'TerrariumSourceSHA256')==row['sha256'],(row['name'],'Source changed; explicitly rebuild this mesh before reuse')
    if not mesh:
        dynamic=unreal.DynamicMesh();buf=unreal.GeometryScriptSimpleMeshBuffers()
        buf.vertices=[unreal.Vector(*(v*100 for v in p)) for p in source['vertices']]
        buf.triangles=[unreal.IntVector(a,c,b) for a,b,c in source['triangles']]
        buf.vertex_colors=[unreal.LinearColor(*rgb,1) for rgb in source['colors']]
        buf.uv0=[unreal.Vector2D(p[0]/4,p[1]/4) for p in source['vertices']]
        dynamic.append_buffers_to_mesh(buf);unreal.GeometryScript_Normals.set_per_face_normals(dynamic)
        assert dynamic.get_triangle_count()==row['triangles']
        if row['kind']=='terrain':
            n,valid=dynamic.get_triangle_face_normal(0);assert valid and n.z>0,(row['name'],'inverted terrain')
        options=unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=row['collision'],enable_recompute_normals=False,enable_recompute_tangents=False)
        mesh,outcome=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dynamic,path,options)
        assert mesh and outcome==unreal.GeometryScriptOutcomePins.SUCCESS,row['name']
        mesh.set_material(0,water if row['kind']=='water' else mat)
        if row['collision']:
            body=mesh.get_editor_property('body_setup');assert body
            body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            body.set_editor_property('double_sided_geometry',True)
        unreal.EditorAssetLibrary.set_metadata_tag(mesh,'TerrariumSourceSHA256',row['sha256'])
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    label='WX_'+row['name'];actor=actors.get(label)
    if not actor:actor=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0));actor.set_actor_label(label)
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_collision_profile_name('BlockAll' if row['collision'] else 'NoCollision')
    actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if row['collision'] else unreal.CollisionEnabled.NO_COLLISION)
    actor.set_folder_path('WorldExpansion/'+row['kind'].title())
    records.append({'actor':label,'mesh':mesh.get_path_name(),'triangles':row['triangles'],'collision':row['collision'],'source_sha256':row['sha256']})
assert L.save_current_level()
(DOC/f'terrain-admission-{cfg.get("offset",0):03d}.json').write_text(json.dumps({'world':LEVEL,'meshes':records,'validation':'native triangle counts and upward terrain normal checked; visual and traversal validation separate'},indent=2))
print(json.dumps({'admitted':len(records),'offset':cfg.get('offset',0),'triangles':sum(r['triangles'] for r in records)}))
