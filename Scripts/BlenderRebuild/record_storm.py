"""Record the first Blender Storm source and its actual validation limits."""
import json,hashlib,html
from pathlib import Path
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/Storm';src=root/'SourceAssets/Blender/Storm'
def read(name):return json.loads((out/name).read_text())
mesh=read('mesh-validation.json');saved=read('saved-blend-verification.json');verified=read('saved-world-verification.json');placed=read('world-placement.json')
assert saved['sha256']==hashlib.sha256((src/'Storm.blend').read_bytes()).hexdigest()
assert saved['direct_project_open_in_independent_process'] and mesh['all_parts_closed_positive_volume']
assert mesh['parts']==53 and mesh['material_slots']==2 and saved['packed_images']==3
connections=read('connection-verification.json')
assert connections['source_blend_sha256']==saved['sha256']
assert connections['body_parts']==43 and connections['detached_sparks']==10
assert sorted(map(len,connections['components']))==[1]*10+[43]
projection=read('reference-projection-verification.json')
assert projection['source_blend_sha256']==saved['sha256']
core=read('core-volume-verification.json')
assert core['source_blend_sha256']==saved['sha256'] and core['evaluated_closed'] and core['evaluated_volume_m3']>0
assert len(projection['cube_anchors'])==42 and projection['cream_hexahedra']==2 and projection['gold_hexahedra']==1
assert len(projection['gold_column_corners'])==7 and max(p['max_error_px'] for p in projection['gold_column_corners'])<.001
uv=read('palette-uv-verification.json')
assert uv['source_blend_sha256']==saved['sha256'] and len(uv['parts'])==53 and uv['outside_palette_cell']==0
assert abs(projection['camera_elevation_deg']-30)<.0001
for name,row in mesh['files'].items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==row['sha256']
assert read('unreal-import.json')['source_fbx_sha256']==mesh['files']['SM_Blender_Storm.fbx']['sha256']
assert verified['reload_verified'] and len(verified['counter_support'])==3 and all(p['passed'] for p in verified['counter_support'])
clearance=read('post-clearance-verification.json')['samples'];assert len(clearance)==12 and min(p['bounding_box_clearance_cm'] for p in clearance)>.1
assert all(p.read_bytes()[24]==8 for p in src.glob('*.png'))
probe=json.loads((root/'Docs/BlenderRebuild/ColorManagement/storm-atlas.json').read_text())[0]
assert probe['asset']=='Storm' and probe['source_sha256']==mesh['files']['Storm_BaseColor.png']['sha256'] and probe['srgb']
image=Image.open(src/'Storm_BaseColor.png').convert('RGB');errors=[];colors=set()
def linear(v):
    v=v/255
    return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for sample in probe['samples']:
    rgb=image.getpixel(tuple(sample['source_pixel']));colors.add(rgb)
    errors.extend(abs(actual-linear(value)) for actual,value in zip(sample['linear_rgb'],rgb))
