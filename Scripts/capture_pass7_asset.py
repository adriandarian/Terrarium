"""Six actual camera-specific native Unreal renders; no viewport cache reuse."""
import sys,json,subprocess,time
from pathlib import Path
from PIL import Image,ImageDraw
asset=sys.argv[1]
folder=Path('Docs/Fidelity/Pass7/Assets')/asset
folder.mkdir(parents=True,exist_ok=True)
views=[('front-right',135,-32),('front-left',45,-32),('back-left',-45,-32),('back-right',-135,-32),('overhead',135,-72),('low-angle',135,-8)]
for label,yaw,pitch in views:
    filename=(folder/(label+'.png')).resolve()
    before=filename.stat().st_mtime_ns if filename.exists() else 0
    Path('Saved/inspect-request.json').write_text(json.dumps({'asset':asset,'yaw':yaw,'pitch':pitch,'output':str(filename)}))
    subprocess.run([sys.executable,'Scripts/run_editor.py','Scripts/inspect_one_asset.py'],check=True)
    deadline=time.monotonic()+50
    while not filename.exists() or filename.stat().st_mtime_ns==before:
        if time.monotonic()>deadline:raise TimeoutError(str(filename))
        time.sleep(.5)
    time.sleep(.3)
    print(label,flush=True)
sheet=Image.new('RGB',(1200,700),(30,32,25));draw=ImageDraw.Draw(sheet)
for i,(label,_,_) in enumerate(views):
    im=Image.open(folder/(label+'.png'));im.thumbnail((395,315))
    x=i%3*400;y=i//3*350
    sheet.paste(im,(x,y+30));draw.text((x+6,y+8),asset+' / '+label,fill=(239,231,198))
sheet.save(folder/'contact-sheet.jpg',quality=93)
print((folder/'contact-sheet.jpg').resolve())
