"""Record Tide's physical-model checks without granting reference fidelity."""
import json,hashlib,struct,html
from pathlib import Path
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/Tide';src=root/'SourceAssets/Blender/Tide'
def read(n):return json.loads((out/n).read_text())
mesh=read('mesh-validation.json');opened=read('saved-blend-verification.json');placed=read('world-placement.json');verified=read('saved-world-verification.json')
assert opened['sha256']==hashlib.sha256((src/'Tide.blend').read_bytes()).hexdigest()
assert opened['direct_project_open_in_independent_process'] and mesh['all_parts_closed_positive_volume']
for name,row in mesh['files'].items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==row['sha256']
assert read('unreal-import.json')['source_fbx_sha256']==mesh['files']['SM_Blender_Tide.fbx']['sha256']
assert verified['reload_verified'] and len(verified['opening_collision'])==12
assert read('connection-verification.json')['connected_components']==1
assert all(p.read_bytes()[24]==8 for p in src.glob('*.png'))
b=(src/'SM_Blender_Tide.glb').read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert len(g['meshes'])==1 and len(g['meshes'][0]['primitives'])==1 and len(g['images'])==3
assert all(m['pbrMetallicRoughness'].get('metallicFactor',1)==0 for m in g['materials'])
probe=json.loads((root/'Docs/BlenderRebuild/ColorManagement/tide-atlas.json').read_text())[0]
assert probe['asset']=='Tide' and probe['source_sha256']==mesh['files']['Tide_BaseColor.png']['sha256']
assert probe['srgb'] and probe['source_bit_depth']==8
def linear(v):
    c=v/255
    return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
im=Image.open(src/'Tide_BaseColor.png').convert('RGB');errors=[];unique=set()
for sample in probe['samples']:
    rgb=im.getpixel(tuple(sample['source_pixel']));unique.add(rgb)
    errors.extend(abs(a-linear(v)) for a,v in zip(sample['linear_rgb'],rgb))
