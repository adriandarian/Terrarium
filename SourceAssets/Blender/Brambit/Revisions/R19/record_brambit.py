"""Bind Brambit's source, exports, captures and tested limits into one review."""
import json,hashlib,html,ast,struct,io
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/Brambit';src=root/'SourceAssets/Blender/Brambit'
def read(name):return json.loads((out/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
mesh=read('mesh-validation.json');saved=read('saved-blend-verification.json');source=read('source-validation.json');world=read('saved-world-verification.json');placement=read('world-placement.json')
assert sha(src/'Brambit.blend')==saved['sha256']==source['source_blend_sha256']==world['source_blend_sha256']
assert saved['direct_project_open_in_independent_process'] and mesh['all_parts_closed_positive_volume']
assert source['construction_blocks']==185 and len(source['union_volumes'])==5 and source['foot_samples']==20
assert list(map(len,read('connection-verification.json')['components']))==[5]
shoots=read('shoot-topology-verification.json');assert shoots['source_blend_sha256']==saved['sha256'] and len(shoots['shoots'])==3
assert all(row['evaluated_connected_components']==1 and row['closed_positive_volume'] for row in shoots['shoots'])
for filename,row in mesh['files'].items():assert sha(src/filename)==row['sha256']
assert world['reload_verified'] and world['material_verified'] and len(world['foot_samples'])==20 and all(row['passed'] for row in world['foot_samples'])
assert sha(src/'SM_Blender_Brambit.fbx')==world['source_fbx_sha256']==read('unreal-import.json')['source_fbx_sha256']
assert all(p.read_bytes()[24]==8 for p in src.glob('*.png'))
uv_report=read('surface-uv-verification.json');assert uv_report['source_blend_sha256']==saved['sha256'] and len(uv_report['parts'])==5
assert all(row['faces_with_texture_area']==row['surface_faces'] for row in uv_report['parts'])
landmarks=read('foot-landmark-verification.json');assert landmarks['source_blend_sha256']==saved['sha256'] and len(landmarks['landmarks'])==3
assert all(row['error_pixels']<2 for row in landmarks['landmarks'])
burrs=read('front-burr-verification.json');assert burrs['source_blend_sha256']==saved['sha256']
assert len(burrs['burrs'])==4 and all(row['error_pixels']<.01 for row in burrs['burrs'])
assert len(burrs['connected_sections'])==5 and all(row['connected_components']==1 for row in burrs['connected_sections'])
crown=read('front-crown-verification.json');assert crown['source_blend_sha256']==saved['sha256']
assert len(crown['courses'])==5 and all(row['error_pixels']<.01 for row in crown['courses'])
bark=read('bark-envelope-verification.json');assert bark['source_blend_sha256']==saved['sha256']
assert len(bark['patches'])==44 and bark['samples']>0 and bark['maximum_relief_m']<.003002
face_depth=read('face-depth-verification.json');assert face_depth['source_blend_sha256']==saved['sha256']
assert len(face_depth['construction_planes'])==22 and len(face_depth['evaluated_surface_samples'])==19 and face_depth['maximum_sampled_offset_m']<.001302
texture_rows=[]
for kind in ['BaseColor','Roughness']:
    path=src/f'Brambit_{kind}.png';pixels=np.array(Image.open(path).convert('RGB'))[::-1];assert pixels.shape==(1024,1024,3)
    counts=[]
    for index in range(16):
        cell=pixels[index//8*128:(index//8+1)*128,index%8*128:(index%8+1)*128]
        counts.append(len(np.unique(cell.reshape(-1,3),axis=0)))
    assert all(count>=8 for index,count in enumerate(counts) if kind!='BaseColor' or index!=7)
    if kind=='BaseColor':
        # The dark pigment has only 2% variation. PNG8 quantization legitimately
        # merges shades; verify its small nonzero range instead of demanding
        # the brighter cells' number of distinct encoded colors.
        dark=pixels[:128,7*128:8*128].reshape(-1,3).astype(int)
        assert counts[7]>=2 and 0<np.max(np.ptp(dark,axis=0))<=4
        assert np.max(np.abs(np.mean(dark,axis=0)-np.array([61,56,39])))<2
    texture_rows.append({'map':kind,'sha256':sha(path),'size':[1024,1024],'unique_colors_per_pigment_cell':counts})
(out/'surface-texture-verification.json').write_text(json.dumps({'source_blend_sha256':saved['sha256'],'maps':texture_rows,'limits':'Stored pixel variation and source UV coverage. Does not establish visual fidelity.'},indent=2))
paint=read('authored-pigment-regions.json');assert paint['atlas_size']==[1024,1024] and len(paint['regions'])==9
pixels=np.array(Image.open(src/'Brambit_BaseColor.png').convert('RGB'))[::-1]
lo=mesh['bounds_m']['min'];hi=mesh['bounds_m']['max'];paint_samples=[]
for region in paint['regions']:
    xmin,xmax,zmin,zmax=region['world_xz_bounds_m'];cell=region['palette_cell']
    u,v=region['center_uv']
    assert region['dedicated_painted_texels']>region['painted_texels']
    actual=pixels[int(v*1024),int(u*1024)].astype(int)
    expected=np.array([int(region['pigment_srgb_hex'][i:i+2],16) for i in (0,2,4)])
    error=int(np.max(np.abs(actual-expected)))
    assert error<=7,(region['region'],actual,expected)
    paint_samples.append({'region':region['region'],'encoded_rgb':actual.tolist(),'max_channel_error':error})
(out/'authored-pigment-verification.json').write_text(json.dumps({'source_blend_sha256':saved['sha256'],'base_color_sha256':sha(src/'Brambit_BaseColor.png'),'samples':paint_samples,'limits':'Nine stored region-center samples after color-managed PNG export; does not establish overall concept fidelity.'},indent=2))
data=(src/'SM_Blender_Brambit.glb').read_bytes();size=struct.unpack_from('<I',data,12)[0];glb=json.loads(data[20:20+size])
assert len(glb['meshes'])==1 and len(glb['meshes'][0]['primitives'])==1 and len(glb['images'])==3
assert all(m['pbrMetallicRoughness'].get('metallicFactor',1)==0 for m in glb['materials'])
atlas=read('face-atlas-verification.json');layout=read('face-atlas-layout.json')
assert atlas['source_blend_sha256']==saved['sha256'] and atlas['layout_sha256']==sha(out/'face-atlas-layout.json')
assert atlas['uv_loops_checked']>0 and atlas['maximum_uv_error']<1e-6
blob=data[28+size:];embedded=[]
for entry in glb['images']:
    view=glb['bufferViews'][entry['bufferView']];offset=view.get('byteOffset',0)
    raw=blob[offset:offset+view['byteLength']]
    actual=np.array(Image.open(io.BytesIO(raw)).convert('RGB'))
    source_pixels=np.array(Image.open(src/(entry['name']+'.png')).convert('RGB'))
    if entry['name'].endswith('Roughness'):
        # glTF packs roughness in green; red and blue serve other channels.
        assert np.array_equal(actual[:,:,1],source_pixels[:,:,1])
    else:assert np.array_equal(actual,source_pixels)
    embedded.append({'image':entry['name'],'pixel_content_matches_source':True})
accessor=glb['accessors'][glb['meshes'][0]['primitives'][0]['attributes']['TEXCOORD_0']]
view=glb['bufferViews'][accessor['bufferView']]
assert accessor['componentType']==5126 and accessor['type']=='VEC2'
uvs=np.ndarray((accessor['count'],2),dtype='<f4',buffer=blob,offset=view.get('byteOffset',0)+accessor.get('byteOffset',0),strides=(view.get('byteStride',8),4)).copy()
uvs[:,1]=1-uvs[:,1] # glTF's image-coordinate origin is opposite Blender's.
export_regions=[]
for pigment,m in layout['regions'].items():
    lower=np.array(m['uv_min'])-1e-6;upper=np.array(m['uv_max'])+1e-6
    count=int(np.sum(np.all((uvs>=lower)&(uvs<=upper),axis=1)))
    assert count>0
    export_regions.append({'pigment':int(pigment),'exported_vertices_in_region':count})
(out/'face-atlas-export-verification.json').write_text(json.dumps({'source_blend_sha256':saved['sha256'],'glb_sha256':sha(src/'SM_Blender_Brambit.glb'),'embedded_images':embedded,'uv_regions':export_regions,'limits':'Saved source UV coverage, exported atlas presence and embedded image pixels. Does not establish overall visual fidelity.'},indent=2))
reference=np.array(Image.open(root/'SourceAssets/Voxel/brambit.png')).astype(int)
mask=~((reference[:,:,0]>reference[:,:,1]+60)&(reference[:,:,2]>reference[:,:,1]+60))
render=np.array(Image.open(out/'front.png'))[:,:,3]>127;assert mask.shape==render.shape==(1254,1254)
(out/'silhouette-verification.json').write_text(json.dumps({'source_sha256':mesh['source_sha256'],'render_sha256':sha(out/'front.png'),'intersection_over_union':float(np.sum(mask&render)/np.sum(mask|render)),'mismatched_pixels':int(np.sum(mask^render)),'method':'Fixed reference camera, no image registration or optimization; source chroma foreground versus rendered alpha.','limits':'Projected outline only. Does not measure internal block layout, colors, face expression, depth or unseen anatomy.'},indent=2))
previous_path=out/'R18/front.png';previous=np.array(Image.open(previous_path))[:,:,3]>127
assert previous.shape==mask.shape
def span(image,y):
    xs=np.flatnonzero(image[y]);return [int(xs[0]),int(xs[-1])] if len(xs) else None
contour={'source_sha256':sha(root/'SourceAssets/Voxel/brambit.png'),'source_blend_sha256':saved['sha256'],'previous_render_sha256':sha(previous_path),'render_sha256':sha(out/'front.png'),'previous_revision':'r18_flush_face_courses','revision':'r19_dedicated_face_atlas','previous_outline_iou':float(np.sum(mask&previous)/np.sum(mask|previous)),'current_outline_iou':float(np.sum(mask&render)/np.sum(mask|render)),'sampled_rows':[{'y':y,'concept_span':span(mask,y),'previous_span':span(previous,y),'current_span':span(render,y)} for y in range(660,881,20)],'method':'Same fixed 1254-pixel reference camera; magenta chroma foreground versus rendered alpha above 127. No image registration.','limits':'Outline overlap and row extents only, not a fidelity score. Does not evaluate colors, internal block layout, depth or unseen anatomy.'}
(out/'body-contour-verification.json').write_text(json.dumps(contour,indent=2))
remaining=[
 'The cap still spreads too broadly and has a flatter arrangement than the concept. Crown overhangs, course heights, the brown saddle and stem exposure need closer matching.',
 'The forehead, surrounding front bark and belly now sit close to the tan face plane. The front body core is 2 mm behind the tan face, closing the deep backing recess. Sampled face-course offsets are 1-1.3 mm. Fine seams remain, and the block divisions and facial pigment boundaries still differ from the source.',
 'The face and belly now use dedicated atlas regions, and their pigment boundaries are sharper in Blender and Unreal. The color blocks are still too regular and differ from the concept in placement and contrast. The Unreal face remains darker than the studio reference.',
 'The body outline is closer after narrowing the middle rear section and adjusting two bark protrusions. Side and rear anatomy, bark pattern and coloration still differ from the concept. The rear is inferred from a single front view.',
 'The leafy shoots retain a more regular surface pattern and different colors than the concept. Leaf seams, exposed stems and the unseen rear arrangement remain unresolved.',
 'The model has four statically supported feet with twenty tested sole samples. It has no rig, animation, locomotion or physics validation. No perfect-fidelity approval is claimed.'
]
revision='r19_dedicated_face_atlas'
review={'revision':revision,'accepted_fidelity':False,'visually_checked':True,'parts':5,'editable_construction_blocks':185,'triangles':mesh['triangles'],'studio_views':['front.png','left.png','side.png','rear.png'],'world_views':['World/unreal-viewport.png','Side/unreal-viewport.png','Rear/unreal-viewport.png','Context/unreal-viewport.png'],'remaining':remaining}
(out/'visual-review.json').write_text(json.dumps(review,indent=2))
adapt=read('source-adaptation.json');adapt.update(revision=revision,status='imported_with_visual_refinement_open')
for node in ast.walk(ast.parse((root/'Scripts/BlenderRebuild/brambit.py').read_text())):
    if isinstance(node,ast.Dict):
        values={k.value:v for k,v in zip(node.keys,node.values) if isinstance(k,ast.Constant)}
        if 'revision' in values and isinstance(values.get('method'),ast.Constant):adapt['method']=values['method'].value
(out/'source-adaptation.json').write_text(json.dumps(adapt,indent=2))
placement['status']='saved_reload_and_native_views_verified_fidelity_open';(out/'world-placement.json').write_text(json.dumps(placement,indent=2))
detail=f'Brambit is a physical Blender model with a stepped bark body, tan face, four feet, an asymmetric moss crown and three leafy shoots. This revision gives the face and belly dedicated texture regions within the existing 1024-pixel atlas. Each region has 472 by 712 pixels inside its gutters. The face has about 6.8 times the horizontal and 16.8 times the vertical texel density of the previous mapping. The nine authored pigment regions are rasterized directly at that density, producing sharper boundaries in the checked Blender and Unreal views. The forehead is now 1.3 mm ahead of the tan face instead of 15 mm; the other front courses and belly are 1 mm ahead. The body core is 2 mm behind the face. These changes reduce the dark seams seen in R17 while retaining the projecting nose and bark knots. Nineteen evaluated surface samples and all 22 authored front planes pass the depth check. The model retains five connected closed volumes, 185 hidden editable construction parts, {mesh["triangles"]:,} exported triangles, one opaque nonmetallic material and three packed 1024-pixel PNG8 maps. The Blender project reopened independently, all source faces have UV area, and the current FBX and material bindings passed Unreal map reload verification. Twenty imported sole samples across four feet pass static support checks, with maximum uneven-ground clearance of {world["max_clearance_cm"]*10:.2f} mm. Brambit is saved in HomesteadBlender at {placement["height_cm"]:.2f} cm tall. Four studio angles and four native Unreal views were inspected. Crown shape, facial pigment placement and contrast, bark divisions and leaf details remain unfinished. The comparison is evidence of progress, not a claim of perfect fidelity.'

for name,path in [('face-concept.png',root/'SourceAssets/Voxel/brambit.png'),('face-r18.png',out/'R18/front.png'),('face-current.png',out/'front.png')]:
    Image.open(path).crop((480,520,930,1025)).save(out/name)
cards=[('Concept face close-up','face-concept.png'),('Previous R18 face close-up','face-r18.png'),('Current face close-up','face-current.png'),('Original concept','../../../SourceAssets/Voxel/brambit.png'),('Previous R18 reference view','R18/front.png'),('Previous R18 rear left','R18/left.png'),('Blender reference view','front.png'),('Blender opposite front','side.png'),('Blender rear left','left.png'),('Blender rear','rear.png'),('Unreal front','World/unreal-viewport.png'),('Unreal side','Side/unreal-viewport.png'),('Unreal rear','Rear/unreal-viewport.png'),('Unreal courtyard context','Context/unreal-viewport.png')]
for _,path in cards:assert (out/path).resolve().is_file()
figures=''.join(f'<figure><figcaption>{html.escape(title)}</figcaption><a href="{path}"><img src="{path}" alt="{html.escape(title)}"></a></figure>' for title,path in cards)
(out/'comparison.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Brambit concept and Blender model</title><style>body{margin:32px;background:#23251c;color:#f5ebd1;font:16px/1.5 system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:18px}figure{margin:0;padding:12px;background:#343b28}img{width:100%;height:450px;object-fit:contain}p{max-width:1100px}a{color:inherit}</style><h1>Brambit - fidelity remains open</h1><p>'+detail+'</p><main>'+figures+'</main><ul>'+''.join('<li>'+html.escape(item)+'</li>' for item in remaining)+'</ul></html>',encoding='utf-8')
readme=root/'Docs/BlenderRebuild/README.md';text=readme.read_text(encoding='utf-8')
text=text.replace('All 32 currently authored Blender outputs (25 source concepts and seven placement variants)','All 33 currently authored Blender outputs (26 source concepts and seven placement variants)')
start=text.find('\n## Brambit\n')
if start!=-1:
    end=text.find('\n## ',start+12);text=text[:start]+(text[end:] if end!=-1 else '')
readme.write_text(text+'\n## Brambit\n\n'+detail+' See `Brambit/comparison.html` for the source, studio views and native Unreal captures.\n\n'+' '.join(remaining)+'\n',encoding='utf-8')
print(json.dumps({'asset':'Brambit','volumes':5,'editable_blocks':185,'triangles':mesh['triangles'],'foot_samples':20,'accepted_fidelity':False}))
