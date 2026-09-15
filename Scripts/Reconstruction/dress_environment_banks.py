"""Place reference shoreline groups and soften overly regular river facets."""
import unreal,sys,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment';sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadReference.' in str(levels.get_current_level())
mat=unreal.load_asset('/Game/Terrarium/Environment/Materials/M_ReferenceFacetedWater');lib=unreal.MaterialEditingLibrary
# Fresh explicit expression list rather than modifying global renderer exposure.
for expression in unreal.ObjectIterator(unreal.MaterialExpressionCustom):
    if expression.get_outer()==mat:
        code=expression.get_editor_property('code').replace('lerp(.82,1.18,h)*lerp(.94,1.04,facet)','lerp(.93,1.09,h)*lerp(.985,1.015,facet)')
        expression.set_editor_property('code',code)
lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label().startswith('Reference_Bank_'):actors.destroy_actor(a)
pigment=unreal.load_asset('/Game/Terrarium/Environment/Materials/M_EnvironmentPigment')
rows=[]
for i,(x,y,kind,sx,sy,sz,yaw) in enumerate([
    (38,539,'rock',.48,.60,.34,30),(59,551,'reeds',.65,.72,.75,60),(76,570,'rock',.48,.48,.28,0),
    (111,580,'reeds',.48,.60,.60,80),(146,572,'rock',.39,.45,.25,90),(175,586,'reeds',.58,.48,.54,60),
    (203,601,'rock',.32,.37,.22,15),(224,629,'reeds',.48,.44,.52,65),(118,642,'rock',.40,.40,.25,70),
    (45,620,'rock',.62,.68,.40,0),(69,623,'reeds',.44,.51,.45,30),(413,541,'rock',.4,.4,.25,90),
    (430,550,'reeds',.55,.54,.65,20),(399,584,'reeds',.45,.46,.52,50)]):
    mesh=unreal.load_asset('/Game/Terrarium/Reconstruction/Meshes/'+('SM_Recon_MossRock_R3' if kind=='rock' else 'SM_Recon_Riverbank_R3'))
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*ref.world(x,y,-9)))
    a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,pigment)
    a.set_actor_scale3d(unreal.Vector(sx,sy,sz));a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False)
    a.set_actor_label('Reference_Bank_'+str(i));a.set_folder_path('Reference/Shoreline')
    rows.append({'actor':a.get_actor_label(),'source':kind,'reference_pixel':[x,y],'base_z_cm':-9})
assert levels.save_current_level();(out/'shoreline.json').write_text(json.dumps(rows,indent=2))
