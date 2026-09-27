"""Record bounded batch evidence and an explicit, unapproved fidelity review."""
import json,hashlib,struct,html
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2];docs=root/'Docs/BlenderRebuild';out=docs/'RemainingBatch';keys=['Kindlehorn','Rillip','Player','RangerSela','HomesteadCompound']
notes={
 'Kindlehorn':'Tall upright ears, central emissive horn, cream muzzle/chest, dark hooves and rear flame tail are present. The head is squarer, ear recesses flatter and horn less tapered than the source; subtle ember particles are omitted.',
 'Rillip':'Closed stepped body, mint fins/toes, blush, smile and crown tip are present. Body layers were repaired to overlap. The silhouette is more pyramidal and less rounded than the source; foam placement remains approximate.',
 'Player':'Front and back references share one physical model, including orange jacket, gold scarf, green backpack with pockets/buckles, boots and face. Body stance, head/hair volume and scarf silhouette are simplified. A rear render verifies the equipment. Atlas poses are references only.',
 'RangerSela':'Teal long coat, cream scarf, silver hair, shoulder insignia, diagonal strap and ochre satchel are present. Hair, face, tailoring and stance remain simplified; unseen rear details are inferred. The pose atlas is retained as reference only.',
 'HomesteadCompound':'Existing editable Cottage geometry/material is reused, with new shed, fence, planted bed, lamppost, shrine and flowerbed. Arrangement is a first-pass adaptation, with a larger cottage footprint and simpler plants/stonework than the source. The open courtyard uses real empty space; no object-image billboards.'}
rows=[]
for key in keys:
 folder=docs/key;source=root/'SourceAssets/Blender'/key
 mesh=json.loads((folder/'mesh-validation.json').read_text());saved=json.loads((folder/'saved-blend-verification.json').read_text());imp=json.loads((folder/'unreal-import.json').read_text())
 assert saved['sha256']==hashlib.sha256((source/(key+'.blend')).read_bytes()).hexdigest()
 assert imp['source_fbx_sha256']==hashlib.sha256((source/('SM_Blender_'+key+'.fbx')).read_bytes()).hexdigest()
 assert mesh['all_parts_closed_positive_volume'] and imp['scale_verified']
 b=(source/('SM_Blender_'+key+'.glb')).read_bytes();magic,version,total=struct.unpack_from('<III',b);length,kind=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+length]);assert magic==0x46546c67 and version==2 and total==len(b)
 assert len(g['meshes'])==1 and all('TEXCOORD_0' in p['attributes'] and 'NORMAL' in p['attributes'] for p in g['meshes'][0]['primitives'])
 (folder/'glb-validation.json').write_text(json.dumps({'meshes':1,'uv_and_normals':True,'bytes':len(b),'visual_acceptance':False},indent=2))
 imp['status']='imported_saved_visual_reviewed_fidelity_pending';(folder/'unreal-import.json').write_text(json.dumps(imp,indent=2))
 (folder/'visual-review.md').write_text('# '+key+' — bounded first-pass review\n\n'+notes[key]+'\n\nValidated: packed editable Blender project reopened independently; closed positive-volume component solids; FBX/GLB and UVs; Unreal material bindings and import scale; saved review-map reopen and shared native viewport. Touching/overlapping editable blocks are not a welded character mesh. No rig, animation, locomotion, collision navigation, or game performance acceptance is claimed.\n\nStatus: authored/imported, fidelity unapproved.\n',encoding='utf-8')
 rows.append({'asset':key,'source':mesh['source'],'parts':mesh['parts'],'triangles':mesh['triangles'],'dimensions_cm':imp['dimensions_cm'],'saved_blend_sha256':saved['sha256'],'fbx_sha256':imp['source_fbx_sha256'],'fidelity_approved':False,'review_note':notes[key]})
