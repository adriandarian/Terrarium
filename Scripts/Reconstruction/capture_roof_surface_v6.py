"""Capture the v6 candidate through the shared roof review workflow."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('capture_roof_surface.py')),
               init_globals={'ROOF_KEY':'cottage_roof_tile_v6_candidate'})
