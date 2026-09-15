"""Current-file checks and visual-review record for the physical Ember Crest."""
import json,hashlib,struct
from pathlib import Path
root=Path(__file__).resolve().parents[2];folder=root/'Docs/BlenderRebuild/EmberCrest';source=root/'SourceAssets/Blender/EmberCrest'
mesh=json.loads((folder/'mesh-validation.json').read_text());opened=json.loads((folder/'saved-blend-verification.json').read_text())
assert opened['sha256']==hashlib.sha256((source/'EmberCrest.blend').read_bytes()).hexdigest()
for name,record in mesh['files'].items():assert record['sha256']==hashlib.sha256((source/name).read_bytes()).hexdigest()
b=(source/'SM_Blender_EmberCrest.glb').read_bytes();magic,version,size=struct.unpack_from('<III',b);n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n])
assert magic==0x46546c67 and version==2 and size==len(b)
assert len(g['meshes'])==1 and len(g['meshes'][0]['primitives'])==3 and len(g['images'])==3
for m in g['materials']:
    role=next(r for r in ['Frame','Enamel','Field'] if m['name'].startswith('M_EmberCrest_'+r))
    assert abs(m['pbrMetallicRoughness']['metallicFactor']-(.72 if role=='Frame' else .12))<1e-6
    assert m.get('emissiveFactor',[0,0,0])==[0,0,0]
(folder/'file-verification.json').write_text(json.dumps({'current_export_hashes_verified':True,'blend_direct_open_verified':True,'glb_material_roles':3,'glb_embedded_images':3,'non_emissive':True,'visual_acceptance':False},indent=2))
review={'revision':'r4_measured_flame_and_textured_gold','parts':mesh['parts'],'triangles':mesh['triangles'],
        'changes':['Measured stepped shield and rim silhouette reconstructed as solids','Recessed charcoal tile field and continuous backing','Raised enamel flame blocks, corrected central gap and taller upper yellow tier','Four faceted red gems in thick gold sockets','Fine gold grain in packed albedo and roughness textures','Moved world mounting left to clear existing folded cloth'],
        'studio_views':['front.png','rear.png'],'world_views':['Current/unreal-viewport.png','Current/Side/unreal-viewport.png','Current/Context/unreal-viewport.png'],'visually_checked':True,
        'remaining':['Exact flame color distribution and block depths','Lower rim courses and gem-bevel proportions','Gold microtexture scale and turquoise patina placement','World shading is much darker and cooler than the concept','Plain rear is inferred from a single front concept'],
        'presentation':'Blender Standard color transform, medium high contrast, exposure -0.35. Unreal uses its existing world lighting and exposure. No emissive flame shader or added light.',
        'accepted_fidelity':False}
(folder/'visual-review.json').write_text(json.dumps(review,indent=2))
adapt=json.loads((folder/'source-adaptation.json').read_text());adapt.update({'revision':review['revision'],'status':'imported_with_visual_refinement_open'});(folder/'source-adaptation.json').write_text(json.dumps(adapt,indent=2))
placement=json.loads((folder/'world-placement.json').read_text());placement['status']='saved_reload_and_native_views_verified_fidelity_open';(folder/'world-placement.json').write_text(json.dumps(placement,indent=2))
readme=root/'Docs/BlenderRebuild/README.md';text=readme.read_text(encoding='utf-8')
text=text.replace('All 26 currently authored Blender outputs (19 source concepts and seven placement variants)','All 27 currently authored Blender outputs (20 source concepts and seven placement variants)')
start=text.find('`ember_crest.png` ')
if start>=0:
    end=text.index('`trail_prism.png` ',start);text=text[:start]+text[end:]
section='''`ember_crest.png` now has a normal editable Blender project at `SourceAssets/Blender/EmberCrest/EmberCrest.blend`. It contains 582 closed solid parts and exports to 65,624 triangles: a continuous shield body, stepped gold rim, recessed charcoal tiles, raised flame blocks, central ember cross, and four faceted red gems. Albedo and roughness include fine gold grain. Three packed textures and three material roles are retained through FBX/GLB. The rear is an inferred plain minted plate. The final `.blend` was directly opened and inspected in an independent Blender process.

`Blender_EmberCrest_MarketFront` is mounted against the left counter at (184, 628.175, 592) cm, uniform scale 0.24 and height 28.628 cm. The original position was shifted 14 cm left after an oblique viewport exposed occlusion by folded cloth. All nine final wall samples, a 0.015 cm back clearance, the transform, three shader bindings and parameters, texture color spaces and export/import hash passed after map reload. Current native front, side and wider context views are under `EmberCrest/Current/`; studio images are `front.png` and `rear.png`.

The crest remains under refinement. Flame color/depth distribution, lower rim courses, gem bevels and patina need closer reference matching. Unreal's awning shade is much darker and cooler than the reference; no emissive shader or additional light was used to conceal that difference. Attachment hardware, pickup gameplay, full collision and performance have not been validated. No perfect-fidelity approval is recorded.

'''
text=text.replace('`trail_prism.png` ',section+'`trail_prism.png` ',1);readme.write_text(text,encoding='utf-8')
print('EmberCrest current files, embedded maps and material roles verified; fidelity remains open.')
