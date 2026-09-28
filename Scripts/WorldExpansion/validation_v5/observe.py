"""Passive idle/city V5 observation with isolated receipts and no scene mutations."""
import sys
from pathlib import Path
import unreal
ROOT = Path(unreal.Paths.project_dir()).resolve()
assert ROOT == Path('C:/Users/hello/Projects/Terrarium')
sys.path.insert(0, str(ROOT / 'Scripts/WorldExpansion/validation_v5'))
from common import legacy_source, execute_source
source = legacy_source('observe_play.py').replace('_world_expansion_traversal_runner', '_world_expansion_v5_traversal_runner').replace('_world_expansion_observer', '_world_expansion_v5_observer')
execute_source(source, 'observe_play.py')
