import json
from pathlib import Path
import unreal

assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
camera = next(a for a in actors.get_all_level_actors()
              if a.get_actor_label() == 'Baseline_Orthographic_Review')
cc = camera.camera_component
material = unreal.load_asset('/Game/Terrarium/Materials/M_Pass7_DistantSoftness')
stats = unreal.MaterialEditingLibrary.get_statistics(material)
report = {'blend_weight': cc.get_editor_property('post_process_blend_weight'),
          'settings': str(cc.get_editor_property('post_process_settings')),
          'statistics': str(stats), 'material': material.get_path_name(),
          'blendable': str(material.get_editor_property('blendable_location'))}
Path(unreal.Paths.project_dir(), 'Docs/Fidelity/Pass7/camera-material.json').write_text(json.dumps(report, indent=2))
unreal.log('PASS7_CAMERA_MATERIAL_INSPECTED')
