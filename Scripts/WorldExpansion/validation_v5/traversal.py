"""Run the same eight real CharacterMovement routes into separate V5 receipts."""
import sys
from pathlib import Path
import unreal
ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
sys.path.insert(0, str(ROOT / 'Scripts/WorldExpansion/validation_v5'))
from common import assert_baseline_copy, legacy_source, execute_source
assert_baseline_copy()
prior = getattr(unreal, '_world_expansion_traversal_runner', None)
assert not prior or prior.finished, 'Finish the previous traversal before V5 tests'
source = legacy_source('validate_traversal.py').replace('_world_expansion_traversal_runner', '_world_expansion_v5_traversal_runner')
execute_source(source, 'validate_traversal.py')
