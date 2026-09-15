"""Technical overlay of the final modeled outlines; original artwork is untouched."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2];folder=root/'Docs/BlenderRebuild/TrailTerrain'
data=json.loads((folder/'source-trace.json').read_text())
im=Image.open(root/data['source']).convert('RGB');draw=ImageDraw.Draw(im)
for row in data['authored_pavers']:
    points=[((x/2.4+.5)*1254,(.5-y/2.4)*1254) for x,y in row['outline_m']]
    draw.line(points+[points[0]],fill=(20,55,100),width=2)
    draw.text(points[0],str(row['source_stone']),fill=(0,0,0))
im.save(folder/'manual-trace-preview.png')
print('Recorded overlay for',len(data['authored_pavers']),'modeled paver outlines.')
