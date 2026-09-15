"""Sequential six-angle Lumen captures of ONE asset, plus a labeled QA contact sheet."""
import sys,json,subprocess,time
from pathlib import Path
from PIL import Image,ImageDraw

asset=sys.argv[1]
folder=Path('Docs/Phase1/Captures')/asset
folder.mkdir(parents=True,exist_ok=True)
views=[('front-right',135,-32),('front-left',45,-32),('back-left',-45,-32),('back-right',-135,-32),('overhead',135,-72),('low-angle',135,-8)]
sheet=Image.new('RGB',(1500,840),(33,36,28));draw=ImageDraw.Draw(sheet)
for i,(label,yaw,pitch) in enumerate(views):
    Path('Saved/inspect-request.json').write_text(json.dumps({'asset':asset,'yaw':yaw,'pitch':pitch}))
    subprocess.run([sys.executable,'Scripts/run_editor.py','Scripts/inspect_one_asset.py'],check=True,capture_output=True)
    time.sleep(3)
    filename=folder/(label+'.png')
    subprocess.run([sys.executable,'Scripts/capture_baseline.py',str(filename)],check=True,capture_output=True)
    picture=Image.open(filename)
    # Trim only camera pillarboxing in the QA sheet. Originals remain untouched.
    picture=picture.crop((int(picture.width*.127),0,int(picture.width*.873),picture.height))
    picture.thumbnail((496,250))
    x=(i%3)*500;y=(i//3)*420
    sheet.paste(picture,(x+(500-picture.width)//2,y+35))
    draw.text((x+15,y+12),asset+' / '+label,fill=(228,222,197))
sheet.save(folder/'contact-sheet.jpg',quality=93)
print(str((folder/'contact-sheet.jpg').resolve()))
