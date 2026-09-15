"""Record paired native lighting evidence without granting asset fidelity."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'Docs/BlenderRebuild/Lighting'
current=json.loads((out/'sky-current.json').read_text())
live=json.loads((out/'live-diagnostics.json').read_text())
sky=next(a for a in live['actors'] if a['actor']=='Baseline_SkyLight')
assert sky['properties']['intensity']==7
assert all(f'{channel}: 255' in sky['properties']['light_color'] for channel in ['r','g','b'])
assert not live['dirty_maps']
views=['Crest','Tonic','Cottage','Terrace']
for view in views:
    left=json.loads((out/'Before'/view/'unreal-camera.json').read_text())
    right=json.loads((out/'Sky7'/view/'unreal-camera.json').read_text())
    assert left==right,(view,left,right)
    assert (out/'Before'/view/'unreal-viewport.png').is_file()
    assert (out/'Sky7'/view/'unreal-viewport.png').is_file()
current.update(status='working_profile_native_reviewed',paired_cameras_verified=views,
    observations=['Shaded crest relief and tonic label are easier to read.',
        'Sunlit cottage roof and terrace details remain visible in paired views.',
        'Crest metal remains muted and tonic translucency remains too opaque; lighting does not establish fidelity.'],
    limits='Four native camera comparisons and saved lighting readback. No comprehensive foliage-instance preservation audit or performance test.',
    accepted_asset_fidelity=False)
(out/'sky-current.json').write_text(json.dumps(current,indent=2))
html='''<!doctype html><meta charset="utf-8"><title>Terrarium lighting comparison</title>
<style>body{background:#151a1c;color:#ecede7;font:16px system-ui;margin:36px}section{margin:32px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}img{width:100%}h1,h2{font-weight:500}p{max-width:85ch;line-height:1.6}</style>
<h1>Working world lighting comparison</h1><p>The saved HomesteadBlender sky fill changed from intensity 2.2 and a cool tint to intensity 7 and neutral white. Sun intensity (22,500 lux), direction and manual exposure bias (-12) remain unchanged. Each pair uses identical recorded camera settings.</p>
<p>Shaded details are clearer; sunlit roof and terrain details remain visible. The crest's muted metal and tonic's overly opaque glass still require material refinement. This is a lighting review, not asset approval.</p>'''
for view in views:
    html+=f'<section><h2>{view}</h2><div class="pair"><div>Before<img src="Before/{view}/unreal-viewport.png"></div><div>Working sky fill<img src="Sky7/{view}/unreal-viewport.png"></div></div></section>'
(out/'comparison.html').write_text(html,encoding='utf-8')
print('Four paired cameras match; saved sky fill reviewed, asset fidelity open.')
