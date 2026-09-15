"""Generate the offline source-to-reconstruction catalog from current build receipts.

Host-side standard-library only. Does not import recipes, call Unreal, or alter
images. Run again after builds/renders to refresh Docs/Reconstruction outputs.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import struct
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = '/Game/Terrarium/Reconstruction'

ALIASES = {
    'player_back': ('humanoids', 'player_front', 'alternate_view_reference'),
    'player_animation_atlas': ('humanoids', 'player_front', 'animation_reference_static_geometry_only'),
    'player_back_animation_atlas': ('humanoids', 'player_front', 'animation_reference_static_geometry_only'),
    'ranger_sela_animation_atlas': ('humanoids', 'ranger_sela', 'animation_reference_static_geometry_only'),
    'lodge_contact_shadow_v3': ('architecture', 'lodge', 'legacy_contact_shadow_physical_lighting_support'),
}
ENVIRONMENT = {
    'tree': 'SM_Recon_AncientTree', 'homestead_tree_v2': 'SM_Recon_HomesteadTree',
    'meadow_shrub': 'SM_Recon_MeadowShrub', 'rock': 'SM_Recon_MossRock',
    'wheat_field': 'SM_Recon_WheatField', 'homestead_riverbank_v2': 'SM_Recon_Riverbank',
    'river_crossing': 'SM_Recon_RiverCrossing',
}
ICONS = {'grove', 'ember', 'tide', 'storm', 'ember_crest', 'deep_delver_mark'}


def literal_specs(path):
    """Inspect recipe declarations without importing meshkit or running builders."""
    if not path.exists():
        return {}
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SPECS' for t in node.targets):
            try:
                return ast.literal_eval(node.value)
            except (ValueError, TypeError):
                return {}
    return {}


def recipe_mesh_name(path, builder_key, fallback):
    """Resolve the Mesh literal inside a named builder, when no literal SPECS exist."""
    if not path.exists():
        return fallback
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    function_name = builder_key
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BUILDERS' for t in node.targets) and isinstance(node.value, ast.Dict):
            for key, value in zip(node.value.keys, node.value.values):
                if isinstance(key, ast.Constant) and key.value == builder_key and isinstance(value, ast.Name):
                    function_name = value.id
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            for call in ast.walk(node):
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'Mesh' and call.args and isinstance(call.args[0], ast.Constant):
                    return call.args[0].value
    return fallback


def collect_receipts(directory):
    grouped = defaultdict(list)
    warnings = []
    for path in sorted(directory.glob('*.json')):
        try:
            row = json.loads(path.read_text(encoding='utf-8-sig'))
            assert isinstance(row, dict) and all(k in row for k in ('module', 'key', 'asset', 'name'))
            row = dict(row)
            row['revision'] = int(row.get('revision', 1))
            row['receipt'] = path.relative_to(directory.parent).as_posix()
            row['_mtime_ns'] = path.stat().st_mtime_ns
            grouped[(row['module'], row['key'])].append(row)
        except (OSError, ValueError, TypeError, AssertionError, json.JSONDecodeError) as exc:
            warnings.append(f'Skipped incomplete or invalid receipt {path.name}: {type(exc).__name__}')
    latest = {}
    history = {}
    for key, rows in grouped.items():
        rows.sort(key=lambda r: (r['revision'], r['_mtime_ns'], r['receipt']))
        for row in rows:
            del row['_mtime_ns']
        latest[key] = rows[-1]
        history[key] = rows
    return latest, history, warnings


def paths_and_roles(source, recipe_dir):
    stem = source.stem
    if stem in ALIASES:
        module, key, role = ALIASES[stem]
    elif stem.startswith(('terrain_', 'cottage_plaster_', 'cottage_roof_tile_')):
        module, key, role = 'surfaces', stem, 'source_color_texture_on_authored_relief_geometry'
    elif stem in ENVIRONMENT:
        module, key, role = 'environment', stem, 'environment_object_form_reference'
    elif stem == 'homestead_compound':
        module, key, role = 'compound', stem, 'composite_environment_form_reference'
    elif stem in ('player_front', 'ranger_sela'):
        module, key, role = 'humanoids', stem, 'character_form_reference_static_geometry'
    elif stem in ('lodge', 'cottage', 'civic_hall', 'market_stall', 'lantern', 'sign'):
        module, key, role = 'architecture', stem, 'architectural_object_form_reference'
    elif stem in ICONS:
        module, key, role = 'creatures_items', stem, 'ui_icon_interpreted_as_physical_3d_symbol'
    elif stem in ('moss_tonic', 'trail_prism'):
        module, key, role = 'creatures_items', stem, 'item_icon_interpreted_as_physical_3d_collectible'
    else:
        module, key, role = 'creatures_items', stem, 'creature_form_reference_static_geometry'
    specs = literal_specs(recipe_dir / (module + '.py'))
    fallback = ENVIRONMENT.get(key, 'SM_Recon_' + key)
    if module == 'compound':
        fallback = 'SM_Recon_HomesteadCompound'
    spec = specs.get(key, {})
    name = spec.get('name', spec.get('mesh', recipe_mesh_name(recipe_dir / (module + '.py'), key, fallback)))
    return module, key, role, name


def collect(root, output):
    latest, history, warnings = collect_receipts(output / 'Builds')
    source_dir = root / 'SourceAssets/Voxel'
    recipe_dir = root / 'Scripts/Reconstruction'
    sources = sorted(source_dir.glob('*.png'))
    assert len(sources) == 77, f'Expected 77 original PNGs, found {len(sources)}; review source scope before changing expectation.'
    rows = []
    for source in sources:
        module, key, role, expected_name = paths_and_roles(source, recipe_dir)
        receipt = latest.get((module, key))
        flat_surface = receipt and receipt.get('surface_geometry') == 'continuous_flat_slab'
        if flat_surface:
            role = 'source_color_texture_on_continuous_flat_slab'
        name = receipt['name'] if receipt else expected_name
        asset = receipt['asset'] if receipt else PACKAGE + '/Meshes/' + name
        raw = source.read_bytes()
        assert raw[:8] == b'\x89PNG\r\n\x1a\n', source
        dimensions = list(struct.unpack('>II', raw[16:24]))
        renders = {}
        for view in ('front', 'back'):
            render = output / 'Renders' / (name + '-' + view + '.png')
            renders[view] = {'path': render.relative_to(output).as_posix(), 'exists': render.is_file(), 'selected_revision_only': True}
        package_file = root / 'Content' / Path(asset.removeprefix('/Game/')).with_suffix('.uasset')
        gaps = []
        if module == 'surfaces':
            gaps += ['Original rendered color artwork is applied to authored relief geometry; this is not geometry recovered from a normal or height map.', 'The color source retains baked lighting. No authored normal, roughness texture, metallic, ambient-occlusion or packed ORM set is certified.']
            if flat_surface:
                gaps[0] = 'Original sandstone color texture spans a single flat slab with no internal block joints or stepped relief; only the perimeter has a small bevel.'
        if module in ('humanoids',) or key in ('brambit', 'kindlehorn', 'rillip'):
            gaps += ['Static geometry only: no skeletal rig, skinning, animation clips or runtime controller is claimed.']
        if 'animation_reference' in role:
            gaps += ['The original atlas is associated with the same character mesh. Frame animation has not been converted into 3D motion.']
        if source.stem == 'lodge_contact_shadow_v3':
            gaps += ['Maps to the lodge geometry for physical ground-contact lighting support; no standalone shadow mesh is expected, and renderer shadow fidelity remains to be reviewed.']
        if 'physical_3d' in role:
            gaps += ['Original UI/icon artwork is interpreted as a real object with modeled depth and reverse geometry; no production inventory/UI behavior is implied.']
        if key == 'kindlehorn' and receipt and receipt['revision'] >= 6:
            gaps += ['Horn-only emissive material and animated Niagara sparks are included in BP_Kindlehorn_R6 under Reconstruction/Blueprints. The Characters gallery includes the attached spark system and local horn light. Particle motion, fade and respawn were checked in editor; the creature itself remains an unrigged static mesh.']
        elif key in ('moss_tonic', 'trail_prism', 'kindlehorn'):
            gaps += ['Geometry and palette do not by themselves certify glass transmission, luminous cores or physically matching materials.']
        if module == 'compound':
            gaps += ['Composite source is an authored arrangement of modeled environment parts; playable navigation, interactions and world integration are separate verification.']
        gaps += ['Package or render existence does not establish fidelity acceptance. Inspect the current source/render comparison and the selected build receipt.']
        row = {
            'source': source.name, 'local_source': source.relative_to(root).as_posix(),
            'source_image': '../../SourceAssets/Voxel/' + quote(source.name),
            'source_sha256': hashlib.sha256(raw).hexdigest(), 'source_dimensions': dimensions,
            'source_role': role, 'module': module, 'builder_key': key,
            'expected_base_mesh': expected_name, 'selected_mesh': name, 'selected_asset': asset,
            'selected_revision': receipt['revision'] if receipt else None,
            'status': 'saved_build_receipt_present' if receipt else 'build_receipt_pending',
            'visual_acceptance': receipt.get('visual_acceptance', 'not_recorded') if receipt else 'pending_build_and_independent_comparison',
            'acceptance_claimed_by_catalog': False,
            'package_exists_on_disk': package_file.is_file(),
            'latest_build_receipt': receipt, 'revision_history': history.get((module, key), []),
            'renders': renders,
            'source_color_material': '/Game/Terrarium/Migration/Materials/MI_Surface_' + source.stem if module == 'surfaces' else None,
            'intended_review_map': PACKAGE + '/Maps/ReviewStage', 'gaps': gaps,
        }
        rows.append(row)
    identities = {(r['module'], r['builder_key']) for r in rows}
    assert len(identities) == 72, f'Expected 72 distinct reconstruction keys, got {len(identities)}'
    meshes = []
    for module, key in sorted(identities):
        associated = [r for r in rows if (r['module'], r['builder_key']) == (module, key)]
        r = associated[0]
        meshes.append({'module': module, 'key': key, 'sources': [a['source'] for a in associated], 'selected_mesh': r['selected_mesh'], 'selected_asset': r['selected_asset'], 'revision': r['selected_revision'], 'status': r['status'], 'visual_acceptance': r['visual_acceptance'], 'renders': r['renders'], 'receipt': r['latest_build_receipt']['receipt'] if r['latest_build_receipt'] else None})
    summary = {
        'original_pngs': len(rows), 'distinct_reconstruction_meshes': len(meshes),
        'meshes_by_module': dict(Counter(m['module'] for m in meshes)),
        'meshes_with_build_receipts': sum(m['status'] == 'saved_build_receipt_present' for m in meshes),
        'meshes_waiting_for_build_receipts': sum(m['status'] == 'build_receipt_pending' for m in meshes),
        'sources_with_build_receipts': sum(r['latest_build_receipt'] is not None for r in rows),
        'meshes_with_current_front_renders': sum(m['renders']['front']['exists'] for m in meshes),
        'meshes_with_current_back_renders': sum(m['renders']['back']['exists'] for m in meshes),
        'fidelity_acceptance_claims_from_existence': 0,
    }
    return {'schema_version': 1, 'generated_utc': datetime.now(timezone.utc).isoformat(), 'generator': 'Scripts/Reconstruction/catalog.py', 'scope': 'All 77 copied original voxel PNGs; 72 distinct expected reconstruction builders.', 'revision_policy': 'Select maximum numeric revision per module+key; receipt mtime and filename break equal-revision ties. Only exact selected mesh-name render files are shown; older revision renders never substitute silently.', 'evidence_policy': 'Build receipts and image existence are reported independently. This catalog never infers visual acceptance from either. Source roles distinguish animation associations, legacy shadow support, texture inputs and actual 3D object interpretations.', 'summary': summary, 'warnings': warnings, 'meshes': meshes, 'assets': rows}


def write_html(data, output):
    e = html.escape
    cards = []
    for row in data['assets']:
        frames = [f'<figure><a href="{e(row["source_image"], quote=True)}" target="_blank" rel="noopener"><img src="{e(row["source_image"], quote=True)}" alt="Original {e(row["source"], quote=True)}" loading="lazy" decoding="async"></a><figcaption>Original · {row["source_dimensions"][0]} × {row["source_dimensions"][1]}</figcaption></figure>']
        for view, render in row['renders'].items():
            if render['exists']:
                url = quote(render['path'], safe='/')
                frames.append(f'<figure><a href="{url}" target="_blank" rel="noopener"><img src="{url}" alt="Selected mesh {e(view)} render" loading="lazy" decoding="async"></a><figcaption>Current {view} render · inspect fidelity</figcaption></figure>')
            else:
                frames.append(f'<figure><div class="pending">{view.capitalize()} render pending<span>Exact selected mesh revision only</span></div><figcaption>{view.capitalize()} comparison</figcaption></figure>')
        revision = 'Pending build' if row['selected_revision'] is None else 'Revision ' + str(row['selected_revision'])
        receipt = row['latest_build_receipt']
        receipt_html = f'<a href="{quote(receipt["receipt"], safe="/")}">Selected build receipt</a> · {receipt.get("triangles", "unreported")} triangles · {receipt.get("saved_normal_errors", "unreported")} saved normal errors' if receipt else 'No completed build receipt is present for this key.'
        search = ' '.join([row['source'], row['module'], row['source_role'], row['builder_key'], row['selected_mesh'], row['status']]).lower()
        gaps = ''.join('<li>' + e(g) + '</li>' for g in row['gaps'])
        surface = '<p>Applied source-color material: <code>' + e(row['source_color_material']) + '</code></p>' if row['source_color_material'] else ''
        cards.append(f'<article class="card" data-search="{e(search, quote=True)}" data-module="{e(row["module"])}" data-status="{e(row["status"])}"><div class="card-heading"><div><p class="eyebrow">{e(row["module"].replace("_", " "))}</p><h2>{e(row["source"])}</h2></div><span class="badge">{e(revision)}</span></div><div class="comparisons">{"".join(frames)}</div><div class="body"><p class="role">{e(row["source_role"].replace("_", " "))}</p><p><code>{e(row["selected_asset"])}</code></p><p class="evidence">{receipt_html}</p><p class="review">Review status from receipt: {e(str(row["visual_acceptance"]).replace("_", " "))}</p><details><summary>Source role and conversion limits</summary>{surface}<ul>{gaps}</ul></details></div></article>')
    summary = data['summary']
    modules = ''.join(f'<option value="{e(m)}">{e(m.replace("_", " "))}</option>' for m in sorted(summary['meshes_by_module']))
    template = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>Terrarium · Reconstruction comparisons</title><style>
:root{color-scheme:dark;font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;background:#141918;color:#e3e8df}*{box-sizing:border-box}body{margin:0}header,main,footer{max-width:1740px;margin:auto;padding:26px 30px}header{padding-top:45px}h1{font-size:clamp(30px,4vw,50px);font-weight:630;letter-spacing:-.04em;margin:9px 0 18px;line-height:1.1}.eyebrow{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#acd0a3;margin:0}.intro{max-width:1050px;color:#b0bdb1}.stats{display:flex;flex-wrap:wrap;gap:13px 30px;margin:22px 0;color:#b0bdb1;font-size:13px}.stats strong{font-size:25px;font-weight:600;color:#e2eadc;margin-right:5px}a{color:#bed4b0;text-underline-offset:3px}.nav{display:flex;gap:22px;flex-wrap:wrap;font-size:13px}.notice{max-width:1100px;background:#222a22;border:1px solid #40503e;border-radius:9px;padding:13px 16px;color:#bdc8b5;font-size:13px}.filters{display:grid;grid-template-columns:1fr 210px 240px auto;gap:12px;align-items:end;margin-bottom:15px}label{display:block;font-size:12px;color:#a9b7a9;margin-bottom:6px}input,select,button{background:#222b24;border:1px solid #425241;color:#e5eddf;border-radius:7px;padding:11px;font:inherit;width:100%;min-height:46px}button{cursor:pointer}input:focus,select:focus,button:focus,a:focus,summary:focus{outline:2px solid #c7dea9;outline-offset:3px}button:hover{background:#344032}#count{font-size:13px;color:#a7b5a4;margin-bottom:20px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;align-items:start}.card{border:1px solid #38483b;background:#1c241e;border-radius:12px;overflow:hidden}.card-heading{padding:17px 18px;display:flex;align-items:center;justify-content:space-between;gap:10px}h2{font-size:17px;margin:4px 0 0;overflow-wrap:anywhere}.badge{font-size:11px;white-space:nowrap;background:#354830;color:#cde0bb;border-radius:5px;padding:4px 7px}.comparisons{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:2px;background:#394339}figure{margin:0;min-width:0;background:#101710}figure a{display:flex;aspect-ratio:1;align-items:center;justify-content:center}figure img{display:block;width:100%;height:100%;object-fit:contain}figcaption{font-size:10px;color:#a2afa0;padding:7px 8px;background:#202921;text-align:center;min-height:42px}.pending{aspect-ratio:1;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:12px;text-align:center;color:#adbba4;font-size:13px}.pending span{font-size:10px;color:#758470;margin-top:8px}.body{padding:13px 18px 17px}.body p{margin:6px 0}.role{color:#b2c5a4;font-size:12px}code{font:11px/1.4 ui-monospace,Consolas,monospace;overflow-wrap:anywhere;color:#b8c6b1}.evidence,.review{color:#94a48e;font-size:11px}details{border-top:1px solid #364537;margin-top:13px;padding-top:12px;font-size:12px;color:#a6b59e}summary{cursor:pointer;color:#c0d1b4}ul{padding-left:18px}li{margin:7px 0}footer{color:#8ea086;font-size:12px;padding-bottom:35px}[hidden]{display:none!important}#empty{padding:35px;text-align:center;color:#b7c6ae}@media(max-width:1150px){.grid{grid-template-columns:1fr}.filters{grid-template-columns:1fr 1fr}.filters .search{grid-column:1/-1}.filters button{grid-column:1/-1}}@media(max-width:600px){header,main,footer{padding-left:14px;padding-right:14px}.filters{grid-template-columns:1fr}.filters>*{grid-column:1/-1}.comparisons{grid-template-columns:1fr 1fr}.comparisons figure:last-child{grid-column:2;grid-row:2}.comparisons figure:first-child{grid-column:1;grid-row:1/3}.comparisons figure:first-child a{position:sticky;top:0}.card-heading{align-items:flex-start}.badge{white-space:normal}figcaption{font-size:9px}.stats{gap:10px 20px}}
</style></head><body><header><p class="eyebrow">Terrarium / reconstruction review</p><h1>Originals beside the modeled assets</h1><p class="intro">All 77 original voxel images are mapped to 72 distinct reconstruction builders. Each card pairs the original with the newest receipted mesh revision and its exact front/back render files. Missing results remain visibly pending.</p><div class="stats"><span><strong>77</strong> original PNGs</span><span><strong>72</strong> mesh destinations</span><span><strong>__BUILT__</strong> build receipts</span><span><strong>__FRONT__</strong> current front renders</span><span><strong>__BACK__</strong> current back renders</span></div><nav class="nav"><a href="coverage.md">Coverage report</a><a href="asset-map.json">Source-to-mesh JSON</a><a href="../../SourceAssets/Voxel/PROVENANCE.md">Original provenance</a></nav><p class="notice">A saved package, receipt or render is evidence of execution, not artistic acceptance. Character atlases share their character's static mesh; the lodge shadow reference maps to physical lodge lighting support. Surface sources remain color textures on authored relief geometry. UI symbols are interpreted as physical 3D objects. Read each card's role and limits.</p></header><main><div class="filters"><div class="search"><label for="search">Search source, mesh, module or role</label><input id="search" type="search" placeholder="Try rillip, atlas, terrain or relief…" autocomplete="off"></div><div><label for="module">Modeling group</label><select id="module"><option value="">All groups</option>__MODULES__</select></div><div><label for="status">Build receipt</label><select id="status"><option value="">All receipt states</option><option value="saved_build_receipt_present">Receipt present</option><option value="build_receipt_pending">Receipt pending</option></select></div><button type="button" id="reset">Reset filters</button></div><div id="count" role="status" aria-live="polite">Showing 77 original sources</div><noscript><p>All cards remain visible offline. JavaScript enables local filters only.</p></noscript><section id="cards" class="grid" aria-label="Original and model comparisons">__CARDS__</section><p id="empty" hidden>No sources match the selected filters.</p></main><footer>Generated __GENERATED__. Re-run <code>python Scripts/Reconstruction/catalog.py</code> after new builds or renders. Uses local files only; no external libraries, fonts, analytics or network requests. Full-resolution images open in a separate tab.</footer><script>
'use strict';const ids={search:document.getElementById('search'),module:document.getElementById('module'),status:document.getElementById('status')};const cards=Array.from(document.querySelectorAll('.card'));function update(){const words=ids.search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);let count=0;for(const card of cards){const show=(!ids.module.value||card.dataset.module===ids.module.value)&&(!ids.status.value||card.dataset.status===ids.status.value)&&words.every(w=>card.dataset.search.includes(w));card.hidden=!show;if(show)count++;}document.getElementById('count').textContent='Showing '+count+' of '+cards.length+' original sources';document.getElementById('empty').hidden=count!==0;}ids.search.addEventListener('input',update);ids.module.addEventListener('change',update);ids.status.addEventListener('change',update);document.getElementById('reset').addEventListener('click',()=>{for(const el of Object.values(ids))el.value='';update();ids.search.focus();});update();
</script></body></html>'''
    replacements = {'__BUILT__': str(summary['meshes_with_build_receipts']), '__FRONT__': str(summary['meshes_with_current_front_renders']), '__BACK__': str(summary['meshes_with_current_back_renders']), '__MODULES__': modules, '__CARDS__': '\n'.join(cards), '__GENERATED__': e(data['generated_utc'])}
    for needle, value in replacements.items():
        template = template.replace(needle, value)
    (output / 'catalog.html').write_text(template, encoding='utf-8')


def write_coverage(data, output):
    summary = data['summary']
    lines = ['# Reconstruction coverage', '', f"Generated {data['generated_utc']} from current build receipts and render files.", '', '[Open the visual comparison catalog](catalog.html) · [Machine-readable asset map](asset-map.json)', '', f"**77 original PNGs map to 72 distinct reconstruction builders.** {summary['meshes_with_build_receipts']} selected mesh revisions have completed build receipts; {summary['meshes_waiting_for_build_receipts']} are waiting. Current selected revisions have {summary['meshes_with_current_front_renders']} front renders and {summary['meshes_with_current_back_renders']} back renders.", '', 'A receipt reports saved geometry. A render reports an available image. Neither establishes accepted visual fidelity. The catalog reproduces each selected receipt’s visual-review status without promoting it based on file existence.', '', '## Distinct mesh scope', '', '| Module | Meshes |', '|---|---:|']
    lines += [f'| {key} | {count} |' for key, count in sorted(summary['meshes_by_module'].items())]
    lines += ['', '## Shared source associations', '', '- `player_front.png`, `player_back.png`, `player_animation_atlas.png` and `player_back_animation_atlas.png` map to `humanoids/player_front`. These are the actual copied source filenames; no `atlas_2x` source is present. Atlas association does not create skeletal animation.', '- `ranger_sela.png` and `ranger_sela_animation_atlas.png` map to `humanoids/ranger_sela`; motion remains separate work.', '- `lodge_contact_shadow_v3.png` maps to `architecture/lodge` as evidence for physical ground-contact lighting support. It does not require another standalone flat shadow mesh.', '', '## Image roles and material limits', '', '- 45 surface images are original color textures on authored three-dimensional relief tiles. Their lighting is baked into the source color; this does not certify normal, height, roughness or ORM reconstruction.', '- Grove, Ember, Tide, Storm, Ember Crest and Deep Delver Mark are modeled as physical volumetric symbols/emblems. Moss Tonic and Trail Prism are physical collectible interpretations. These associations do not imply a completed UI or inventory system.', '- Creature and humanoid meshes are static geometry. Unseen surfaces are authored interpretation; skeletal rigging and animation conversion are not established.', '- The composite homestead image maps to its own compound builder. World navigation, collision and gameplay integration require separate checks.', '', '## Revision policy', '', data['revision_policy'], '', 'The generator never imports recipe modules or calls the editor. It inspects literal declarations, reads receipts and checks exact render filenames. Run `python Scripts/Reconstruction/catalog.py` to refresh these three outputs.', '', '## Complete source coverage', '', '| Original PNG | Role | Selected mesh | Revision | Build receipt | Front | Back |', '|---|---|---|---:|---|---|---|']
    for r in data['assets']:
        source = f"[{r['source']}]({r['source_image']})"
        receipt = f"[present]({quote(r['latest_build_receipt']['receipt'], safe='/')})" if r['latest_build_receipt'] else 'pending'
        views = [f"[render]({quote(r['renders'][v]['path'], safe='/')})" if r['renders'][v]['exists'] else 'pending' for v in ('front','back')]
        lines.append(f"| {source} | {r['source_role']} | `{r['selected_mesh']}` | {r['selected_revision'] or '—'} | {receipt} | {views[0]} | {views[1]} |")
    if data['warnings']:
        lines += ['', '## Read warnings', ''] + ['- ' + w for w in data['warnings']]
    lines.append('')
    (output / 'coverage.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    output = root / 'Docs/Reconstruction'
    output.mkdir(parents=True, exist_ok=True)
    data = collect(root, output)
    (output / 'asset-map.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    write_html(data, output)
    write_coverage(data, output)
    print(json.dumps(data['summary'], indent=2))


if __name__ == '__main__':
    main()