surface=json.loads((docs/'SurfaceLibrary/unreal-import.json').read_text());assert surface['material_count']==45 and surface['sample_count']==45
assert json.loads((docs/'SurfaceLibrary/saved-blend-verification.json').read_text())['packed_images']==45
inventory=json.loads((docs/'inventory.json').read_text());assert inventory['source_count']==77 and inventory['unassigned_source_count']==0
world=json.loads((out/'unreal-verification.json').read_text());assert hashlib.sha256((root/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap').read_bytes()).hexdigest()==world['homestead_map_sha256_before']
(out/'batch-validation.json').write_text(json.dumps({'new_models':rows,'source_count':77,'primary_models_total':31,'surface_materials':45,'associated_references':5,'unassigned_sources':0,'fidelity_approvals':0,'original_homestead_unchanged':True,'surface_unreal_visual_samples':['terrain_water_v9','terrain_cliff_face_v9_candidate','cottage_roof_tile_v6_candidate'],'no_rigs_or_animations_delivered':True},indent=2))
# Refresh the one collection contact sheet from existing renders, with no rerender.
primary=[x for x in inventory['assets'] if x['coverage_role']=='primary_model'];sheet=Image.new('RGB',(1280,((len(primary)+3)//4)*195),'#ddd8cd');draw=ImageDraw.Draw(sheet)
for i,row in enumerate(primary):
 key=Path(row['blender_model']).stem;x=(i%4)*320;y=(i//4)*195
 for j,p in enumerate([root/'SourceAssets/Voxel'/row['source'],docs/key/'front.png']):
  if not p.exists():continue
  im=Image.open(p).convert('RGBA');im.thumbnail((155,172));bg=Image.new('RGBA',im.size,'#343933');bg.alpha_composite(im);sheet.paste(bg.convert('RGB'),(x+j*160,y))
 draw.text((x,y+175),key+' | source / model',fill='black')
sheet.save(out/'collection-overview.jpg')
cards=[]
for row in rows:
 key=row['asset'];cards.append(f'<article><h2>{key}</h2><div class="pair"><img src="../../../{row["source"]}"><img src="../{key}/front.png"></div><p>{html.escape(notes[key])}</p><p>{row["parts"]} editable parts · {row["triangles"]:,} triangles · <a href="../../../SourceAssets/Blender/{key}/{key}.blend">Blender file</a></p></article>')
page='''<!doctype html><meta charset="utf-8"><title>Terrarium remaining asset batch</title><style>body{max-width:1200px;margin:40px auto;padding:0 24px;background:#242820;color:#eeeadd;font:16px/1.6 system-ui}a{color:#c9de94}img{max-width:100%;background:#353b30}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}.pair img{width:100%;height:470px;object-fit:contain}article{border-top:1px solid #60664f;margin-top:30px;padding-top:12px}</style><h1>Remaining Terrarium models — authored and imported</h1><p>Five new primary models, 45 material alternatives, and explicit coverage of all 77 source PNGs. Fidelity remains unapproved. Characters are static, with no delivered rig or animation.</p><h2>Unreal review map</h2><p>/Game/Terrarium/Blender/Maps/RemainingModelsReview. Original HomesteadBlender map is unchanged.</p><img src="unreal-viewport.png">'''+''.join(cards)+'''<h2>Material alternatives</h2><p>45 packed source surface images, Blender materials and physical sample slabs, imported as 45 Unreal materials/textures and samples. Water is an opaque appearance sample, not a water simulation. Revisions remain alternatives; world assignments are unchanged.</p><img src="../SurfaceLibrary/overview.png"><h2>Collection comparison</h2><p>One contact-sheet review of existing previews. Broad silhouettes and material identity were inspected; no full-collection rerender or fidelity acceptance was performed.</p><img src="collection-overview.jpg">'''
(out/'review.html').write_text(page,encoding='utf-8')
print('Verified 5 new model sources/exports/imports; 45 surface materials; 77 source records; 0 fidelity approvals.')
