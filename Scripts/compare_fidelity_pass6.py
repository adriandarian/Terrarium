"""Compare native editor captures at reference resolution, without registration."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
root=Path(__file__).resolve().parents[1]
out=root/'Docs/Fidelity/Pass6'
ref=Image.open('C:/Users/hello/.codex/attachments/e15f0cd8-70dc-4b2c-9579-42e0a1c2b7fe/image-1.png').convert('RGB')
prev=Image.open(root/'Docs/Fidelity/Structures/structure-update.png').convert('RGB').resize(ref.size,Image.Resampling.LANCZOS)
cur=Image.open(out/'pass-6.png').convert('RGB').resize(ref.size,Image.Resampling.LANCZOS)
panel=Image.new('RGB',(ref.width*3,ref.height+28),(27,29,22));d=ImageDraw.Draw(panel)
for i,(label,im) in enumerate([('REFERENCE',ref),('BEFORE COMPOSITION UPDATE',prev),('CURRENT UNREAL RENDER',cur)]):
    panel.paste(im,(i*ref.width,28));d.text((i*ref.width+12,8),label,fill=(239,232,199))
panel.save(out/'comparison.png')
a,b,c=[np.asarray(im,dtype=float) for im in [ref,prev,cur]]
regions={'full_frame':(0,0,481,809),'shed':(90,295,171,365),'bridge':(237,527,372,625),'wheat':(226,70,481,204),'garden':(270,326,415,394),'stairs':(136,420,199,498),'upper_land':(0,0,481,220),'river':(0,493,481,660),'lower_land':(225,655,481,809)}
metrics={}
regions['well']=(328,290,381,354)
regions['upper_cliff']=(174,132,244,221)
regions['main_cliff']=(13,421,139,506)
for name,(x0,y0,x1,y1) in regions.items():
    aa=a[y0:y1,x0:x1];bb=b[y0:y1,x0:x1];cc=c[y0:y1,x0:x1]
    metrics[name]={'before_rgb_mae':float(np.abs(aa-bb).mean()),'current_rgb_mae':float(np.abs(aa-cc).mean()),'exact_pixel_fraction':float(np.all(aa==cc,axis=2).mean())}
record={'candidate':'Docs/Fidelity/Pass6/pass-6.png','comparison_resolution':list(ref.size),'metrics':metrics,'pixel_parity_achieved':bool(np.array_equal(a,c)),'limits':'RGB error is not perceptual equivalence. A static traveler is now included; the reference inset is still absent and its pixels remain included in full-frame measurements. No image warp or registration applied.'}
(out/'comparison-metrics.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
