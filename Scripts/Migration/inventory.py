"""Read-only source inventory; emits JSON and Markdown under Docs/AssetMigration.

Run: python Scripts/Migration/inventory.py [--source PATH] [--output PATH]
No editor imports, third-party packages, or changes to the Godot project.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
TEXT_EXTS = {'.gd', '.tscn', '.tres', '.godot', '.gdshader', '.cfg', '.json', '.md', '.py'}
EXCLUDED = {'.git', '.godot', 'node_modules', '.venv', '__pycache__', 'build', 'dist'}
RESOURCE = re.compile(r'res://([^\s\"\'\)]+)')


def category(name):
    if name.endswith('.import'):
        return 'Godot import metadata'
    if name.endswith('.md'):
        return 'Documentation'
    if '_animation_atlas' in name:
        return 'Character animation atlases'
    if name.startswith(('player_', 'ranger_sela')):
        return 'Character references'
    if name in {'kindlehorn.png', 'brambit.png', 'rillip.png'}:
        return 'Creature references'
    if name.startswith(('terrain_', 'cottage_roof_', 'cottage_plaster_')):
        return 'Terrain and building surfaces'
    if name == 'lodge_contact_shadow_v3.png':
        return 'Contact shadow'
    if name in {'ember.png', 'tide.png', 'grove.png', 'storm.png', 'trail_prism.png', 'moss_tonic.png', 'ember_crest.png', 'deep_delver_mark.png'}:
        return 'Items and UI icons'
    if name in {'homestead_compound.png', 'homestead_riverbank_v2.png', 'river_crossing.png'}:
        return 'Composite environment references'
    if name in {'cottage.png', 'civic_hall.png', 'lodge.png', 'market_stall.png'}:
        return 'Buildings'
    return 'Vegetation and props'


def mesh_family(name):
    """Semantic candidates only; these rules do not establish faithful equivalence."""
    if name.startswith(('player_',)):
        return r'SM_Traveler(?:_|$)'
    if name in {'lodge.png', 'cottage.png'} or name.startswith(('cottage_roof_', 'cottage_plaster_')):
        return r'SM_Cottage(?:_|$)'
    if name in {'tree.png', 'homestead_tree_v2.png'} or name.startswith('terrain_foliage'):
        return r'SM_(?:Tree|OrchardTree|VoxelTree|Bush)(?:_|$)'
    if name == 'meadow_shrub.png':
        return r'SM_(?:Bush|GroundPlants)(?:_|$)'
    if name == 'wheat_field.png':
        return r'SM_WheatPatch(?:_|$)'
    if name == 'lantern.png':
        return r'SM_LanternPost(?:_|$)'
    if name == 'rock.png':
        return r'SM_(?:RockCluster|RiverStones|ShoreOutcrop)(?:_|$)'
    if name == 'river_crossing.png':
        return r'SM_(?:PlankBridge|WaterTile|ShoreOutcrop)(?:_|$)'
    if name == 'homestead_riverbank_v2.png':
        return r'SM_(?:RiverStones|ShoreOutcrop|Reeds|WaterTile)(?:_|$)'
    if name == 'homestead_compound.png':
        return r'SM_(?:Cottage|GardenBed|GardenWell|GardenShed|WheatPatch|PerimeterWall)(?:_|$)'
    if name.startswith('terrain_grass'):
        return r'SM_(?:GrassTile|MeadowTile|MeadowEdge)(?:_|$)'
    if name.startswith('terrain_water'):
        return r'SM_Water(?:Tile|Shallow|Deep)(?:_|$)'
    if name.startswith('terrain_trail'):
        return r'SM_PathTile(?:_|$)'
    if name.startswith('terrain_cliff'):
        return r'SM_(?:Cliff|VoxelCliff)[A-Za-z_0-9]*'
    if name.startswith('terrain_moss'):
        return r'SM_CliffMoss(?:_|$)'
    if name.startswith('terrain_stair'):
        return r'SM_StoneStairs(?:_|$)'
    if name.startswith('terrain_wood'):
        return r'SM_(?:PlankBridge|FencePost|FenceRail|LanternPost)(?:_|$)'
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('C:/Users/hello/Projects/Pokemon/assets/voxel'))
    parser.add_argument('--output', type=Path, default=ROOT / 'Docs/AssetMigration')
    args = parser.parse_args()
    source = args.source.resolve()
    godot = source.parents[1]
    files = sorted(p for p in source.rglob('*') if p.is_file())
    png_names = {p.name for p in files if p.suffix.lower() == '.png'}
    texts = {}
    for p in godot.rglob('*'):
        rel = p.relative_to(godot)
        if p.is_file() and p.suffix.lower() in TEXT_EXTS and not EXCLUDED.intersection(rel.parts):
            try:
                texts[rel.as_posix()] = p.read_text(encoding='utf-8-sig')
            except (UnicodeError, OSError):
                continue
    project = texts.get('project.godot', '')
    main_match = re.search(r'run/main_scene="res://([^"]+)"', project)
    main_scene = main_match.group(1) if main_match else None
    reached = set()
    queue = deque([main_scene] if main_scene else [])
    while queue:
        path = queue.popleft()
        if path in reached:
            continue
        reached.add(path)
        queue.extend(match for match in RESOURCE.findall(texts.get(path, '')) if match not in reached)
    usages = {name: [] for name in png_names}
    basename_pattern = re.compile('|'.join(re.escape(n) for n in sorted(png_names, key=len, reverse=True)))
    for rel, body in sorted(texts.items()):
        for number, line in enumerate(body.splitlines(), 1):
            for name in set(basename_pattern.findall(line)):
                usages[name].append({'file': rel, 'line': number, 'kind': 'documentation' if rel.endswith('.md') else 'code_or_data', 'reachable_from_main_by_literal_resource_paths': rel in reached, 'text': line.strip()[:600]})
    assets = sorted((ROOT / 'Content').rglob('*.uasset'))
    mesh_assets = [p for p in assets if p.stem.startswith('SM_')]
    recipes = {}
    for p in sorted((ROOT / 'Scripts').rglob('*.py')):
        if p == Path(__file__).resolve():
            continue
        for number, line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(), 1):
            for name in re.findall(r'\bSM_[A-Za-z0-9_]+', line):
                recipes.setdefault(name, []).append({'file': p.relative_to(ROOT).as_posix(), 'line': number})
    readme = (source / 'README.md').read_text(encoding='utf-8-sig')
    prompts = dict(re.findall(r'^\| `([^`]+)` \| (.*?) \|$', readme, re.M))
    records = []
    for p in files:
        raw = p.read_bytes()
        item = {'file': p.relative_to(source).as_posix(), 'category': category(p.name), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'kind': 'png' if p.suffix.lower() == '.png' else 'godot_import_metadata' if p.suffix == '.import' else 'documentation'}
        if item['kind'] == 'png':
            if raw[:8] != b'\x89PNG\r\n\x1a\n' or raw[12:16] != b'IHDR':
                raise ValueError(f'Invalid PNG header: {p}')
            width, height, depth, color_type = struct.unpack('>IIBB', raw[16:26])
            refs = usages[p.name]
            code_refs = [r for r in refs if r['kind'] == 'code_or_data']
            active_refs = [r for r in code_refs if r['reachable_from_main_by_literal_resource_paths']]
            status = 'reachable_reference' if active_refs else 'referenced_outside_main_dependency_graph' if code_refs else 'candidate_unreferenced' if 'candidate' in p.name else 'unreferenced_retained'
            family = mesh_family(p.name)
            matches = [a for a in mesh_assets if family and re.match(family, a.stem)]
            mapping = [{'asset': '/Game/' + a.relative_to(ROOT / 'Content').with_suffix('').as_posix(), 'package': a.relative_to(ROOT).as_posix(), 'recipe_or_usage_evidence': recipes.get(a.stem, [])} for a in matches]
            item.update(width=width, height=height, bit_depth=depth, png_color_type=color_type, alpha_channel=color_type in {4, 6}, candidate_filename='candidate' in p.name, usage_status=status, source_usages=refs, documented_subject=prompts.get(p.name), existing_terrarium_candidates=mapping, equivalence_status='not_verified', mapping_note='Semantic model-family candidates based on inspected recipes and existing package names; source-image identity and in-editor fidelity have not been established.' if matches else 'No corresponding existing model family established by this inventory.')
        elif item['kind'] == 'godot_import_metadata':
            item['source_png'] = p.name.removesuffix('.import')
            item['migration_action'] = 'retain in inventory only; Godot import metadata is not an Unreal asset'
        records.append(item)
    pngs = [r for r in records if r['kind'] == 'png']
    summary = {'files': len(records), 'pngs': len(pngs), 'godot_import_metadata': sum(r['kind'] == 'godot_import_metadata' for r in records), 'documentation': sum(r['kind'] == 'documentation' for r in records), 'total_bytes': sum(r['bytes'] for r in records), 'png_bytes': sum(r['bytes'] for r in pngs), 'categories_png_only': dict(Counter(r['category'] for r in pngs)), 'usage_status_png_only': dict(Counter(r['usage_status'] for r in pngs)), 'candidate_filenames': sum(r['candidate_filename'] for r in pngs), 'candidate_filenames_reachable': sum(r['candidate_filename'] and r['usage_status'] == 'reachable_reference' for r in pngs), 'pngs_with_existing_semantic_mesh_candidates': sum(bool(r['existing_terrarium_candidates']) for r in pngs), 'pngs_without_existing_semantic_mesh_candidates': sum(not r['existing_terrarium_candidates'] for r in pngs), 'verified_equivalent_migrations': 0}
    result = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'source_root': source.as_posix(), 'source_main_scene': main_scene, 'method': 'All source-directory files, SHA-256 hashes and PNG IHDR dimensions; text basename reference scan; literal res:// dependency traversal from project main scene. Static reachability does not prove visible runtime use, dynamic loads may be missed, and retained files are not automatically obsolete. Existing Unreal package candidates are semantic matches, not editor-verified migrations. This inventory does not modify source files or editor assets.', 'summary': summary, 'existing_terrarium_maps': [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / 'Content').rglob('*.umap'))], 'files': records}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'inventory.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    lines = ['# Godot voxel asset inventory', '', f"Source: `{source.as_posix()}`", '', f"**{summary['files']} files: {len(pngs)} PNGs, {summary['godot_import_metadata']} Godot `.import` sidecars, and {summary['documentation']} README.** PNGs total {summary['png_bytes']:,} bytes; all files total {summary['total_bytes']:,} bytes.", '', 'These are raster sprites, animation atlases, surface textures and composite references. No source mesh, rig, animation clip, or material-map bundle is present in this directory. Building a 3D model from a sprite is reconstruction; hidden surfaces require authored interpretation.', '', f"Godot main scene: `{main_scene}`. The inventory follows literal `res://` dependencies from this scene and records all matching text references. `reachable_reference` means static dependency evidence, not a visible-in-game test. Candidate filenames may be used by the current game. Unreferenced files are retained history or references, not automatically rejected art.", '', '## Counts', '', '| Category | PNGs |', '|---|---:|']
    lines += [f'| {key} | {value} |' for key, value in sorted(summary['categories_png_only'].items())]
    lines += ['', '| Source usage evidence | PNGs |', '|---|---:|']
    lines += [f'| {key} | {value} |' for key, value in sorted(summary['usage_status_png_only'].items())]
    lines += ['', f"There are {summary['candidate_filenames']} candidate-named PNGs; {summary['candidate_filenames_reachable']} are reachable from the current main scene. The source README's final claim of 19 files / roughly 25 MB describes an earlier subset and is not the current inventory.", '', '## Complete PNG list', '', 'Dimensions and full SHA-256 digests, every source usage with line numbers, and all candidate Unreal package mappings are in [inventory.json](inventory.json). Every PNG is listed below. Existing Unreal candidates are related model families only; none has been certified as an equivalent recreation by this inventory.', '']
    for group in sorted(summary['categories_png_only']):
        lines += [f'### {group}', '', '| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |', '|---|---:|---:|---|---|']
        for r in pngs:
            if r['category'] != group:
                continue
            mapped = r['existing_terrarium_candidates']
            names = ', '.join('`'+a['asset'].split('/')[-1]+'`' for a in mapped[:3])
            if len(mapped) > 3:
                names += f' (+{len(mapped)-3} variants; JSON)'
            lines.append(f"| `{r['file']}` | {r['width']} × {r['height']} | {r['bytes']:,} | {r['usage_status']} | {names or 'Unmapped'} |")
        lines.append('')
    lines += ['## Mapping gaps and source handling', '', f"- {summary['pngs_with_existing_semantic_mesh_candidates']} PNGs have related existing mesh-family candidates; {summary['pngs_without_existing_semantic_mesh_candidates']} have none. These counts cover individual image revisions, not unique subjects.", '- Existing traveler meshes are static authored characters and do not establish equivalence with the coral-jacket player or ranger. Sprite atlases do not provide skeletons or animation clips.', '- Surface images are generally lit color artwork, not authored normal, roughness, metallic, AO or height maps. Do not treat painted shadows as physically meaningful height. Review tiling, scale, color space and alpha per intended material.', '- Chroma-key backgrounds and the lodge contact-shadow sprite require special treatment. The README describes magenta removal in Godot; rebuilding full geometry should use actual contact and lighting rather than adding a rectangular sprite foundation.', '- Composite homestead and river images must map to compositions of reusable meshes, not be counted as a single completed mesh.', '- This inventory establishes no editor-verified equivalent migration. Existing semantic candidates require source-by-source visual comparison; missing categories need new models or UI imports.', '', '## Other files', '', '| File | Kind | Bytes |', '|---|---|---:|']
    lines += [f"| `{r['file']}` | {r['kind']} | {r['bytes']:,} |" for r in records if r['kind'] != 'png']
    lines += ['', '## Existing Unreal maps', ''] + [f'- `{p}`' for p in result['existing_terrarium_maps']]
    lines += ['', 'Map presence is verified from files only; it does not prove current editor contents, navigation, collision, or source-asset coverage.', '', '## Reproduce', '', 'Run `python Scripts/Migration/inventory.py` from Terrarium. The script uses only the Python standard library, reads the Godot project without modifying it, and replaces this Markdown and JSON inventory. PNG dimensions are validated from the PNG signature and IHDR header; full raster decoding and rendered visual review are separate checks.', '']
    (args.output / 'inventory.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
