"""Build and capture exactly one asset; human/model visual review stays separate."""
import json,sys,subprocess
from pathlib import Path
recipe,asset=sys.argv[1:3]
Path('Saved/asset-request.txt').write_text(recipe)
subprocess.run([sys.executable,'Scripts/run_editor.py','Scripts/build_one_asset.py'],check=True)
report=Path('Docs/Phase1/Validation')/(asset+'.json')
assert report.exists(), 'Build failed; inspect Saved/Logs/Terrarium.log before continuing.'
subprocess.run([sys.executable,'Scripts/capture_asset_review.py',asset],check=True)
