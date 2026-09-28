"""Package native continuation evidence; no editor operations."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / 'Docs/HomesteadPilot'
original = (DOCS / 'review.html').read_text(encoding='utf-8')
style = re.search(r'<style>(.*?)</style>', original, re.S).group(1)
gallery = [
    ('RiverA/unreal-viewport.png', 'The river', 'Animated teal currents follow the retained stepped banks.'),
    ('Market/unreal-viewport.png', 'The market', 'Stall, props and eight collectibles retain their authored materials.'),
    ('../RuntimeCompletion/FinalBuildings/lod-1-near.png', 'The lodge', 'Native near sample from the automatic-LOD camera sweep.'),
    ('../RuntimeCompletion/FinalBuildings/lod-2-near.png', 'The civic hall', 'Retained silhouette, roof coverage and material detail.'),
    ('../RuntimeCompletion/FinalBuildings/lod-3-near.png', 'The compound', 'Visible structure is intact; nearby trees obscure some surfaces.'),
    ('Gameplay.png', 'At walking height', 'Fresh default Play after the passive profile; inherited explorer presentation.')
]
cards = '\n'.join(f'<figure><a href="{path}" target="_blank" rel="noopener"><img loading="lazy" src="{path}" alt="{title}: {caption}"></a><figcaption><h3>{title}</h3><p>{caption}</p></figcaption></figure>' for path,title,caption in gallery)
page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><title>Terrarium · Homestead continuation</title><style>''' + style + '''
.gallery{display:grid;grid-template-columns:1fr 1fr;gap:32px}.gallery img{width:100%;aspect-ratio:1.68;object-fit:contain;background:var(--deep);border:1px solid var(--line)}figcaption{padding:18px 0}figcaption p{font-size:15px;color:var(--muted);margin:10px 0 0}.receipt-links{display:flex;flex-wrap:wrap;gap:16px 30px;margin-top:26px}.plain-note{padding:24px;border:1px solid var(--line);background:var(--panel);margin-top:28px}.results{width:100%;border-collapse:collapse}.results th,.results td{text-align:left;padding:16px 14px;border-bottom:1px solid var(--line)}.results th{color:var(--muted);font-size:13px;font-weight:400;letter-spacing:.05em}.results td:first-child{padding-left:0}.results td:last-child{color:var(--muted)}@media(max-width:760px){.gallery{grid-template-columns:1fr}.results{font-size:14px}.results th,.results td{padding:12px 7px}.intro{padding-top:40px}.masthead nav{gap:12px}}
</style></head><body>
<header class="masthead"><a class="brand" href="../review.html">Terra<span>rium</span></a><nav><a href="#collection">Collection</a><a href="#validation">Validation</a><a href="Review.md">Evidence notes ↗</a></nav><span class="folio">27 September 2026</span></header>
<main><section class="intro"><div><p class="eyebrow">Homestead · continuation</p><h1>A complete collection.<br>A place to begin.</h1></div><div class="intro-copy"><p>Warm timber and plaster above mossy terraces. Fine angular planting, a working path through the home, and a quieter river below.</p><span class="status">Integrated · saved · reopened</span></div></section>
<figure class="wide-image"><a href="FinalOverview/unreal-viewport.png" target="_blank" rel="noopener"><img src="FinalOverview/unreal-viewport.png" alt="Final native Unreal overview of the terraced homestead, cottage, other buildings, retained grass and animated teal river"></a></figure>
<div class="caption-row"><span><strong>StartingHome</strong> · Native Unreal Engine 5.8.2 capture</span><span>All 5,841 grass tiles retained</span></div>
<div class="intro-facts"><div class="fact"><strong>17</strong><span>Building and prop families with three LODs</span></div><div class="fact"><strong>1,753</strong><span>Retained environment instances verified</span></div><div class="fact"><strong>190</strong><span>Fitted river tiles with animated currents</span></div></div>
<section class="section" id="collection"><div class="section-head"><span class="index">01 /</span><h2>The remaining<br>homestead.</h2><p>The approved eleven families are preserved. Private asset copies extend LOD coverage while keeping the collection's original shapes, placements and material character.</p></div><div class="gallery">''' + cards + '''</div>
<div class="plain-note">Forty pilot families now have three actual LODs. Two small stone meshes and the 12-triangle water tile remain intentionally minimal. Water geometry totals 2,280 placed triangles, down from 1,444,672 inherited LOD0 triangles. This is a geometry reduction, not an attributed frame-rate improvement.</div>
<div class="receipt-links"><a href="../RemainingArt/README.md">Art sources and admission ↗</a><a href="../RemainingEnvironment/README.md">Environment and water ↗</a><a href="RiverB/unreal-viewport.png">Later river animation sample ↗</a></div></section>
<section class="section" id="validation"><div class="section-head"><span class="index">02 /</span><h2>Tested in<br>the editor.</h2><p>Three fresh workers owned separate art, environment and runtime folders. One coordinator integrated, captured and validated everything in Unreal.</p></div>
<table class="results"><thead><tr><th>Check</th><th>Result</th><th>What it establishes</th></tr></thead><tbody>
<tr><td>Save / switch map / reopen</td><td>Passed</td><td>Assignments, materials, visibility, counts and transforms persist.</td></tr>
<tr><td>Cottage, stairs, both bridge spans</td><td>8 checkpoints passed</td><td>CharacterMovement traversal with gravity and collision.</td></tr>
<tr><td>Four-building automatic LOD sweep</td><td>543 samples · 20 captures</td><td>Automatic settings and sampled visible building integrity.</td></tr>
<tr><td>Fresh idle gameplay view</td><td>16.67 ms mean · 16.91 ms p95</td><td>1,800 editor world-frame samples over 30 seconds.</td></tr>
<tr><td>Slowest sampled frame</td><td>54.98 ms</td><td>One frame exceeded 50 ms; continuous 60 fps is not guaranteed.</td></tr>
<tr><td>Collision query mean</td><td>33.48 µs simple · 35.18 µs complex</td><td>484 traces per mode including Python/engine-call overhead.</td></tr>
</tbody></table>
<div class="plain-note">The final idle sample ran separately from imports, sweeps, captures, collision probes and background Blender exports. The existing Blender window remained open. These measurements include editor overhead and do not establish shipping, GPU or city-scale budgets. The earlier popup-obscured sample is excluded.</div>
<div class="receipt-links"><a href="persistence.json">Persistence receipt ↗</a><a href="traversal-receipt.json">Traversal receipt ↗</a><a href="../RuntimeCompletion/Validation.md">Runtime evidence and limits ↗</a><a href="../RuntimeCompletion/FinalBuildings/automatic-lod-sweep.json">Automatic LOD sweep ↗</a></div></section>
<section class="section"><div class="section-head"><span class="index">03 /</span><h2>What comes<br>next.</h2><p>Homestead art is integrated. Interactive acceptance and the next gameplay scope remain distinct steps.</p></div><div class="family-list"><div><h3>Interactive acceptance</h3><p>Physical held-key WASD/mouse behavior and continuous LOD transition smoothness remain unverified. Static samples cannot certify every intermediate frame.</p></div><div><h3>Structural collision</h3><p>All 17 art placements match inherited collision settings. Dense building geometry still triggers navigation-export warnings; simpler structural collision needs a dedicated pass.</p></div><div><h3>Beyond the home</h3><p>Character presentation, connected neighborhoods, navigation, district budgets and world streaming remain future work. Settlement-growth gameplay is not implemented.</p></div></div><div class="receipt-links"><a href="Review.md">Complete continuation notes ↗</a><a href="../../START_HERE.md">Compact handoff ↗</a><a href="../review.html">Historical pilot review ↗</a></div></section></main>
<footer class="footer"><span>Terrarium · StartingHome</span><span>Native captures · Source-backed evidence</span></footer></body></html>'''
(DOCS / 'Completion/review.html').write_text(page, encoding='utf-8')
banner = '<aside style="padding:20px 5%;background:#303b24;color:#e4d8b8;border-bottom:1px solid #6c7f4c"><strong>Historical initial pilot.</strong> The remaining homestead collection is now integrated. <a href="Completion/review.html">Open the latest continuation review and validation ↗</a></aside>'
if 'Historical initial pilot.</strong>' not in original:
    original = original.replace('<body>', '<body>\n' + banner, 1)
    (DOCS / 'review.html').write_text(original, encoding='utf-8')
print('Wrote completion review and historical-review notice.')
