"""Record an actually inspected six-view asset review."""
import sys,json
from pathlib import Path
p=Path('Docs/Phase1/Validation')/(sys.argv[1]+'.json')
d=json.loads(p.read_text())
d['visual_review']='passed: six Lumen-lit views; no missing faces or black-object artifacts'
if len(sys.argv)>2:d['known_gap']=sys.argv[2]
p.write_text(json.dumps(d,indent=2))
