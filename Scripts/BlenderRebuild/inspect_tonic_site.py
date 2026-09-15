"""Read-only placement and material API preflight for Moss Tonic."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=[]
for a in actors.get_all_level_actors():
    cs=a.get_components_by_class(unreal.StaticMeshComponent)
    for c in cs:
        m=c.get_editor_property('static_mesh')
        if m and any(w in (a.get_actor_label()+m.get_path_name()).lower() for w in ['tonic','prism','marketstall']):
            t=a.get_actor_transform();rows.append({'label':a.get_actor_label(),'mesh':m.get_path_name(),'transform':str(t),'bounds':str(a.get_actor_bounds(False))})
mat=unreal.Material()
props={}
for p in ['blend_mode','translucency_lighting_mode','two_sided','refraction_method','shading_model']:
    try:props[p]=str(mat.get_editor_property(p))
    except Exception as e:props[p]=str(e)
enum={k:[a for a in dir(getattr(unreal,k)) if a.isupper()] for k in ['BlendMode','TranslucencyLightingMode','RefractionMode','MaterialProperty'] if hasattr(unreal,k)}
mesh=unreal.load_asset('/Game/Terrarium/Blender/MossTonic/SM_Blender_MossTonic')
slots=[]
if mesh:
    for slot in mesh.static_materials:
        row={'str':str(slot)}
        for p in ['imported_material_slot_name','material_slot_name']:
            try:row[p]=str(slot.get_editor_property(p))
            except Exception as e:row[p]=str(e)
        slots.append(row)
counter=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Blender_MarketStall_UpperPath').static_mesh_component
probes=[]
for dx in [-5,0,5]:
    for dy in [-4,0,4]:
        x=241.4+dx;y=582+dy
        hit=counter.line_trace_component(unreal.Vector(x,y,670),unreal.Vector(x,y,630),True,False,False)
        probes.append({'xy':[x,y],'z':hit[0].z if hit else None})
(root/'Docs/BlenderRebuild/MossTonic/site-preflight.json').write_text(json.dumps({'level':str(levels.get_current_level()),'actors':rows,'material_properties':props,'enums':enum,'imported_slots':slots,'counter_probes':probes},indent=2))
