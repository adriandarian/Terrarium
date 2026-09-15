"""Check the reusable Blueprint and real Niagara particle motion/lifetime in editor."""
import unreal,json,sys,importlib
from pathlib import Path
root=Path(unreal.Paths.project_dir());assert Path(unreal.Paths.get_project_file_path()).name=='Terrarium.uproject'
sys.path.insert(0,str(root/'Scripts/Reconstruction'))
import kindlehorn_effects as effects
importlib.reload(effects)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
bp=unreal.load_asset(effects.BP)
a=actors.spawn_actor_from_class(unreal.load_object(None,effects.BP+'.'+effects.BP.rsplit('/',1)[1]+'_C'),unreal.Vector(1000,0,0))
a.set_actor_label('TransientKindlehornBlueprintVerification')
try:
    mesh=a.get_component_by_class(unreal.StaticMeshComponent)
    nc=a.get_component_by_class(unreal.NiagaraComponent)
    light=a.get_component_by_class(unreal.PointLightComponent)
    assert mesh and nc and light
    assert mesh.static_mesh.get_name()=='SM_Recon_Kindlehorn_R6'
    nc.set_paused(False)
    samples=[]
    for ticks in [30,30,90]:
        nc.advance_simulation(ticks,1/60)
        cache=unreal.NiagaraSimCacheFunctionLibrary.capture_niagara_sim_cache_immediate(unreal.NiagaraSimCache(),unreal.NiagaraSimCacheCreateParameters(),nc)
        assert cache
        names=list(cache.get_emitter_names());assert len(names)==1,names
        pos=cache.read_position_attribute('Position',names[0])
        ids=cache.read_int_attribute('UniqueID',names[0])
        colors=cache.read_color_attribute('Color',names[0])
        samples.append({'ticks_advanced':ticks,'count':len(pos),'positions_cm':[[v.x,v.y,v.z] for v in pos],
                        'particle_ids':list(ids),'alpha':[v.a for v in colors]})
    assert all(s['count']>0 for s in samples),samples
    assert samples[0]['positions_cm']!=samples[1]['positions_cm']
    assert set(samples[0]['particle_ids'])!=set(samples[2]['particle_ids'])
    assert any(0<v<1 for s in samples for v in s['alpha'])
    record={'blueprint':effects.BP,'niagara_system':effects.FX,'mesh':mesh.static_mesh.get_path_name(),
            'blueprint_components_verified':True,'particle_positions_changed':True,'particles_expire_and_respawn':True,
            'samples':samples,'point_light_intensity':light.intensity,'validation':'native editor simulation; not gameplay/packaged build'}
    (root/'Docs/Reconstruction/kindlehorn-fx-verification.json').write_text(json.dumps(record,indent=2))
finally:actors.destroy_actor(a)

