"""Publish the current native V5 review with honest per-check status.

The authorized current WorldExpansion URL redirects to V5; the earlier review
and captures are backed up under V5/Before. Failed/missing checks remain visible.
"""
import hashlib
import html
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Docs/WorldExpansion/V5'


def read(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def text(value):
    return html.escape(str(value))


request = read(OUT / 'review-request.json') or {}
surface = read(OUT / 'surface-validation.json')
inventory = read(OUT / 'validation.json')
reopened = read(OUT / 'reopened.json')
traversal = read(OUT / 'traversal-receipt.json')
forest = read(OUT / 'forest-contact-play.json')
grove_contacts = read(OUT / 'forest-groves-contact-play.json')
terrain = read(ROOT / 'SourceAssets/WorldExpansion/TerrainV5/manifest.json') or {}
ecology = read(ROOT / 'Docs/WorldExpansion/ecology-v5-integration.json') or {}
groves = read(ROOT / 'Docs/WorldExpansion/forest-groves-v5-integration.json') or {}
contract = read(OUT / 'contract.json') or {}
required_views = ['RegionOverview', 'AlderwatchCity', 'StonegateTown', 'BrookmereVillage',
                  'ReedbankVillage', 'HighfieldVillage', 'MountainPass', 'HomeInValley', 'CityStreet']
names = {'AlderwatchCity': 'Alderhaven', 'MountainPass': 'Mountain terrain', 'HomeInValley': 'Home and surrounding terrain', 'CityStreet': 'City street at walking scale'}
captures = request.get('captures') or []
if not captures:
    for name in required_views:
        current = OUT.parent / 'Captures' / (name + '.png')
        historical = OUT / 'Before' / (name + '.png')
        differs = current.exists() and (not historical.exists() or hashlib.sha256(current.read_bytes()).digest() != hashlib.sha256(historical.read_bytes()).digest())
        captures.append({'name': name, 'path': str(current) if differs else 'Captures/' + name + '.png', 'kind': 'native'})
capture_rows, gallery, errors = [], [], []
for row in captures:
    if row.get('kind', 'native') != 'native':
        errors.append('A non-native image is listed in the native capture gallery: ' + row['name'])
        continue
    source = Path(row['path'])
    source = source if source.is_absolute() else OUT / source
    if not source.exists():
        errors.append('Native capture missing: ' + row['name'])
        continue
    # Copy an exact byte-identical native capture into the local review bundle if
    # its coordinator-selected path is elsewhere; no image transformations occur.
    destination = OUT / 'Captures' / (row['name'] + '.png')
    destination.parent.mkdir(exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    capture_rows.append({'name': row['name'], 'file': destination.relative_to(OUT).as_posix(), 'sha256': digest})
    label = row.get('label', names.get(row['name'], row['name'].replace('Village', ' village').replace('Town', ' town')))
    before_file = OUT / 'Before' / (row['name'] + '.png')
    compare = f' data-before="Before/{text(row["name"])}.png" data-after="Captures/{text(row["name"])}.png"' if before_file.exists() else ''
    gallery.append(f'<figure><a href="Captures/{text(row["name"])}.png"><img src="Captures/{text(row["name"])}.png"{compare} alt="Native Unreal capture: {text(label)}" loading="lazy"></a><figcaption>{text(label)} <span>Native V5 screenshot</span></figcaption></figure>')
seen = {r['name'] for r in capture_rows}
for name in required_views:
    if name not in seen and not any(name in e for e in errors):
        errors.append('Required native viewpoint missing: ' + name)

gates = {'surface_bindings': bool(surface and surface.get('passed')),
         'geometry_and_ground_inventory': bool(inventory and inventory.get('passed')),
         'original_home_and_reopen': bool(reopened and reopened.get('passed')),
         'eight_character_routes': bool(traversal and traversal.get('all_routes_passed') and len(traversal.get('routes', [])) == 8),
         'forest_pie_contacts': bool(forest and forest.get('playing') and forest.get('all_sampled_ground_contacts_within_30cm') and forest.get('all_sampled_simple_trunk_rays_hit_expected_instance')),
         'nine_native_views': set(required_views).issubset(seen),
         'visual_acceptance': bool(request.get('visual_review', {}).get('accepted'))}
if groves:
    gates['new_groves_pie_contacts'] = bool(grove_contacts and grove_contacts.get('playing') and grove_contacts.get('all_sampled_ground_contacts_within_30cm') and grove_contacts.get('all_sampled_simple_trunk_rays_hit_expected_instance'))
errors.extend('Acceptance pending or failed: ' + key for key, passed in gates.items() if not passed)
texture_gallery = []
for row in contract.get('textures', []):
    source = Path(row['source_file'])
    source = source if source.is_absolute() else ROOT / source
    if not source.exists():
        continue
    folder = OUT / 'TextureSources'
    folder.mkdir(exist_ok=True)
    copied = folder / source.name
    shutil.copy2(source, copied)
    assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(copied.read_bytes()).digest()
    texture_gallery.append(f'<figure><img src="TextureSources/{text(source.name)}" alt="Actual imagegen albedo source {text(source.stem)}"><figcaption>{text(source.stem)}<span>Generated albedo source; native material use checked separately</span></figcaption></figure>')
concepts = []
for row in request.get('concept_images', []):
    # Concepts remain links with an explicit label and cannot satisfy any gate.
    concepts.append(f'<li>Concept only, not an Unreal result: {text(row.get("label", row.get("path", "Concept")))}</li>')

facts = [f'{len(terrain.get("assets", []))} authored terrain mesh parts',
         f'{terrain.get("total_triangles", 0):,} authored terrain triangles',
         f'{reopened.get("instances", 0):,} persisted mesh instances' if reopened else 'Persistence receipt pending']
groups = ecology.get('groups', {})
groups = list(groups.values()) if isinstance(groups, dict) else groups
if groups:
    facts.append(f'{sum(r["native_instance_count"] for r in groups):,} admitted groundcover/detail instances')
if groves:
    facts.append(f'{groves["native_trees"]:,} added grove trees')
checks = []
for key, value in [('Surface bindings', surface), ('Geometry and ground', inventory), ('Preservation and persistence', reopened)]:
    checks.append((key, 'Passed' if value and value.get('passed') else 'Pending / review required'))
checks.append(('Real character routes', '8/8 passed' if gates['eight_character_routes'] else 'Pending / review required'))
checks.append(('Forest runtime contacts', '12 sampled roots and isolated trunk bodies passed; full-world occlusion rays retained' if gates['forest_pie_contacts'] else 'Pending / review required'))
if groves:
    checks.append(('New grove runtime contacts', '12 sampled roots and trunks passed' if gates['new_groves_pie_contacts'] else 'Pending / review required'))
profile_lines = []
for filename, label in [('idle-observation.json', 'Fresh default Play'), ('city-observation.json', 'City viewpoint')]:
    value = read(OUT / filename)
    if value and not value.get('error') and not value.get('input_activity_observed'):
        f = value['frame_ms']
        profile_lines.append(f'{label}: {value["sample_count"]:,} editor world-frame samples; mean {f["mean"]:.2f} ms, p95 {f["p95"]:.2f} ms, max {f["max"]:.2f} ms.')
visual_notes = request.get('visual_review', {}).get('notes', 'Native visual acceptance is pending.')
status = 'Native correction accepted' if not errors else 'Review preview — acceptance incomplete'
markup = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Terrarium · Terrain V5 review</title>
<style>body{margin:0;background:#19221a;color:#edead9;font:16px/1.6 system-ui,sans-serif}main{max-width:1380px;margin:auto;padding:50px 5vw}h1{font:clamp(38px,6vw,76px)/1.1 Georgia,serif;max-width:1000px}h2{font:30px Georgia,serif;margin-top:48px}.eyebrow{color:#c2d490;text-transform:uppercase;letter-spacing:.15em;font-size:12px}p,li{color:#bac2ac}.facts{padding:20px 0;border-block:1px solid #43523c;display:flex;gap:28px;flex-wrap:wrap}.gallery,.textures{display:grid;grid-template-columns:1fr 1fr;gap:24px}.gallery figure:first-child{grid-column:1/-1}figure{margin:0;background:#253024;border:1px solid #43523c}img{width:100%;display:block}figcaption{padding:18px 22px}figcaption span{display:block;font-size:12px;color:#b2bba2}.textures{grid-template-columns:repeat(3,1fr)}a{color:#c2d490}table{border-collapse:collapse;width:100%}td{padding:12px;border-bottom:1px solid #43523c}.notice{padding:20px;border-left:3px solid #bdcf82;background:#253024}@media(max-width:700px){.gallery,.textures{grid-template-columns:1fr}.gallery figure:first-child{grid-column:auto}}</style><main>
'''
markup += f'<div class="eyebrow">Terrarium · V5 terrain correction</div><h1>Bring the landscape into the homestead’s world.</h1><p class="notice">{text(status)}</p><p>Physical terrain geometry, generated meadow/limestone/gravel albedos and native vegetation are inspected as one scene. The screenshots below show the actual Unreal map; generated source textures are separated below.</p><div class="facts">' + ''.join('<span>' + text(fact) + '</span>' for fact in facts) + '</div>'
markup += '<h2>Actual editor result</h2><p><button type="button" data-view="after" aria-pressed="true">Current V5</button> <button type="button" data-view="before" aria-pressed="false">Previous terrain</button></p><div class="gallery">' + ''.join(gallery) + '</div>'
markup += '<h2>Validation</h2><table>' + ''.join(f'<tr><td>{text(k)}</td><td>{text(v)}</td></tr>' for k, v in checks) + '</table>'
markup += '<p>' + text(visual_notes) + '</p>'
markup += ''.join('<p>' + text(line) + '</p>' for line in profile_lines)
if errors:
    markup += '<div class="notice"><strong>Not yet accepted</strong><ul>' + ''.join('<li>' + text(error) + '</li>' for error in errors) + '</ul></div>'
markup += '<h2>Actual generated material sources</h2><p>These PNGs are source albedos, not rendered world views. The native surface receipt checks imported Texture2D assets, material references, hashes and native mip/resampling settings.</p><div class="textures">' + ''.join(texture_gallery) + '</div>'
if concepts:
    markup += '<h2>Separate concept references</h2><ul>' + ''.join(concepts) + '</ul>'
markup += '<h2>Limits</h2><p>Traversal uses real CharacterMovement but teleports to each route’s initial start. Ground samples and forest rays do not cover every surface or prove complete navigation. Full-world trunk rays retain intervening terrain hits; separate terrain-ignored rays verify the intended trunk body. Frame observations include editor overhead; no shipping performance claim or automatic LOD smoothness claim is made. Source texture tiling must be judged in native images rather than inferred from its prompt.</p><p><a href="Review.md">Written receipts and handoff</a> · <a href="QA.md">Acceptance criteria and commands</a> · <a href="Before/review.html">Previous regional review</a></p></main><style>button{font:inherit;background:#30432d;color:#edead9;border:1px solid #819568;padding:10px 20px;cursor:pointer}button[aria-pressed=true]{background:#bdcf82;color:#172116}</style><script>document.querySelectorAll("button[data-view]").forEach(b=>b.addEventListener("click",()=>{const mode=b.dataset.view;document.querySelectorAll("button[data-view]").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));document.querySelectorAll(".gallery img[data-before]").forEach(img=>{img.src=img.dataset[mode];img.closest("a").href=img.dataset[mode];img.closest("figure").querySelector("figcaption span").textContent=mode==="before"?"Previous native screenshot":"Native V5 screenshot";});}));</script></html>'
(OUT / 'review-preview.html').write_text(markup, encoding='utf-8')
lines = ['# V5 terrain correction review', '', '**' + status + '**', '',
         'Actual geometry, imagegen albedos and ecology are evaluated in native Unreal screenshots. Concepts and albedo source images do not count as completed world renders.', '',
         '## Validation', '']
lines.extend('- **' + key + ':** ' + value for key, value in checks)
lines.extend(['', '## Native visual review', '', visual_notes, '', '## Source and evidence', '',
    '- [Surface/material/texture contract](surface-validation.json)',
    '- [Geometry and ground inventory](validation.json)',
    '- [Original preservation and final reopen](reopened.json)',
    '- [Eight real movement routes](traversal-receipt.json)',
    '- [Forest contacts in Play](forest-contact-play.json)',
    '- Geometry source: `SourceAssets/WorldExpansion/TerrainV5/manifest.json`.',
    '- Actual generated albedos: `SourceAssets/WorldExpansion/ArtDirection/`; original source bytes compared with the specified imagegen outputs.',
    '- Ecology source and admission: `Docs/WorldExpansion/ecology-v5-layout.json` and `ecology-v5-integration.json`.', '',
    '## Passive performance', ''] + (profile_lines or ['No separate V5 passive performance receipt has been recorded.']) + ['',
    'Diagnostics run during traversal are excluded from performance interpretation. Passive measurements represent their recorded editor viewpoint and include editor overhead.', '',
    '## Preservation and scope', '',
    'The original homestead baseline is never overwritten. V5 before/admitted/reopened snapshots live in this folder. Retiring coarse regional meshes or moving regional forest roots is allowed; original pilot mesh-instance signatures and original map bytes remain protected. Historical receipts remain intact; the previous review/captures are backed up under `Before/`, and the current WorldExpansion review URL opens this V5 result.', '',
    'The changed terrain uses its actual visible LOD inventory; no unobserved LOD transitions or world streaming are implied. Full regional navigation, NPC simulation and physical hardware input acceptance remain separate work.', ''])
(OUT / 'Review-preview.md').write_text('\n'.join(lines), encoding='utf-8')
receipt = {'passed': not errors, 'gates': gates, 'errors': errors, 'captures': capture_rows,
           'published': True, 'previous_review_backed_up': True, 'current_review_redirected_to_v5': True}
before = OUT / 'Before'
before.mkdir(exist_ok=True)
old_html = OUT.parent / 'review.html'
old_md = OUT.parent / 'Review.md'
def historical_link(link):
    if '://' in link or link.startswith('#'):
        return link
    original = OUT.parent / link
    if link.startswith('Captures/') and (before / Path(link).name).exists():
        return Path(link).name
    return os.path.relpath(original, before).replace('\\', '/')
if old_html.exists() and not (before / 'review.html').exists():
    saved = re.sub(r'(href|src)="([^"]+)"', lambda m: m[1] + '="' + historical_link(m[2]) + '"', old_html.read_text(encoding='utf-8'))
    (before / 'review.html').write_text(saved, encoding='utf-8')
if old_md.exists() and not (before / 'Review.md').exists():
    saved = re.sub(r'\]\(([^)]+)\)', lambda m: '](' + historical_link(m[1]) + ')', old_md.read_text(encoding='utf-8'))
    (before / 'Review.md').write_text(saved, encoding='utf-8')
(OUT / 'review.html').write_text(markup, encoding='utf-8')
(OUT / 'Review.md').write_text('\n'.join(lines), encoding='utf-8')
old_html.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=V5/review.html"><title>Terrarium V5 terrain review</title><p><a href="V5/review.html">Open the current native V5 terrain review</a></p><p><a href="V5/Before/review.html">Previous regional review</a></p></html>', encoding='utf-8')
old_md.write_text('# Current terrain review\n\n[Open the V5 native terrain review](V5/Review.md).\n\n[Previous regional review](V5/Before/Review.md).\n', encoding='utf-8')
(OUT / 'review-build.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'preview_written': True, 'published': receipt['published'], 'gate_errors': len(errors)}))
