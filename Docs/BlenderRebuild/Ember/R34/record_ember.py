"""Record Ember's physical-model checks without granting reference fidelity."""
import json,hashlib,struct,html
from pathlib import Path
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/Ember';src=root/'SourceAssets/Blender/Ember'
def read(n):return json.loads((out/n).read_text())
mesh=read('mesh-validation.json');opened=read('saved-blend-verification.json');placed=read('world-placement.json');verified=read('saved-world-verification.json')
assert opened['sha256']==hashlib.sha256((src/'Ember.blend').read_bytes()).hexdigest()
assert opened['direct_project_open_in_independent_process'] and mesh['all_parts_closed_positive_volume']
for name,row in mesh['files'].items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==row['sha256']
assert read('unreal-import.json')['source_fbx_sha256']==mesh['files']['SM_Blender_Ember.fbx']['sha256']
base=read('base-support-source.json')['samples'];base_count=len(base);probe_count=base_count*5
assert base_count>0 and verified['reload_verified'] and len(verified['counter_support'])==probe_count
connections=read('connection-verification.json')
assert connections['parts']==mesh['parts']
assert sorted(map(len,connections['groups']))==[1,1,1,1,mesh['parts']-4]
stacks=read('branch-stack-verification.json')['stacks']
assert len(stacks)==3 and all(r['xy_alignment_error_m']<.0001 and .002<r['vertical_overlap_m']<.006 for r in stacks)
assert all(p.read_bytes()[24]==8 for p in src.glob('*.png'))
b=(src/'SM_Blender_Ember.glb').read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert len(g['meshes'])==1 and len(g['meshes'][0]['primitives'])==1 and len(g['images'])==3
assert all(m['pbrMetallicRoughness'].get('metallicFactor',1)==0 for m in g['materials'])
probe=json.loads((root/'Docs/BlenderRebuild/ColorManagement/ember-atlas.json').read_text())[0]
assert probe['asset']=='Ember' and probe['source_sha256']==mesh['files']['Ember_BaseColor.png']['sha256']
assert probe['srgb'] and probe['source_bit_depth']==8
def linear(v):
    c=v/255
    return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
im=Image.open(src/'Ember_BaseColor.png').convert('RGB');errors=[];unique=set()
for sample in probe['samples']:
    rgb=im.getpixel(tuple(sample['source_pixel']));unique.add(rgb)
    errors.extend(abs(a-linear(v)) for a,v in zip(sample['linear_rgb'],rgb))
assert len(unique)==8 and max(errors)<.015
colors={'source_sha256':probe['source_sha256'],'samples':len(probe['samples']),'unique_source_colors':len(unique),'mean_linear_channel_error':sum(errors)/len(errors),'max_linear_channel_error':max(errors),'method':'Transient texture-sampling material rendered into RGBA32F, read without normalization and compared to decoded source PNG pixels. Production shaders are unchanged.','limits':'Sampling and compression check only; shaded appearance is not expected to match source pixels exactly.'}
(out/'color-verification.json').write_text(json.dumps(colors,indent=2))
audit_path=root/'Docs/BlenderRebuild/ColorManagement/atlas-bit-depth-audit.json'
audit=json.loads(audit_path.read_text())
audit['assets']=[r for r in audit['assets'] if r['asset']!='Ember']+[{'asset':'Ember','basecolor':'SourceAssets/Blender/Ember/Ember_BaseColor.png','bit_depth':8,'needs_shader_sampling_check':False}]
audit['assets'].sort(key=lambda r:r['asset'])
audit['additional_verified_png8_assets']=sorted(set(audit.get('additional_verified_png8_assets',[])+['Ember']))
audit['scope']='Current top-level Blender atlases; archived revisions excluded. Historical PNG16 corrections are listed separately from additional verified PNG8 assets.'
audit_path.write_text(json.dumps(audit,indent=2))

