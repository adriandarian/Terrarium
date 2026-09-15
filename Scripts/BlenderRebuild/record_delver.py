"""Verify current Delver files and record the inspected visual limitations."""
import json,hashlib,struct
from pathlib import Path
root=Path(__file__).resolve().parents[2];folder=root/'Docs/BlenderRebuild/DeepDelverMark';source=root/'SourceAssets/Blender/DeepDelverMark'
mesh=json.loads((folder/'mesh-validation.json').read_text());opened=json.loads((folder/'saved-blend-verification.json').read_text())
assert opened['sha256']==hashlib.sha256((source/'DeepDelverMark.blend').read_bytes()).hexdigest()
for name,record in mesh['files'].items():assert record['sha256']==hashlib.sha256((source/name).read_bytes()).hexdigest()
b=(source/'SM_Blender_DeepDelverMark.glb').read_bytes();magic,version,size=struct.unpack_from('<III',b);n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n])
assert magic==0x46546c67 and version==2 and size==len(b)
assert len(g['meshes'])==1 and len(g['meshes'][0]['primitives'])==3 and len(g['images'])==3
for m in g['materials']:
    role=next(r for r in ['Frame','Cavern','Crystal'] if m['name'].startswith('M_DeepDelverMark_'+r))
    assert abs(m['pbrMetallicRoughness']['metallicFactor']-{'Frame':.65,'Cavern':.03,'Crystal':.10}[role])<1e-6
    assert m.get('emissiveFactor',[0,0,0])==[0,0,0]
(folder/'file-verification.json').write_text(json.dumps({'current_export_hashes_verified':True,'blend_direct_open_verified':True,'glb_material_roles':3,'glb_embedded_images':3,'non_emissive':True,'visual_acceptance':False},indent=2))
review={'revision':'r9_jointed_stone_and_socket_flange_refinement','parts':mesh['parts'],'triangles':mesh['triangles'],
    'changes':['Physical hexagonal gold frame, continuous wall to the solid back plate, four corner clips and two gem sockets.',
        'Recessed square cavern tiles and individual turned-square ledge columns.',
        'Raised mineral crystal glyph and faceted turquoise gems.',
        'Hidden sloping solid rear webs support the raised relief.',
        'Narrower upper stone band and individually jointed shoulder blocks.',
        'Shorter cavern columns with connecting stepped risers.',
        'Gold grain in albedo and roughness; angled socket braces and longer lower corner flanges.',
        'Socket rear supports now use the gold material after rear-view inspection.'],
    'studio_views':['front.png','rear.png'],'world_views':['World/unreal-viewport.png','Side/unreal-viewport.png','Context/unreal-viewport.png'],
    'visually_checked':True,'accepted_fidelity':False,
    'remaining':['Cavern ledges are too columnar and regular compared with the denser stepped source.',
        'Upper gray shoulders now have joints but still need closer fracture and color matching.',
        'Gold grain, reflective highlights, socket facets and corner profiles need closer matching.',
        'Unreal shades the gold greener and cavern bluer than the concept.',
        'Rear plate and support webs are inferred; full collision, pickup and performance remain untested.'],
    'presentation':'Blender Standard transform, Medium High Contrast, exposure -0.35; Unreal working sky fill 7 with manual bias -12. No added light or emissive material for this badge.'}
(folder/'visual-review.json').write_text(json.dumps(review,indent=2))
adapt=json.loads((folder/'source-adaptation.json').read_text());adapt.update(revision=review['revision'],status='imported_with_visual_refinement_open',unseen_structure='Plain cast rear, continuous perimeter wall and sloping relief support webs are inferred.')
(folder/'source-adaptation.json').write_text(json.dumps(adapt,indent=2))
placement=json.loads((folder/'world-placement.json').read_text());placement['status']='saved_reload_and_native_views_verified_fidelity_open'
(folder/'world-placement.json').write_text(json.dumps(placement,indent=2))
readme=root/'Docs/BlenderRebuild/README.md';text=readme.read_text(encoding='utf-8')
text=text.replace('All 27 currently authored Blender outputs (20 source concepts and seven placement variants)','All 28 currently authored Blender outputs (21 source concepts and seven placement variants)')
text=text.replace('461 closed solid parts, 51,452 exported triangles','585 closed solid parts, 64,948 exported triangles')
text=text.replace('The cavern is still too regular and columnar, upper stone shoulders too smooth, and gold highlights and grain do not yet match the concept.','The current revision narrows the upper band, adds stone joints, shortens cavern ledges, adds gold grain and refines the socket braces and lower flanges. The cavern still differs in density and depth, and gold highlights and roughness need closer matching. `DeepDelverMark/comparison.html` shows the source, earlier draft and current model; its silhouette measurement covers only the outer outline.')
if '## Working world lighting' not in text:
    text+='''\n## Working world lighting\n\nThe saved sky fill is now intensity 7 with neutral white tint. The sun remains at 22,500 lux and its original rotation; manual exposure remains bias -12. Four paired native camera views are recorded in `Lighting/comparison.html`. The stronger fill improves shaded relief readability while retaining visible sunlit roof and terrace detail. Prism's luminous core was also inspected after the change; it still looks pale and flat. Tonic's opaque-looking glass and the crests' muted metal remain material problems. Existing static placement bindings and the focused tonic, prism and crest checks passed after reload. This does not verify every foliage instance or establish fidelity.\n'''
if '`deep_delver_mark.png` now' not in text:
    section='''`deep_delver_mark.png` now has a normal editable Blender project at `SourceAssets/Blender/DeepDelverMark/DeepDelverMark.blend`: 585 closed solid parts, 64,948 exported triangles and three packed textures. It contains a hexagonal frame, continuous backing wall, stepped corner clasps, recessed cavern tiles and ledges, a raised crystal glyph and two faceted turquoise gems. Rear supports and the plain cast reverse are inferred from the single front concept. Independent direct-open and current FBX/GLB hash checks passed.

`Blender_DeepDelverMark_MarketFront` is mounted on the right counter at (355, 627.989, 590) cm, uniform scale 0.23 and height 30.036 cm. The saved map passed uniqueness, transform, all three shader bindings and parameters, texture color spaces, export hash and nine wall-contact checks. The back clearance is 0.015 cm. Front, side and wider context captures are under `DeepDelverMark/World`, `Side` and `Context`.

The cavern is still too regular and columnar, upper stone shoulders too smooth, and gold highlights and grain do not yet match the concept. Unreal adds a green cast to the gold and a blue cast to the cavern. No emission or extra light was added to the badge. Full collision, gameplay and performance remain untested. No perfect-fidelity approval is recorded.

'''
    text=text.replace('## Remaining visual work\n\n','## Remaining visual work\n\n'+section)
readme.write_text(text,encoding='utf-8')
print('Delver current files, embedded maps and three material roles verified; fidelity open.')

