"""Direct pixel comparison is QA evidence, never an artistic replacement render."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
root=Path(__file__).resolve().parents[1]
ref=Image.open('C:/Users/hello/.codex/attachments/e15f0cd8-70dc-4b2c-9579-42e0a1c2b7fe/image-1.png').convert('RGB')
candidate=root/(sys.argv[1] if len(sys.argv)>1 else 'Docs/Fidelity/pass-4.png')
cur=Image.open(candidate).convert('RGB').resize(ref.size,Image.Resampling.LANCZOS)
old=Image.open(root/'Docs/Final/homestead.png').convert('RGB').resize(ref.size,Image.Resampling.LANCZOS)
panel=Image.new('RGB',(ref.width*3,ref.height+28),(27,29,22));d=ImageDraw.Draw(panel)
for i,(label,im) in enumerate([('REFERENCE',ref),('PREVIOUS RENDER',old),('CURRENT 3D RENDER',cur)]):
    panel.paste(im,(i*ref.width,28));d.text((i*ref.width+12,8),label,fill=(239,232,199))
out=root/'Docs/Fidelity';panel.save(out/'comparison.png')
a=np.asarray(ref,dtype=float);b=np.asarray(cur,dtype=float);c=np.asarray(old,dtype=float)
# Full-frame error includes the reference's character/inset pixels. Report that
# limitation explicitly; an environmental landmark match is not pixel parity.
regions={'full_frame':(0,0,481,809),'cottage':(195,220,320,345),'wheat':(226,70,481,204),'river_bridge':(0,493,481,660),'terrain_path':(0,345,481,493)}
metrics={}
for name,(x0,y0,x1,y1) in regions.items():
    aa=a[y0:y1,x0:x1];bb=b[y0:y1,x0:x1];cc=c[y0:y1,x0:x1]
    metrics[name]={'previous_rgb_mae':float(np.abs(aa-cc).mean()),'current_rgb_mae':float(np.abs(aa-bb).mean()),'exact_pixel_fraction':float(np.all(aa==bb,axis=2).mean())}
heat=np.clip(np.abs(a-b).mean(axis=2)*3,0,255).astype('uint8')
Image.fromarray(heat).save(out/'pixel-error.png')
record={'candidate':str(candidate),'comparison_resolution':list(ref.size),'metrics':metrics,'pixel_parity_achieved':bool(np.array_equal(a,b)),'limits':'RGB MAE measures pixel error, not perceptual equivalence. The full frame includes excluded character and inset pixels. No image warp or registration was applied.'}
(out/'comparison-metrics.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
