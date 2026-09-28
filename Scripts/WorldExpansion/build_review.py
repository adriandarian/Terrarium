"""Build a self-contained, receipt-backed review after coordinator native captures."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Docs/WorldExpansion'


def read(name):
    path = OUT / name
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def escape(value):
    return html.escape(str(value))


layout = read('settlement-layout.json') or {}
summary = dict(layout.get('summary', {}))
dressing = read('settlement-dressing-layout.json')
if dressing:
    detail = dressing.get('summary', {})
    summary['buildings'] = summary.get('buildings', 0) + detail.get('infill_buildings', 0)
    summary['actors'] = summary.get('actors', 0) + detail.get('actors', 0)
    summary['instances'] = summary.get('instances', 0) + detail.get('instances', 0)
validation = read('validation.json')
reopened = read('reopened.json')
traversal = read('traversal-receipt.json')
apron_traversal = read('home-apron-traversal.json')
idle = read('idle-observation.json')
city = read('city-observation.json')
forest = read('forest-contact-play.json') or read('forest-contact-validation.json')
collision = read('settlement-collision.json')
forest_collision = read('forest-collision.json')
forest_inventory = read('forest-integration.json') or {}
terrain_path = ROOT / 'SourceAssets/WorldExpansion/Terrain/manifest.json'
terrain = json.loads(terrain_path.read_text()) if terrain_path.exists() else {}
gorge_receipts = sorted(OUT.glob('terrain-gorge-*.json'))
apron_receipts = sorted(OUT.glob('terrain-apron-*.json'))
tributary_repair = read('tributary-seam-repair.json')
forest_trees = sum(g.get('instances', 0) for g in forest_inventory.get('groups', []) if 'BroadTree' in g.get('mesh', ''))
forest_undergrowth = sum(g.get('instances', 0) for g in forest_inventory.get('groups', []) if 'Shrub' in g.get('mesh', ''))
views = [
    ('RegionOverview', 'A valley beyond the homestead', 'The regional terrain, mountain rim and settlement network.'),
    ('AlderwatchCity', 'Alderhaven', 'Civic square, market streets, artisan blocks and garden courtyards.'),
    ('StonegateTown', 'Stonegate', 'An upland town with a fortified edge and a southern approach.'),
    ('BrookmereVillage', 'Brookmere', 'An orchard village gathered around a market green.'),
    ('ReedbankVillage', 'Reedbank', 'A lowland trading village with gardens and roadside commerce.'),
    ('HighfieldVillage', 'Highfield', 'A farming settlement below the mountain slopes.'),
    ('MountainPass', 'Mountain country', 'Angular peaks and broad slopes frame the inhabited valley.'),
    ('HomeInValley', 'The starting home, preserved', 'The approved home remains the player’s point of departure.'),
    ('CityStreet', 'At walking scale', 'Street-level buildings and details reuse the approved architectural families.'),
]
evidence = []
if reopened:
    evidence.append(('Preservation', 'Verified' if reopened.get('original_instances_preserved') and reopened.get('protected_maps_unchanged') else 'Needs review',
                     f"{reopened.get('instances', 0):,} total mesh instances inspected after reopen; original placements and protected map bytes compared.", 'reopened.json'))
    evidence.append(('Persistence', 'Verified' if reopened.get('passed') else 'Needs review',
                     'Mesh transforms, effective materials, visibility, component collision modes and camera activation checked across reopening.', 'reopened.json'))
else:
    evidence.append(('Preservation / persistence', 'Pending', 'The original baseline is recorded; save/reopen verification has not been recorded yet.', 'original-baseline.json'))
if validation:
    evidence.append(('Editor inventory', 'Passed' if validation.get('passed') else 'Needs review',
                     f"{validation.get('actor_count', 0)} expansion actors, {validation.get('mesh_count', 0)} mesh families and {len(validation.get('ground_probes', []))} ground checkpoints inspected; {len(validation.get('warnings', []))} warnings.", 'validation.json'))
else:
    evidence.append(('Editor inventory', 'Pending', 'LOD, material, transform and ground probe receipt has not been recorded yet.', None))
if collision:
    source_ok = all(r.get('source_disk_unchanged') for r in collision.get('native_mesh_evidence', []))
    before = collision.get('sum_collision_triangles_at_placements_before', 0)
    after = collision.get('sum_collision_triangles_at_placements_after', 0)
    evidence.append(('Settlement collision', 'Recorded' if source_ok else 'Needs review',
                     f"{len(collision.get('actor_changes', []))} settlement actors use private mesh copies with the authored third LOD for complex collision. Their triangle-placement proxy changes from {before:,} to {after:,} (about {before/1e6:.1f}M → {after/1e6:.1f}M). Original render geometry, materials and source files were checked. This proxy is not memory usage or a measured physics speedup.", 'settlement-collision.json'))
if forest:
    contacts_ok = forest.get('all_sampled_ground_contacts_within_30cm')
    trunks_ok = forest.get('all_sampled_simple_trunk_rays_hit_expected_instance')
    evidence.append(('Forest contacts', 'Recorded' if contacts_ok and trunks_ok else 'Needs review',
                     f"{forest.get('sampled_trees', 0)} tree samples checked in {'Play' if forest.get('playing') else 'the editor'} against terrain with foliage ignored; separate simple trunk rays identify the expected instance. The region uses a private tree mesh with a 30cm-radius, 260cm-tall simple trunk capsule; original tree assets stay unchanged. {len(forest.get('warnings', []))} review warnings. This does not establish capsule traversal through the forest.", 'forest-contact-play.json' if forest.get('playing') else 'forest-contact-validation.json'))
if traversal:
    successes = sum(r.get('passed', False) for r in traversal.get('routes', []))
    evidence.append(('Collision traversal', 'Passed' if traversal.get('all_routes_passed') else 'Needs review',
                     f"{successes}/{len(traversal.get('routes', []))} routes passed using possessed CharacterMovement, including the home-to-hub connection and both bank transitions across the full city river bridge. Initial position is teleported per route; segments use AddMovementInput.", 'traversal-receipt.json'))
else:
    evidence.append(('Collision traversal', 'Pending', 'Short routes through new streets and roads have not been recorded yet.', None))
if apron_traversal:
    evidence.append(('Final homestead transition', 'Passed' if apron_traversal.get('all_routes_passed') else 'Needs review',
                     'The home approach was walked again after the final apron terrain change. This supplements the eight-route receipt and checks the edited connection with real CharacterMovement.', 'home-apron-traversal.json'))
if idle:
    frame = idle.get('frame_ms', {})
    formatted = ', '.join(f"{key} {frame[key]:.2f} ms" for key in ('mean', 'p95', 'max') if frame.get(key) is not None)
    status = 'Recorded' if not idle.get('error') and not idle.get('input_activity_observed') else 'Needs review'
    evidence.append(('Fresh default Play', status,
                     f"{idle.get('sample_count', 0):,} editor world-frame samples; {formatted}. Includes editor overhead and is limited to this camera and scene state.", 'idle-observation.json'))
else:
    evidence.append(('Fresh default Play', 'Pending', 'Passive 20-second frame sample after five seconds of warmup has not been recorded yet.', None))
if city:
    frame = city.get('frame_ms', {})
    formatted = ', '.join(f"{key} {frame[key]:.2f} ms" for key in ('mean', 'p95', 'max') if frame.get(key) is not None)
    status = 'Recorded' if not city.get('error') and not city.get('input_activity_observed') and city.get('sample_count', 0) > 0 else 'Needs review'
    evidence.append(('City-view passive sample', status,
                     f"{city.get('sample_count', 0):,} editor world-frame samples at a selected city viewpoint; {formatted}. Separate from traversal and collision-query runs; not a shipping CPU/GPU profile.", 'city-observation.json'))

gallery = []
for filename, title, description in views:
    src = f'Captures/{filename}.png'
    available = (OUT / src).exists()
    media = f'<a href="{src}"><img src="{src}" alt="{escape(title)} — native Unreal editor capture" loading="lazy"></a>' if available else '<div class="placeholder">Native capture pending</div>'
    gallery.append(f'<figure>{media}<figcaption><h2>{escape(title)}</h2><p>{escape(description)}</p></figcaption></figure>')
cards = []
for title, status, description, receipt in evidence:
    link = f'<a href="{receipt}">Read receipt ↗</a>' if receipt else ''
    cards.append(f'<article><span class="status">{escape(status)}</span><h3>{escape(title)}</h3><p>{escape(description)}</p>{link}</article>')
markup = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Terrarium · Valley Region</title>
<style>
:root{color-scheme:dark;--ink:#eeeade;--muted:#b5b8a6;--line:#414a39;--accent:#c5d493}
*{box-sizing:border-box}body{margin:0;background:#1d241c;color:var(--ink);font:16px/1.6 system-ui,sans-serif}
main{max-width:1420px;margin:auto;padding:56px 5vw 80px}header{max-width:980px;margin-bottom:36px}
.eyebrow{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent)}
h1{font:clamp(38px,6vw,80px)/1.05 Georgia,serif;letter-spacing:-.03em;margin:18px 0 24px}p{color:var(--muted);margin:10px 0}
.intro{font-size:20px;max-width:880px}.facts{display:flex;gap:32px;flex-wrap:wrap;margin:32px 0 40px;padding:20px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.facts strong{display:block;font:32px Georgia,serif}.facts span{font-size:12px;color:var(--muted)}
.gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:30px}figure{margin:0;background:#242d22;border:1px solid var(--line)}figure:first-child{grid-column:1/-1}
img{width:100%;display:block;background:#11180f}figcaption{padding:20px 24px}h2{font:28px Georgia,serif;margin:0 0 6px}figcaption p{font-size:14px;margin:0}.placeholder{display:grid;place-items:center;min-height:300px;color:#8b947e;background:#20281e}
.evidence{margin-top:56px}.evidence>h2{margin-bottom:22px}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}article{border:1px solid var(--line);padding:24px}h3{margin:8px 0;font-size:20px}.status{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}.limits{margin-top:32px;padding-top:24px;border-top:1px solid var(--line);font-size:14px}code{font-size:13px;overflow-wrap:anywhere}@media(max-width:720px){main{padding-top:32px}.gallery,.cards{grid-template-columns:1fr}.facts{gap:22px}figure:first-child{grid-column:auto}}
</style><main><header><div class="eyebrow">Terrarium / World expansion</div><h1>From a home<br>to an inhabited valley.</h1><p class="intro">A regional city, an upland town and three villages extend the homestead’s warm timber, plaster and mossy stone language into a larger landscape of roads, water and mountain slopes.</p><p>Working map: <code>/Game/Terrarium/WorldExpansion/Maps/ValleyRegion</code></p></header>
'''
markup += f'<div class="facts"><div><strong>5</strong><span>authored settlements</span></div><div><strong>{summary.get("buildings", "—")}</strong><span>buildings in the layout manifest</span></div><div><strong>{summary.get("instances", "—"):,}</strong><span>settlement detail instances in the manifest</span></div></div>' if isinstance(summary.get('instances'), int) else ''
markup += f'<p class="intro">The region adds {forest_trees:,} forest trees and {forest_undergrowth:,} undergrowth instances. Its current source manifest contains {len(terrain.get("assets", []))} terrain, road, water, bridge and transition meshes.</p>'
markup += '<section class="gallery">' + ''.join(gallery) + '</section>'
markup += '<section class="evidence"><h2>What was checked</h2><div class="cards">' + ''.join(cards) + '</div></section>'
markup += '<div class="limits"><p>All pictured scenes are native Unreal captures. Authored counts describe the layout manifest; verification cards describe actual editor receipts.</p><p>Visual follow-up: the broad mineral terrain is noticeably simpler than the original homestead’s dense groundcover and fine stonework. The new apron and widened tributary close the earlier exposed water underside, but the terrain style transition remains visible. The three villages share a repeated street template.</p><p>This pass establishes a regional environment and limited collision coverage. It does not establish city simulation, NPC schedules, quests, navigation across every district, spatial streaming, held hardware input, complete automatic LOD acceptance, or a shipping performance budget.</p><p><a href="Review.md">Written review</a> · <a href="settlement-layout.json">Settlement manifest</a> · <a href="../START_HERE.md">Continuation handoff</a></p></div></main></html>'
(OUT / 'review.html').write_text(markup, encoding='utf-8')
lines = ['# Valley Region review', '',
         'Working map: `/Game/Terrarium/WorldExpansion/Maps/ValleyRegion`.', '',
         'Alderhaven is the regional city, Stonegate the upland town; Brookmere, Reedbank and Highfield form three village destinations. The original home remains the starting point. The expansion reuses approved building families and adds connected terrain, road surfaces, water and mountain slopes.', '',
         f"The authored settlement manifest contains **{summary.get('buildings', 'pending')} buildings**, {summary.get('actors', 'pending')} individual placements and {summary.get('instances', 'pending')} detail instances. These authored counts are separate from the scene readback below.", '',
         f"Private forest groups contain **{forest_trees:,} trees and {forest_undergrowth:,} undergrowth instances**. The effective terrain source is `SourceAssets/WorldExpansion/Terrain/manifest.json`, currently listing **{len(terrain.get('assets', []))} mesh sources** across terrain, roads, water, bridges and transitions. The region spans 1.6 × 1.6 km.", '',
         'Open [the visual review](review.html) for the native capture gallery.', '', '## Evidence', '']
for title, status, description, receipt in evidence:
    lines += [f'- **{title}: {status}.** {description}' + (f' [Receipt]({receipt}).' if receipt else '')]
lines += ['', '## Acceptance limits', '',
          'Ground probes check sampled simple/complex Visibility hits and expected elevations. Traversal uses the possessed explorer with real gravity and collision, but teleports to the start of each short route. Neither covers every path between settlements or proves physical keyboard input.', '',
          'The passive profile records editor world-frame deltas for one fresh default Play viewpoint. It is not a shipping GPU/CPU profile or a city simulation budget. Automatic LOD screen thresholds are inventoried; a full continuous visual transition review remains separate.', '',
          'Traversal frame deltas are excluded from the passive performance claims because diagnostic collision queries ran during that traversal session. Use the separate idle and city observation receipts for their stated viewpoints.', '',
          'Native visual review: the final city avenue has grounded architecture, coherent materials and a civic focal point. The river-gorge extrusion and exposed black water underside were repaired. The broad mineral terrain remains visibly simpler than the homestead’s rich groundcover and stone detail, including around the new apron. Village street layouts are repeated; more local identity and edge dressing remain worthwhile visual follow-up.', '',
          'NPC life, economy, quests, navigation across every district, spatial streaming and a complete terrain/settlement walk-through remain future work.', '',
          '## Reproducing the receipts', '',
          'Only the coordinator uses the connected Terrarium editor. End Play before `validate_world.py` or `snapshot_world.py`. The snapshot request names are `original-baseline`, `admitted` and `reopened`; the baseline refuses overwrite. After the admitted snapshot, save, switch to another map, reopen ValleyRegion and run the reopened snapshot.', '',
          'Run `validate_traversal.py` with `traversal-request.json`, then start Play. Stop that Play session after its receipt. For the idle profile, arm `observe_play.py` with `observation-request.json` and start a fresh Play session; perform no imports or captures during the five-second warmup and 20-second sample. Regenerate this review with `python Scripts/WorldExpansion/build_review.py` after captures and receipts.', '']
if gorge_receipts or apron_receipts or tributary_repair:
    lines += ['## Effective terrain replacements', '',
              'The initial admission receipts are historical for replaced chunks. The current stack is the source manifest plus `_GorgeV2` valley replacements, `_HomeApronV3` replacements/addition, and the tributary `_SeamV4` replacement. Later entries override earlier mesh bindings; `validation.json` and the reopened snapshot are authoritative.', '']
    effective = {}
    for path in gorge_receipts + apron_receipts:
        receipt = json.loads(path.read_text())
        for row in receipt.get('records', []):
            effective[row['actor']] = row['after']
        lines.append(f'- [{path.name}]({path.name})')
    if tributary_repair:
        effective[tributary_repair['actor']] = tributary_repair['after']
        lines.append('- [tributary-seam-repair.json](tributary-seam-repair.json)')
    lines += ['', '| Actor | Effective mesh |', '| --- | --- |']
    for actor, mesh in sorted(effective.items()):
        lines.append(f'| `{actor}` | `{mesh.split(".")[-1]}` |')
    lines.append('')
lines += ['## Source handoff', '',
          '- Working map: `/Game/Terrarium/WorldExpansion/Maps/ValleyRegion`; original StartingHome and HomesteadBlender map files remain protected by the baseline hash receipt.',
          '- Terrain source and geometry: `Scripts/WorldExpansion/terrain_source.py` and `SourceAssets/WorldExpansion/Terrain/manifest.json`. Apply source revisions through the coordinator’s native mesh admission/replacement scripts; existing admitted assets with different source hashes must receive explicit replacement handling.',
          '- Settlement placement sources: `settlement-layout.json` and additive `settlement-dressing-layout.json`. Their integration receipts record final mesh assignments, counts and native FoliageTypes.',
          '- Building collision copies: `/Game/Terrarium/WorldExpansion/Architecture/Meshes`; effective bindings are recorded in `settlement-collision-assets.json`. Render LODs and materials match the protected approved sources; authored LOD2 supplies complex collision.',
          '- Forest source placement list is in the terrain manifest. Private `/Game/Terrarium/WorldExpansion/Forest/SM_WX_BroadTree5m` carries the simple trunk capsule. `forest-contact-play.json` supersedes editor-world trunk misses for runtime query acceptance.',
          '- `reopened.json` is the final scene persistence authority when its passed flag is true. Named water NoCollision profiles are required for persistence; do not infer success from the earlier custom-profile state.',
          '- The nine PNGs in `Captures/` are native editor views. Rebuild this review after replacing captures or receipts with `python Scripts/WorldExpansion/build_review.py`.', '']
(OUT / 'Review.md').write_text('\n'.join(lines), encoding='utf-8')
print('WorldExpansion review generated from available receipts and native captures.')
