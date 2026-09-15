"""Record all source surface names and dominant cell colors without changing images."""
import json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[2]
records=[]
for p in sorted((root/'SourceAssets/Voxel').glob('*.png')):
    if not p.stem.startswith(('terrain_','cottage_plaster_','cottage_roof_tile_')):continue
    im=Image.open(p).convert('RGB').resize((20,20),Image.Resampling.BOX)
    records.append({'name':p.stem,'colors':['%02x%02x%02x'%c for c in im.getdata()]})
assert len(records)==45
(root/'Docs/Reconstruction/surfaces-source.json').write_text(json.dumps(records))
print('45 surface sources recorded')
