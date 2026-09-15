"""Final editor validation of saved migration references, galleries and model metadata."""
import json
import math
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root = Path(unreal.Paths.project_dir())
out = root / 'Docs/AssetMigration'
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.eject_pilot_level_actor()
report = {'project':unreal.Paths.get_project_file_path(),'textures':0,'surface_materials':0,'models':[],'maps':[]}
for r in json.loads((out/'imported.json').read_text()):
    texture = unreal.load_asset(r['texture'])
    assert isinstance(texture,unreal.Texture2D) and texture.get_editor_property('srgb')
    report['textures'] += 1
    for key in ['reference_material','surface_material']:
        if not r[key]: continue
        material = unreal.load_asset(r[key])
        assert isinstance(material,unreal.MaterialInstanceConstant)
        actual = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(material,'SourceColor')
        assert actual.get_path_name() == texture.get_path_name(), r
        parent = material.get_editor_property('parent').get_name()
        assert parent == ('M_Reference' if key=='reference_material' else 'M_Surface')
        if key=='surface_material':report['surface_materials'] += 1
for group in ['structures','characters']:
    for r in json.loads((out/(group+'-built.json')).read_text()):
        mesh = unreal.load_asset(r['asset'])
        assert isinstance(mesh,unreal.StaticMesh) and mesh.get_material(0)
        assert r['validation']['saved_normal_errors']==0
        report['models'].append({'asset':r['asset'],'triangles':r['validation']['triangles'],'saved_normal_errors':0})
for kind in ['Architecture','Characters','Environment','References','Surfaces']:
    record=json.loads((out/(kind.lower()+'-gallery.json')).read_text())
    assert levels.load_level(record['map'])
    scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
    assert not any('TransientCapture' in name for name in scene)
    for r in record['records']:
        actor=scene[r['label']]
        comp=actor.static_mesh_component
        assert comp.static_mesh.get_path_name().split('.')[0]==r['mesh']
        assert comp.get_material(0)
        if r['material_override']:assert comp.get_material(0).get_path_name().split('.')[0]==r['material_override']
    for name,a in scene.items():
        if name.startswith('Label_'):
            a.set_actor_rotation(unreal.Rotator(pitch=0 if kind in ['Architecture','Characters','Environment'] else -90,yaw=-90,roll=0),False)
    assert levels.save_current_level()
    report['maps'].append({'map':record['map'],'entries':record['count'],'reopened_exact_references':True})
report['visual_evidence']='Unreal asset thumbnails and isolated front base-color captures; final Lit material acceptance remains pending.'
report['gameplay_collision_rigs_animations_pbr_sets']='not implemented'
(out/'verification.json').write_text(json.dumps(report,indent=2))
assert levels.load_level('/Game/Terrarium/Migration/Maps/Architecture')
unreal.log('MIGRATION_FINAL_VERIFICATION_PASSED')
