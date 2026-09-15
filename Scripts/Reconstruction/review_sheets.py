"""Diagnostic contact sheets: unmodified source/capture thumbnails with labels."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2]
rows={}
for p in (root/'Docs/Reconstruction/Builds').glob('*.json'):
    r=json.loads(p.read_text())
    if r['key'] not in rows or r['revision']>rows[r['key']]['revision']:rows[r['key']]=r
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',13)
out=root/'Docs/Reconstruction/ReviewSheets';out.mkdir(exist_ok=True)
for group,items in [('objects',[r for r in rows.values() if r['module']!='surfaces']),('surfaces',[r for r in rows.values() if r['module']=='surfaces'])]:
    items.sort(key=lambda r:(r['module'],r['key']))
    for start in range(0,len(items),9):
        page=Image.new('RGB',(1200,780),'#20252b');draw=ImageDraw.Draw(page)
        back=Image.new('RGB',(1200,780),'#20252b');bd=ImageDraw.Draw(back)
        for i,r in enumerate(items[start:start+9]):
            x=(i%3)*400;y=(i//3)*260
            draw.text((x+8,y+5),r['key']+'  R'+str(r['revision']),font=font,fill='white')
            bd.text((x+8,y+5),r['key']+' front / back',font=font,fill='white')
            paths=[root/'SourceAssets/Voxel'/r['source'],root/'Docs/Reconstruction/Renders'/(r['name']+'-front.png'),root/'Docs/Reconstruction/Renders'/(r['name']+'-back.png')]
            for j,p in enumerate(paths):
                im=Image.open(p).convert('RGB');im.thumbnail((194,225))
                if j<2:page.paste(im,(x+j*200+(200-im.width)//2,y+28+(225-im.height)//2))
                if j>0:back.paste(im,(x+(j-1)*200+(200-im.width)//2,y+28+(225-im.height)//2))
        page.save(out/(group+'-'+str(start//9+1)+'-comparison.png'))
        back.save(out/(group+'-'+str(start//9+1)+'-angles.png'))
