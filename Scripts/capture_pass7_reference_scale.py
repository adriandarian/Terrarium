"""Native render at the exact 481x809 dimensions of the user's reference."""
from pathlib import Path
import unreal

assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
camera = next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
              if a.get_actor_label() == 'Baseline_Orthographic_Review')
assert camera.camera_component.post_process_blend_weight == 1.0
assert unreal.AutomationLibrary.take_high_res_screenshot(
    481, 809, str(Path(unreal.Paths.project_dir(), 'Docs/Fidelity/Pass7/reference-scale.png')),
    camera=camera, delay=1.0)