assert len(unique)==8 and max(errors)<.015
colors={'source_sha256':probe['source_sha256'],'samples':len(probe['samples']),'unique_source_colors':len(unique),'mean_linear_channel_error':sum(errors)/len(errors),'max_linear_channel_error':max(errors),'method':'Transient texture-sampling material rendered into RGBA32F, read without normalization and compared to decoded source PNG pixels. Production shaders are unchanged.','limits':'Sampling and compression check only; shaded appearance is not expected to match source pixels exactly.'}
(out/'color-verification.json').write_text(json.dumps(colors,indent=2))
audit_path=root/'Docs/BlenderRebuild/ColorManagement/atlas-bit-depth-audit.json'
audit=json.loads(audit_path.read_text())
audit['assets']=[r for r in audit['assets'] if r['asset']!='Tide']+[{'asset':'Tide','basecolor':'SourceAssets/Blender/Tide/Tide_BaseColor.png','bit_depth':8,'needs_shader_sampling_check':False}]
audit['assets'].sort(key=lambda r:r['asset'])
audit['additional_verified_png8_assets']=sorted(set(audit.get('additional_verified_png8_assets',[])+['Tide']))
audit['scope']='Current top-level Blender atlases; archived revisions excluded. Historical PNG16 corrections are listed separately from additional verified PNG8 assets.'
audit_path.write_text(json.dumps(audit,indent=2))
s=np.array(Image.open(root/'SourceAssets/Voxel/tide.png')).astype(int)
reference=~((s[:,:,0]>s[:,:,1]+60)&(s[:,:,2]>s[:,:,1]+60));render=np.array(Image.open(out/'front.png'))[:,:,3]>127
assert reference.shape==render.shape==(1254,1254)
silhouette={'intersection_over_union':float(np.sum(reference&render)/np.sum(reference|render)),'mismatched_pixels':int(np.sum(reference^render)),'render_sha256':hashlib.sha256((out/'front.png').read_bytes()).hexdigest(),'source_sha256':mesh['source_sha256'],'method':'Fixed 1254-square orthographic camera; source foreground excludes magenta, model mask uses alpha >127. No registration or scaling optimization.','limits':'Single-view projected outline and holes only, not block shape, shading, color or unseen rear.'}
(out/'silhouette-verification.json').write_text(json.dumps(silhouette,indent=2))
review={'revision':'r5_solid_wave_and_open_curl','parts':mesh['parts'],'triangles':mesh['triangles'],'studio_views':['front.png','rear.png'],'world_views':['World/unreal-viewport.png','Side/unreal-viewport.png','Context/unreal-viewport.png'],'visually_checked':True,'accepted_fidelity':False,'remaining':['Some rectangular front divisions and relief steps differ from the reference cubic rhythm.','The pale crest, curl interior and lower profile need closer shape matching.','Corners and highlights remain sharper and flatter than the concept; Unreal shade is darker.','Rear surfaces are inferred. No fluid simulation, rigid-body balance, character movement or performance validation.']}
(out/'visual-review.json').write_text(json.dumps(review,indent=2))
placed['status']='saved_reload_and_native_views_verified_fidelity_open';(out/'world-placement.json').write_text(json.dumps(placed,indent=2))
adapt=read('source-adaptation.json');adapt.update(status='imported_with_visual_refinement_open',revision=review['revision']);(out/'source-adaptation.json').write_text(json.dumps(adapt,indent=2))
cards=[('Original concept','../../../SourceAssets/Voxel/tide.png'),('Blender front','front.png'),('Blender rear - inferred surfaces','rear.png'),('Unreal front','World/unreal-viewport.png'),('Unreal side','Side/unreal-viewport.png'),('Unreal context','Context/unreal-viewport.png')]
body=''.join(f'<figure><figcaption>{html.escape(title)}</figcaption><a href="{p}"><img src="{p}" alt="{html.escape(title)}"></a></figure>' for title,p in cards)
text=f'Editable Blender wave with {mesh["parts"]} closed parts, {mesh["triangles"]:,} triangles and three packed PNG8 maps. Its curl is a real opening. The {placed["height_cm"]:.2f} cm model is seated on the left market counter. Saved-map reload, material bindings, four base samples and twelve opening/solid collision probes passed. Silhouette overlap is {silhouette["intersection_over_union"]:.1%}; this measures the outline only.'
(out/'comparison.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tide concept and Blender model</title><style>body{margin:32px;background:#121e25;color:#e2f1f4;font:16px/1.5 system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:18px}figure{margin:0;padding:12px;background:#213039}img{width:100%;height:450px;object-fit:contain}figcaption{margin-bottom:10px}p{max-width:1100px}</style><h1>Tide - fidelity review remains open</h1><p>'+text+'</p><main>'+body+'</main><p>'+html.escape(' '.join(review['remaining']))+'</p></html>',encoding='utf-8')
readme=root/'Docs/BlenderRebuild/README.md';text=readme.read_text(encoding='utf-8').replace('All 29 currently authored Blender outputs (22 source concepts and seven placement variants)','All 30 currently authored Blender outputs (23 source concepts and seven placement variants)')
start=text.find('\n## Tide\n')
suffix=''
if start!=-1:
    end=text.find('\n## ',start+10)
    if end!=-1:suffix=text[end:]
    text=text[:start]
text+=f'\n## Tide\n\n`tide.png` now has an editable Blender project containing {mesh["parts"]} closed solid blocks, {mesh["triangles"]:,} exported triangles and three packed PNG8 maps. The blue wave and stepped aqua highlight surround a physical opening, with inferred rear surfaces. It is an opaque stylized model, with no fluid simulation. `Tide/comparison.html` records the concept, studio front/rear and native Unreal views.\n\nThe {placed["height_cm"]:.3f} cm model is placed at ({placed["location_cm"][0]:.3f}, {placed["location_cm"][1]:.3f}, {placed["location_cm"][2]:.3f}) cm on the left market counter, scale {placed["scale"]}. Four low-cube center support probes and a 0.02 cm minimum base clearance passed after map reload. Three rays through the curl and three through solid blocks were tested with both simple and complex Unreal queries; all twelve gave the expected result. Complex mesh collision preserves the opening for this static prop. These are sampled checks, not full gameplay validation.\n\nThe saved Blender file reopened independently. GPU sampling covers all eight unique palette colors, with maximum linear channel error {max(errors):.5f}; shader bindings use the intended opaque, nonmetallic material. Fixed-camera silhouette overlap is {silhouette["intersection_over_union"]:.1%}, which excludes internal shape and shaded fidelity. Block divisions, pale crest proportions, relief depth, corner rounding and color under world lighting need further refinement. Fidelity remains unapproved.\n'
readme.write_text(text+suffix,encoding='utf-8')
print(json.dumps({'parts':mesh['parts'],'triangles':mesh['triangles'],'color_check':colors,'silhouette':silhouette,'accepted_fidelity':False},indent=2))
