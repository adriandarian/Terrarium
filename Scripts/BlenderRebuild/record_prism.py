"""Record inspected prism views and export checks, with fidelity still open."""
import json,hashlib,struct
from pathlib import Path
root=Path(__file__).resolve().parents[2];folder=root/'Docs/BlenderRebuild/TrailPrism';source=root/'SourceAssets/Blender/TrailPrism'
mesh=json.loads((folder/'mesh-validation.json').read_text());opened=json.loads((folder/'saved-blend-verification.json').read_text())
assert opened['sha256']==hashlib.sha256((source/'TrailPrism.blend').read_bytes()).hexdigest()
for name,record in mesh['files'].items():assert record['sha256']==hashlib.sha256((source/name).read_bytes()).hexdigest()
data=(source/'SM_Blender_TrailPrism.glb').read_bytes();magic,version,length=struct.unpack_from('<III',data);size,kind=struct.unpack_from('<II',data,12)
assert magic==0x46546c67 and version==2 and length==len(data)
g=json.loads(data[20:20+size]);assert len(g['meshes'])==1 and len(g['meshes'][0]['primitives'])==3
roles={next(role for role in ['Crystal','Core','Frame'] if m['name'].startswith('M_TrailPrism_'+role)):m for m in g['materials']}
assert abs(roles['Crystal']['extensions']['KHR_materials_transmission']['transmissionFactor']-.82)<1e-6
assert abs(roles['Crystal']['extensions']['KHR_materials_ior']['ior']-1.12)<1e-6
assert abs(roles['Frame']['pbrMetallicRoughness']['metallicFactor']-.82)<1e-6
assert len(g['images'])==3 and all('bufferView' in im for im in g['images'])
(folder/'file-verification.json').write_text(json.dumps({'current_hashes_verified':True,'glb_primitives':3,'embedded_images':3,'crystal_transmission':.82,'crystal_ior':1.12,'frame_metallic':.82,'blend_direct_open_verified':True,'visual_acceptance':False},indent=2))
review={'revision':'r6_wrapped_cage_and_raised_equator','parts':mesh['parts'],'triangles':mesh['triangles'],'changes':['Continuous stepped amber crystal with separate luminous solid inclusion','Raised equatorial frame and longer lower taper','Narrower upper tip and four orthogonal corner clamps with joined top pegs','Three packed atlas textures and material roles retained through FBX and GLB','World exposure retained; core emission, local point light and an explicit amber-scattering approximation support the glow in shade'],
        'studio_views':['front.png','rear.png'],'world_views':['Current/unreal-viewport.png','Side/unreal-viewport.png','Context/unreal-viewport.png'],'visually_checked':True,
        'remaining':['Crystal tier proportions and facet pattern still differ from the concept','Clamp/stud dimensions and metal color need closer source matching','Blender internal reflections differ from the illustrated core','Unreal crystal is paler and flatter; the outer bronze is much darker under the awning','Unseen rear is inferred from the four-sided design'],
        'optics_limit':'The Blender crystal uses stylized transmission 0.82 and IOR 1.12. UE surface translucency uses opacity 0.36, refraction 1.0054, core emission 2000 and amber-scattering emission 1800 at world exposure bias -12. A 150 lumen shadowless point light approximates core illumination over 40 cm. This is not path-traced optical equivalence.',
        'accepted_fidelity':False}
(folder/'visual-review.json').write_text(json.dumps(review,indent=2))
adapt=json.loads((folder/'source-adaptation.json').read_text());adapt.update({'status':'imported_with_visual_refinement_open','revision':review['revision']});(folder/'source-adaptation.json').write_text(json.dumps(adapt,indent=2))
placement=json.loads((folder/'world-placement.json').read_text());placement['status']='saved_reload_and_native_views_verified_fidelity_open';(folder/'world-placement.json').write_text(json.dumps(placement,indent=2))
readme=root/'Docs/BlenderRebuild/README.md';text=readme.read_text(encoding='utf-8')
text=text.replace('All 25 currently authored Blender outputs (18 source concepts and seven placement variants)','All 26 currently authored Blender outputs (19 source concepts and seven placement variants)')
start=text.find('`trail_prism.png` ')
if start>=0:
    end=text.index('`moss_tonic.png` ',start);text=text[:start]+text[end:]
section='''`trail_prism.png` now has an editable Blender project at `SourceAssets/Blender/TrailPrism/TrailPrism.blend`. The current model has 122 closed positive-volume parts and 17,432 triangles: a continuous stepped amber crystal, separate luminous inclusion, four bronze rails, orthogonal stepped corner clamps and gold studs. Three packed textures and three material slots survive the FBX/GLB export. The normal `.blend` was independently opened with its own active scene and camera. The unseen rear is inferred from the four-sided design.

`Blender_TrailPrism_MarketCounter` is placed in HomesteadBlender at (307, 623, 635.012) cm, uniform scale 0.19 and height 21.28 cm. Nine samples under its small flat tip hit the counter; the saved base clearance is 0.02 cm. After reload, the actor transform, three material bindings and parameters, texture color spaces, source FBX hash and companion core light passed verification. The 150 lumen local light has a 40 cm radius. World exposure remains at bias -12. Source studio front/rear and native three-quarter/side/context views are available in `TrailPrism/`.

The prism is still an approximation. Tier proportions, facet distribution, clamp dimensions and core reflections need closer matching. Unreal uses surface translucency plus explicit core-scattering emission, which looks paler and flatter than the Blender crystal; outer bronze remains dark under the awning. This is not optical equivalence. Gameplay pickup, rigid-body balance, all-view translucency and performance remain untested. No perfect-fidelity approval is recorded.

'''
text=text.replace('`moss_tonic.png` ',section+'`moss_tonic.png` ',1);readme.write_text(text,encoding='utf-8')
print('TrailPrism current files and GLB materials verified; visual refinement remains open.')
