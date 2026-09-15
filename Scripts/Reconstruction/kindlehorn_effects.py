"""Reusable creature Blueprint: saved mesh, looping Niagara sparks and local horn light."""
import unreal
FX='/Game/Terrarium/Reconstruction/Effects/NS_KindlehornSparks_R4'
BP='/Game/Terrarium/Reconstruction/Blueprints/BP_Kindlehorn_R6'

def build_blueprint(mesh_path):
    bp=unreal.load_asset(BP)
    if not bp:
        factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
        bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_Kindlehorn_R6','/Game/Terrarium/Reconstruction/Blueprints',unreal.Blueprint,factory)
        sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        lib=unreal.SubobjectDataBlueprintFunctionLibrary
        parent=sub.k2_gather_subobject_data_for_blueprint(bp)[0]
        for cls,name in [(unreal.StaticMeshComponent,'Creature'),(unreal.NiagaraComponent,'HornSparks'),(unreal.PointLightComponent,'HornLight')]:
            handle,fail=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent,new_class=cls,blueprint_context=bp))
            assert not str(fail),str(fail)
            sub.rename_subobject(handle,unreal.Text(name))
            obj=lib.get_object(lib.get_data(handle))
            if cls==unreal.StaticMeshComponent:obj.set_static_mesh(unreal.load_asset(mesh_path))
            elif cls==unreal.NiagaraComponent:
                obj.set_asset(unreal.load_asset(FX));obj.set_editor_property('relative_location',unreal.Vector(0,-31,139))
                obj.set_editor_property('auto_activate',True)
            else:
                obj.set_editor_property('relative_location',unreal.Vector(0,-39,135))
                obj.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
                obj.set_light_color(unreal.LinearColor(1,.38,.018,1))
                obj.set_intensity(1.2);obj.set_attenuation_radius(65)
                obj.set_editor_property('cast_shadows',False)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset(FX))
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
    return bp

def spawn_effects(parent):
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    pos=parent.get_actor_location()
    fx=actors.spawn_actor_from_class(unreal.NiagaraActor,pos+unreal.Vector(0,-31,139))
    fx.set_actor_label('FX_KindlehornSparks')
    c=fx.get_component_by_class(unreal.NiagaraComponent);c.set_asset(unreal.load_asset(FX));c.activate(True)
    light=actors.spawn_actor_from_class(unreal.PointLight,pos+unreal.Vector(0,-39,135))
    light.set_actor_label('FX_KindlehornGlow');lc=light.light_component
    lc.set_mobility(unreal.ComponentMobility.MOVABLE);lc.set_intensity(1.2);lc.set_attenuation_radius(65)
    lc.set_light_color(unreal.LinearColor(1,.38,.018,1));lc.set_editor_property('cast_shadows',False)
    for actor in [fx,light]:
        actor.attach_to_actor(parent,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    return fx,light