assert len(colors)==8 and max(errors)<.015
(out/'color-verification.json').write_text(json.dumps({'unique_colors':len(colors),'samples':len(probe['samples']),'mean_linear_channel_error':sum(errors)/len(errors),'max_linear_channel_error':max(errors),'source_sha256':probe['source_sha256'],'method':'RGBA32F native texture-sampling readback compared with linearized PNG8 source pixels.','limits':'Color sampling only; shaded appearance remains a separate visual review.'},indent=2))
ref=np.array(Image.open(root/'SourceAssets/Voxel/storm.png')).astype(int)
mask=~((ref[:,:,0]>ref[:,:,1]+60)&(ref[:,:,2]>ref[:,:,1]+60));render=np.array(Image.open(out/'front.png'))[:,:,3]>127
assert mask.shape==render.shape
(out/'silhouette-verification.json').write_text(json.dumps({'intersection_over_union':float(np.sum(mask&render)/np.sum(mask|render)),'mismatched_pixels':int(np.sum(mask^render)),'render_sha256':hashlib.sha256((out/'front.png').read_bytes()).hexdigest(),'limits':'Projected outline only. This does not measure internal features or prove fidelity.'},indent=2))
old=np.array(Image.open(out/'R18/front.png'))[:,:,3]>127
region=(slice(940,1130),slice(430,650))
tip={'region_xyxy':[430,940,650,1130],'source_sha256':mesh['source_sha256'],'limits':'Fixed lower-tip crop, same reference camera. Binary outline overlap only; not surface, depth or overall fidelity approval.'}
prior=np.array(Image.open(out/'R20/front.png'))[:,:,3]>127
for revision,arr,path in [('R18',old,out/'R18/front.png'),('R20',prior,out/'R20/front.png'),('R21',np.array(Image.open(out/'R21/front.png'))[:,:,3]>127,out/'R21/front.png'),('R28',np.array(Image.open(out/'R28/front.png'))[:,:,3]>127,out/'R28/front.png'),('R32',render,out/'front.png')]:
    ref_tip=mask[region];candidate=arr[region]
    tip[revision]={'intersection_over_union':float(np.sum(ref_tip&candidate)/np.sum(ref_tip|candidate)),'mismatched_pixels':int(np.sum(ref_tip^candidate)),'render_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(out/'tip-comparison.json').write_text(json.dumps(tip,indent=2))
comparison={'previous_revision':'R28','current_revision':'R32','source_blend_sha256':saved['sha256'],'source_concept_sha256':mesh['source_sha256'],'limits':'Binary foreground outline only. Internal surfaces, shading and physical depth need visual inspection.'}
for rev,path in [('R21',out/'R21/front.png'),('R28',out/'R28/front.png'),('R32',out/'front.png')]:
    arr=np.array(Image.open(path))[:,:,3]>127
    comparison[rev]={'intersection_over_union':float(np.sum(mask&arr)/np.sum(mask|arr)),'mismatched_pixels':int(np.sum(mask^arr)),'render_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
comparison['changed_alpha_mask_pixels_since_R28']=int(np.sum((np.array(Image.open(out/'R28/front.png'))[:,:,3]>127)^render))
(out/'front-outline-comparison.json').write_text(json.dumps(comparison,indent=2))
remaining=[
 'The broad upper gold column replaces two narrow overlapping ribs; the adjoining blocks connect in depth and the central shoulder no longer protrudes through its visible face. The cream crest steps and gold course proportions still differ from the concept.',
 'The 43 non-spark solids now form one connected group with positive interior overlap witnesses. They remain editable overlapping meshes, not a Boolean-unioned manifold.',
 'Cloud cluster sizes, spacing and partial overlaps still differ from the source.',
 'The gold edge has four measured sections, but the upper cap has an exaggerated triangular crease and some middle facets shade too dark. Section seams and narrow side gaps still need refinement.',
 'The cream now has raised blocks, a broad crossbar and lower facets. Block depths and seam transitions still differ from the source. Shorter cream backs reduce the exposed lower rear patches, but a narrow edge of the tip remains visible from the rear.',
 'The flat gold rear cap has been replaced with a continuous raised ridge and angular surfaces. This unseen back is inferred from the front spine; its facet layout and transitions still need visual refinement.',
 'Ten sparks follow the concept arrangement, with small remaining position and size differences.',
 'Static tip contact and sampled post clearance passed; rigid-body balance, animation, gameplay and full collision have not been tested.'
]
review={'revision':'r32_broad_upper_gold_column','accepted_fidelity':False,'visually_checked':True,'parts':mesh['parts'],'triangles':mesh['triangles'],'connected_body_parts':43,'detached_source_sparks':10,'studio_views':['front.png','side.png','left.png','rear.png'],'world_views':['World/unreal-viewport.png','Side/unreal-viewport.png','Context/unreal-viewport.png'],'remaining':remaining}
(out/'visual-review.json').write_text(json.dumps(review,indent=2))
adapt=read('source-adaptation.json');adapt.update(revision=review['revision'],status='imported_with_visual_refinement_open');(out/'source-adaptation.json').write_text(json.dumps(adapt,indent=2))
placed['status']='saved_reload_and_native_views_verified_fidelity_open';(out/'world-placement.json').write_text(json.dumps(placed,indent=2))
cards=[('Original concept','../../../SourceAssets/Voxel/storm.png'),('Blender front','front.png'),('Blender right','side.png'),('Blender left','left.png'),('Previous R28 front','R28/front.png'),('Previous R28 rear','R28/rear.png'),('Blender rear - inferred','rear.png'),('Unreal front','World/unreal-viewport.png'),('Unreal side','Side/unreal-viewport.png'),('Unreal context','Context/unreal-viewport.png')]
detail=f'Storm R32 has {mesh["parts"]} editable closed parts and {mesh["triangles"]:,} exported triangles. A broad eight-corner gold column replaces two narrow crest boxes. Its seven visible control corners follow measured concept coordinates. The neighboring gold and cloud cluster now joins it in depth. The hidden central shoulder was narrowed to stop it protruding through the visible column. This revision retains the four rebuilt gold edge sections and their closed, tapered backs from R28. All {uv["evaluated_loops"]:,} evaluated UV corners stay inside their assigned uniform palette cells. Its 43 body solids form one connected group with {len(connections["edges"])} verified interior overlap witnesses; ten source sparks remain separate. Three packed PNG8 maps feed two opaque nonmetallic material roles. The normal Blender file reopened independently. The {placed["height_cm"]:.2f} cm display is saved beside Grove; three tip-contact samples and twelve post-face clearance samples passed after reload. The inferred rear, cream transitions, gold facet shading and cloud proportions still need refinement. Concept fidelity remains unaccepted.'

body=''.join(f'<figure><figcaption>{html.escape(title)}</figcaption><a href="{path}"><img src="{path}" alt="{html.escape(title)}"></a></figure>' for title,path in cards)
(out/'comparison.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Storm concept and Blender model</title><style>body{margin:32px;background:#24221b;color:#fff4d1;font:16px/1.5 system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:18px}figure{margin:0;padding:12px;background:#343126}img{width:100%;height:450px;object-fit:contain}p{max-width:1100px}</style><h1>Storm - fidelity remains open</h1><p>'+detail+'</p><main>'+body+'</main><ul>'+''.join('<li>'+html.escape(r)+'</li>' for r in remaining)+'</ul></html>',encoding='utf-8')
readme=root/'Docs/BlenderRebuild/README.md';text=readme.read_text(encoding='utf-8').replace('All 31 currently authored Blender outputs (24 source concepts and seven placement variants)','All 32 currently authored Blender outputs (25 source concepts and seven placement variants)')
start=text.find('\n## Storm\n')
if start!=-1:
    end=text.find('\n## ',start+10);text=text[:start]+(text[end:] if end!=-1 else '')
readme.write_text(text+'\n## Storm\n\n'+detail+' See `Storm/comparison.html` for the original, studio views and native Unreal captures.\n\n'+' '.join(remaining)+'\n',encoding='utf-8')
print(json.dumps({'asset':'Storm','parts':mesh['parts'],'triangles':mesh['triangles'],'tip_probes':3,'post_probes':12,'accepted_fidelity':False}))
