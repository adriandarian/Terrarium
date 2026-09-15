"""Record current Grove geometry, sampled GPU colors, and inspected limitations."""
import ast,json,hashlib,struct,html
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/Grove';src=root/'SourceAssets/Blender/Grove'
def read(name):return json.loads((out/name).read_text())
mesh=read('mesh-validation.json');opened=read('saved-blend-verification.json');placement=read('world-placement.json')
assert opened['sha256']==hashlib.sha256((src/'Grove.blend').read_bytes()).hexdigest()
for name,r in mesh['files'].items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==r['sha256']
assert read('saved-world-verification.json')['reload_verified']
assert read('connection-verification.json')['connected_components']==1
for p in src.glob('*.png'):
    assert p.read_bytes()[24]==8
    assert mesh['files'][p.name]['sha256']==json.loads((out/'R7/mesh-validation.json').read_text())['files'][p.name]['sha256'], 'Prior GPU sampling evidence requires unchanged texture bytes'
b=(src/'SM_Blender_Grove.glb').read_bytes();size=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+size])
assert len(g['meshes'])==1 and len(g['meshes'][0]['primitives'])==3 and len(g['images'])==3
assert all(m['pbrMetallicRoughness'].get('metallicFactor',1)==0 for m in g['materials'])
tree=ast.parse((root/'Scripts/BlenderRebuild/grove.py').read_text())
palette=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='P' for t in n.targets))
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
rows=[]
for sample in read('gpu-texture-8bit-probe.json'):
    hx=palette[sample['palette_index']][0];expected=[linear(int(hx[j:j+2],16)/255) for j in [0,2,4]]
    error=max(abs(a-b) for a,b in zip(sample['linear_rgb'],expected))
    assert error<.02,(sample,expected,error)
    rows.append(dict(sample,expected_linear_rgb=expected,max_channel_error=error))
(out/'color-verification.json').write_text(json.dumps({'source_basecolor_sha256':mesh['files']['Grove_BaseColor.png']['sha256'],'png_bit_depth':8,'samples':rows,'method':'Material albedo routed to emission and drawn into an RGBA32F target, then read without normalization; a constant-color control verified the linear readback. Original opaque material restored and saved afterward.','finding':'The previous PNG16 import sampled approximately encoded RGB despite srgb=true. This PNG8 import samples decoded linear RGB within 0.02 per channel at the eight checked palette cells.','limits':'Texture sampling check only; no claim that all 16-bit textures are affected or that the shaded scene matches the concept.'},indent=2))
review={'revision':'r13_leaf_volume_and_seated_turf','parts':mesh['parts'],'triangles':mesh['triangles'],'studio_views':['front.png','rear.png'],'world_views':['World/unreal-viewport.png','Side/unreal-viewport.png','Context/unreal-viewport.png'],'visually_checked':True,'accepted_fidelity':False,'remaining':['Leaf front divisions, corner rounding and shade still differ from the concept; rear colors are inferred.','Some turf joints remain too recessed; soil block depths and underside profile still need refinement.','Unreal shade is darker and less yellow than the studio source.','Rear structure is inferred from one view; full collision, gameplay and performance remain untested.'],'changes':['Replaced the concentric grid base with individually modeled soil and turf courses, hanging grass and recessed solid core blocks; increased block bevel width.','Increased blade block depth and removed four narrow edge strips; seated two raised turf blocks farther into the mound.','Replaced exported PNG16 maps with color-managed PNG8 maps to correct measured Unreal sampling.']}
(out/'visual-review.json').write_text(json.dumps(review,indent=2))
placement['status']='saved_reload_and_native_views_verified_fidelity_open';(out/'world-placement.json').write_text(json.dumps(placement,indent=2))
adapt=read('source-adaptation.json');adapt['status']='imported_with_visual_refinement_open';adapt['revision']=review['revision'];(out/'source-adaptation.json').write_text(json.dumps(adapt,indent=2))
cards=[('Original concept','../../../SourceAssets/Voxel/grove.png'),('Blender front','front.png'),('Previous Blender leaves (R11)','R11/front.png'),('Current Unreal placement','World/unreal-viewport.png'),('Blender rear — inferred geometry','rear.png'),('Unreal context','Context/unreal-viewport.png')]
body=''.join('<figure><figcaption>'+html.escape(title)+'</figcaption><a href="'+path+'"><img src="'+path+'" alt="'+html.escape(title)+'"></a></figure>' for title,path in cards)
(out/'comparison.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Grove concept and model</title><style>body{margin:32px;background:#161a13;color:#ecf1e7;font:16px/1.5 system-ui}h1{font-size:28px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:20px}figure{margin:0;background:#252a20;padding:12px}img{width:100%;height:420px;object-fit:contain;background:#10130e}figcaption{margin-bottom:10px}p{max-width:1000px}</style><h1>Grove — fidelity review remains open</h1><p>Editable physical Blender model: 109 closed parts, 11,772 triangles and three packed maps. The 27.13 cm model is seated on the market counter. Individually modeled soil and turf replace the regular grid mound. At the unchanged Blender camera, leaf-and-fork outline intersection over union improved from 94.4% (R11) to 97.0% (R13); this measures the outline alone. The modeled blade depth now forms the exposed stepped sides. Unreal world lighting is unchanged.</p><main>'+body+'</main><p>Remaining: leaf volume and edge profiles, recessed turf joints, soil depth, and shaded color matching. Rear geometry is inferred. Passing structural and color-sampling checks does not establish a perfect concept match.</p></html>',encoding='utf-8')
readme=root/'Docs/BlenderRebuild/README.md';text=readme.read_text(encoding='utf-8')
start=text.index('## Grove');end=text.index('## Item atlas color correction',start)
text=text[:start]+f"""## Grove

`grove.png` revision R13 has an editable Blender project with {mesh['parts']} closed parts and {mesh['triangles']:,} triangles. Individually shaped soil and turf courses replace the regular grid mound; the base includes hanging grass and a connected recessed core. R13 increases blade-block depth, removes four narrow side strips, and seats two raised turf blocks farther into the mound. All parts have positive volume and form one overlapping assembly. This is not a Boolean-unioned mesh.

The model is on the right market counter at ({placement['location_cm'][0]:.3f}, {placement['location_cm'][1]:.3f}, {placement['location_cm'][2]:.3f}) cm, scale {placement['scale']}, height {placement['height_cm']:.3f} cm. Saved-map reload, material bindings, export hash, and {len(placement['support_probes'])} soil-center counter probes passed. The lowest soil course clears the counter by 0.02 cm; higher irregular courses do not all touch the counter. Native front, side and context views were inspected.

At the unchanged studio camera, the base silhouette intersection over union is 97.8%, improved from 84.6% at R7. Leaf-and-fork outline overlap improved from 94.4% (R11) to 97.0% (R13), and the full silhouette from 95.5% to 97.1%. `Grove/silhouette-comparison.json` records the mask method and exact image hashes. This measures the projected outline only, not overall visual fidelity. `Grove/comparison.html` shows the concept, old and current studio model, and native world views.

Three packed PNG8 maps preserve the previously GPU-verified color atlas bytes. Leaf volume and edge profiles, recessed turf joints, soil depth and shaded color still differ from the concept. Rear geometry is inferred. Fidelity remains unapproved.

"""+text[end:]
readme.write_text(text,encoding='utf-8')
print('Grove source, GLB, saved map and unchanged sampled color atlas verified. Fidelity remains open.')
