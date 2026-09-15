"""Verify and place the v6 candidate through the shared gallery workflow."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('update_roof_surface_gallery.py')),
               init_globals={'ROOF_KEY':'cottage_roof_tile_v6_candidate'})
