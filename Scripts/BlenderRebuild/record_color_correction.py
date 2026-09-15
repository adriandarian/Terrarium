"""Verify four corrected atlases and preserve geometry and visual-review evidence."""
import json,hashlib,struct,html
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'Docs/BlenderRebuild/ColorManagement'
keys=['DeepDelverMark','EmberCrest','MossTonic','TrailPrism']
def load(p):return json.loads(p.read_text())
def glb(path):
    b=path.read_bytes();assert b[:4]==b'glTF';n=struct.unpack_from('<I',b,12)[0]
    g=json.loads(b[20:20+n]);offset=20+n
    size,kind=struct.unpack_from('<II',b,offset);assert kind==0x004e4942
    return g,b[offset+8:offset+8+size]
def accessor(g,b,index):
    a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
    width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]*{5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a['componentType']]
    start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',width)
    return b''.join(b[start+i*stride:start+i*stride+width] for i in range(a['count']))
def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
before={r['asset']:r for r in load(out/'four-atlases-before.json')}
after={r['asset']:r for r in load(out/'four-atlases-after.json')}
rows=[];sections=[]
for key in keys:
    source=root/'SourceAssets/Blender'/key;docs=root/'Docs/BlenderRebuild'/key;backup=source/'Revisions/BeforeColorFix'
    oldg,oldb=glb(backup/f'SM_Blender_{key}.glb');g,b=glb(source/f'SM_Blender_{key}.glb')
    def material_roles(materials):
        return [dict(m,name=m['name'].split('.')[0]) for m in materials]
    assert material_roles(oldg['materials'])==material_roles(g['materials']),key+' changed material factors'
    oldp=oldg['meshes'][0]['primitives'];p=g['meshes'][0]['primitives'];assert len(p)==len(oldp)
    uv_error=0
    for a,c in zip(oldp,p):
        assert a['attributes'].keys()==c['attributes'].keys()
        for semantic in a['attributes']:
            old_values=accessor(oldg,oldb,a['attributes'][semantic]);new_values=accessor(g,b,c['attributes'][semantic])
            if semantic=='TEXCOORD_0':
                assert len(old_values)==len(new_values)
                fmt='<'+str(len(old_values)//4)+'f'
                error=max(abs(x-y) for x,y in zip(struct.unpack(fmt,old_values),struct.unpack(fmt,new_values)))
                uv_error=max(uv_error,error);assert error<1e-6,(key,semantic,error)
            else:assert old_values==new_values,(key,semantic)
        assert accessor(oldg,oldb,a['indices'])==accessor(g,b,c['indices']),key
    mesh=load(docs/'mesh-validation.json');previous=load(out/key/'Before/mesh-validation.json')
    for field in ['parts','vertices','triangles','bounds_m','material_slots']:assert mesh[field]==previous[field],(key,field)
    for name,r in mesh['files'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==r['sha256']
    assert hashlib.sha256((source/(key+'.blend')).read_bytes()).hexdigest()==load(docs/'saved-blend-verification.json')['sha256']
    assert load(docs/'unreal-import.json')['source_fbx_sha256']==mesh['files'][f'SM_Blender_{key}.fbx']['sha256']
    assert load(docs/'saved-world-verification.json')['reload_verified']
    assert load(out/key/'Before/unreal-camera.json')==load(out/key/'After/unreal-camera.json')
    stats={}
    for stage,probe,folder in [('before',before[key],backup),('after',after[key],source)]:
        path=folder/(key+'_BaseColor.png');assert hashlib.sha256(path.read_bytes()).hexdigest()==probe['source_sha256']
        im=Image.open(path).convert('RGB');errors=[]
        for s in probe['samples']:
            expected=[linear(v/255) for v in im.getpixel(tuple(s['source_pixel']))]
            errors.extend(abs(a-b) for a,b in zip(s['linear_rgb'],expected))
        stats[stage]={'mean_linear_channel_error':sum(errors)/len(errors),'max_linear_channel_error':max(errors)}
    assert after[key]['source_bit_depth']==8 and after[key]['srgb']
    assert stats['after']['max_linear_channel_error']<.011 and stats['after']['mean_linear_channel_error']<stats['before']['mean_linear_channel_error']/20
    rows.append({'asset':key,'positions_normals_indices_byte_identical':True,'max_uv_coordinate_roundoff':uv_error,'glb_material_factors_preserved':True,'saved_blend_reopened':True,'map_reload_verified':True,'camera_pair_identical':True,'colors':stats,'fidelity_accepted':False})
    review=load(docs/'visual-review.json');review['color_correction']={'maps':'PNG8','evidence':'../ColorManagement/'+key,'finding':'Corrected missing sRGB decode measured in the previous PNG16 atlas import. Geometry and material factors preserved.'}
    review['world_views']=[f'../ColorManagement/{key}/{p}/unreal-viewport.png' for p in ['After','AfterSide','AfterContext']]
    review['accepted_fidelity']=False;(docs/'visual-review.json').write_text(json.dumps(review,indent=2))
    concept=Path(mesh['source']).name
    items=[('Concept',f'../../../SourceAssets/Voxel/{concept}'),('Before — PNG16 import',f'{key}/Before/unreal-viewport.png'),('After — corrected sampling',f'{key}/After/unreal-viewport.png')]
    cards=''.join(f'<figure><figcaption>{html.escape(title)}</figcaption><a href="{path}"><img loading="lazy" src="{path}" alt="{html.escape(title)}"></a></figure>' for title,path in items)
    sections.append(f'<section><h2>{key}</h2><p>Mean sampled linear color error: {stats["before"]["mean_linear_channel_error"]:.4f} → {stats["after"]["mean_linear_channel_error"]:.4f}. Matching native camera and lighting. Geometry unchanged.</p><div class="views">{cards}</div></section>')
(out/'verification.json').write_text(json.dumps({'assets':rows,'measurement':'32 palette-cell centers per atlas through a transient texture-sampling material into an RGBA32F target, read without normalization; compared with sRGB-decoded source PNG pixels. Production shaders are not modified by the probe.','limits':'Residual differences include texture compression and filtering. This validates these four import paths, not every Unreal PNG16 texture. Geometry preservation and color correctness do not establish concept fidelity.'},indent=2))
audit=[]
for folder in sorted((root/'SourceAssets/Blender').iterdir()):
    p=folder/(folder.name+'_BaseColor.png')
    if p.exists():audit.append({'asset':folder.name,'basecolor':str(p.relative_to(root)),'bit_depth':p.read_bytes()[24],'needs_shader_sampling_check':p.read_bytes()[24]==16})
(out/'atlas-bit-depth-audit.json').write_text(json.dumps({'confirmed_and_corrected_assets':['Grove']+keys,'scope':'Current top-level Blender atlas files; archived revisions excluded. Only the five listed assets received direct GPU color probes.','assets':audit},indent=2))
(out/'comparison.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Atlas color correction</title><style>body{margin:32px;background:#181914;color:#eee;font:16px/1.5 system-ui}p{max-width:1100px}.views{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}figure{margin:0;background:#24271f;padding:12px}img{width:100%;height:380px;object-fit:contain;background:#10110e}section{margin:40px 0}figcaption{margin-bottom:10px}@media(max-width:850px){.views{grid-template-columns:1fr}}</style><h1>Four corrected color atlases</h1><p>The original 16-bit PNG atlases sampled encoded RGB despite their sRGB flag. Blender now exports and packs 8-bit maps, and Unreal samples the expected linear values. This fixes the measured import problem. The crests still need closer material and relief matching; tonic glass still reads too opaque, and prism glow remains flatter than its concept. Full collection fidelity is open.</p>'+''.join(sections)+'</html>',encoding='utf-8')
print(json.dumps(rows,indent=2))