reference=np.array(Image.open(root/'SourceAssets/Voxel/ember.png')).astype(int)
mask=~((reference[:,:,0]>reference[:,:,1]+60)&(reference[:,:,2]>reference[:,:,1]+60))
measurements=[]
for revision,path in [('R4',out/'R4/front.png'),('R9',out/'R9/front.png'),('R10',out/'R10/front.png'),('R13',out/'R13/front.png'),('R19',out/'R19/front.png'),('R22',out/'R22/front.png'),('R29',out/'R29/front.png'),('R34',out/'front.png')]:
    render=np.array(Image.open(path))[:,:,3]>127
    assert mask.shape==render.shape==(1254,1254)
    measurements.append({'revision':revision,'intersection_over_union':float(np.sum(mask&render)/np.sum(mask|render)),'mismatched_pixels':int(np.sum(mask^render)),'render_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(out/'silhouette-verification.json').write_text(json.dumps({'source_sha256':mesh['source_sha256'],'measurements':measurements,'method':'Unregistered fixed 1254-square camera; magenta-excluded source versus render alpha >127.','limits':'Projected outline only; does not measure cube arrangement, physical depth, colors or fidelity.'},indent=2))
prior=json.loads((out/'R9/mesh-validation.json').read_text())
old_depth=prior['bounds_m']['max'][1]-prior['bounds_m']['min'][1]
new_depth=mesh['bounds_m']['max'][1]-mesh['bounds_m']['min'][1]
base=read('base-support-source.json')['samples']
assert max(r['bottom_m'] for r in base)-min(r['bottom_m'] for r in base)<1e-6
assert {r['part'] for r in verified['counter_support']}=={r['part'] for r in base}
shape={'previous_depth_m':old_depth,'current_depth_m':new_depth,'depth_ratio':new_depth/old_depth,'flat_base_parts':base_count,'counter_contact_samples':probe_count,'ground_elevation_range_m':[min(r['bottom_m'] for r in base),max(r['bottom_m'] for r in base)],'method':'Evaluated exported mesh extents; every floor-course cube underside and five native counter traces per cube after saved-map reload.','limits':'Physical volume and sampled contact only; no reference fidelity or balance certification.'}
r10=read('R10/mesh-validation.json')
shape.update(outer_bounds_unchanged_from_r10=mesh['bounds_m']==r10['bounds_m'],previous_bounds_m=r10['bounds_m'],current_bounds_m=mesh['bounds_m'],added_interior_cells=len(read('bulk-interior.json')['cells']))
(out/'volume-and-base-verification.json').write_text(json.dumps(shape,indent=2))
remaining=[
    'Ten cream cubes now form the measured cluster and central pair, but their spacing, lower recesses and neighboring yellow arrangement still differ from the concept.',
    'The cream cluster is recessed into the body and the large R19 side opening is reduced, but some lower blocks still project farther than the source arrangement suggests.',
    'The upper orange columns and yellow stack are closer to the concept, but individual widths, middle transitions and protrusion still need refinement. Some source faces remain interpreted as separate blocks.',
    'Side views expose small dark recesses beneath the middle columns and cream cluster. The rear terraces remain inferred and visually repetitive.',
    'Orange side tongues, yellow transitions, individual widths, bevels and shaded colors still need closer matching.',
    'Rear structure and interior pigments are inferred from one view; a few small junctions remain visible.',
    'World shade is darker than the concept. Palette sampling is verified separately from appearance.',
    'The shared floor and sampled counter contact are verified, but no rigid-body stability, particle simulation, full collision or gameplay validation has been performed.'
]
review={'revision':'r34_outer_branch_stacks','parts':mesh['parts'],'triangles':mesh['triangles'],'studio_views':['front.png','rear.png','side.png','left.png'],'world_views':['World/unreal-viewport.png','Side/unreal-viewport.png','Context/unreal-viewport.png'],'visually_checked':True,'accepted_fidelity':False,'remaining':remaining}
(out/'visual-review.json').write_text(json.dumps(review,indent=2))
placed['status']='saved_reload_and_native_views_verified_fidelity_open';(out/'world-placement.json').write_text(json.dumps(placed,indent=2))
adapt=read('source-adaptation.json');adapt.update(status='imported_with_visual_refinement_open',revision=review['revision']);(out/'source-adaptation.json').write_text(json.dumps(adapt,indent=2))
cards=[('Original concept','../../../SourceAssets/Voxel/ember.png'),('Earlier R29 front','R29/front.png'),('Earlier R29 side','R29/Side/unreal-viewport.png'),('Current Blender front','front.png'),('Current Blender right','side.png'),('Current Blender left','left.png'),('Current rear - inferred','rear.png'),('Unreal front','World/unreal-viewport.png'),('Unreal side','Side/unreal-viewport.png'),('Unreal context','Context/unreal-viewport.png')]
body=''.join(f'<figure><figcaption>{html.escape(title)}</figcaption><a href="{p}"><img src="{p}" alt="{html.escape(title)}"></a></figure>' for title,p in cards)
detail=f'{mesh["parts"]} editable closed parts; {mesh["triangles"]:,} exported triangles; three packed PNG8 maps. One connected flame body and four separate reference sparks. Model depth is {new_depth/old_depth:.2f} times the earlier thin version. The two outer branches now use aligned full cube stacks in place of offset overlapping face entries. Three measured two-cube joints share an XY column with approximately 4 mm of overlap. Inferred fill below orange-authored cubes stays within the orange palette, removing unrelated yellow patches on those columns. Inferred fill is screened against the cream cluster and selected visible cubes. All {base_count} floor cubes share the same underside; {probe_count} center/inset-corner counter traces passed after map reload. The saved Blender file reopened independently. Height {placed["height_cm"]:.2f} cm, counter position x={placed["location_cm"][0]:.2f}, y={placed["location_cm"][1]:.2f}. These checks establish usable source and import, not a faithful or finished model.'
(out/'comparison.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ember source and model review</title><style>body{margin:32px;background:#201914;color:#fff0df;font:16px/1.5 system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:18px}figure{margin:0;padding:12px;background:#32251e}img{width:100%;height:450px;object-fit:contain}figcaption{margin-bottom:10px}p{max-width:1100px}</style><h1>Ember - fidelity remains open</h1><p>'+detail+'</p><main>'+body+'</main><ul>'+''.join('<li>'+html.escape(t)+'</li>' for t in remaining)+'</ul></html>',encoding='utf-8')
readme=root/'Docs/BlenderRebuild/README.md';text=readme.read_text(encoding='utf-8').replace('All 30 currently authored Blender outputs (23 source concepts and seven placement variants)','All 31 currently authored Blender outputs (24 source concepts and seven placement variants)')
start=text.find('\n## Ember\n');suffix=''
if start!=-1:
    end=text.find('\n## ',start+10)
    if end!=-1:suffix=text[end:]
    text=text[:start]
text+='\n## Ember\n\n'+detail+' See `Ember/comparison.html` for the source, R29 comparison, current studio views and native Unreal captures.\n\n'+' '.join(remaining)+'\n'
readme.write_text(text+suffix,encoding='utf-8')
print(json.dumps({'parts':mesh['parts'],'triangles':mesh['triangles'],'color_check':colors,'outline_measurements':measurements,'accepted_fidelity':False},indent=2))
