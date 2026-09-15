"""Closed terrain tile with the unmodified v9 grass albedo and shallow physical relief."""
import sys,shutil,math,json,hashlib
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import bpy
from assetkit import Asset,ROOT
a=Asset('GrassTerrain','terrain_grass_top_v9.png',[('707832','mineral')])
source=ROOT/a.scene['concept'];target=a.out/'GrassTerrain_BaseColor.png'
shutil.copyfile(source,target)
original=bpy.data.images.load(str(target),check_existing=False);original.name='GrassTerrain_SourceAlbedo';original.pack()
for node in a.material.node_tree.nodes:
    if node.type=='TEX_IMAGE' and 'BaseColor' in node.image.name:
        node.image=original;node.interpolation='Linear'
pixels=list(original.pixels);iw,ih=original.size
def luminance(u,v):
    at=(min(ih-1,int(v*(ih-1)))*iw+min(iw-1,int(u*(iw-1))))*4
    return pixels[at]*.2126+pixels[at+1]*.7152+pixels[at+2]*.0722
n=8
lum=[luminance(ix/n,iy/n) for iy in range(n+1) for ix in range(n+1)]
low,high=min(lum),max(lum)
verts=[]
for iy in range(n+1):
    for ix in range(n+1):
        z=0 if ix in [0,n] or iy in [0,n] else -.009*(high-lum[iy*(n+1)+ix])/(high-low)
        verts.append((-1+2*ix/n,-1+2*iy/n,z))
faces=[]
for iy in range(n):
    for ix in range(n):
        q=iy*(n+1)+ix
        faces.extend([(q,q+1,q+n+2),(q,q+n+2,q+n+1)])
ring=list(range(n+1))+[iy*(n+1)+n for iy in range(1,n+1)]+[n*(n+1)+ix for ix in range(n-1,-1,-1)]+[iy*(n+1) for iy in range(n-1,0,-1)]
bottom=[]
for i in ring:
    x,y,z=verts[i];bottom.append(len(verts));verts.append((x,y,-.12))
for j in range(len(ring)):
    k=(j+1)%len(ring);faces.append((ring[j],bottom[j],bottom[k],ring[k]))
faces.append(tuple(reversed(bottom)))
mesh=bpy.data.meshes.new('Grass terrain closed surface');mesh.from_pydata(verts,[],faces);mesh.update()
ob=bpy.data.objects.new('Grass terrain closed surface',mesh);a.scene.collection.objects.link(ob)
ob['part']='Closed grass terrain with shallow relief';a.parts.append(ob);mesh.materials.append(a.material)
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
    for li in poly.loop_indices:
        v=mesh.vertices[mesh.loops[li].vertex_index].co
        uv.data[li].uv=((v.x+1)/2,(v.y+1)/2)
a.scene['surface_top_m']=0.;a.scene['support_bottom_m']=-.12
a.scene['maximum_relief_m']=.009
a.scene['albedo_policy']='Unmodified source PNG; no generated palette replaces its colors.'
a.studio(focus=(0,0,-.03),location=(3,-4,4),scale=3.15)
a.scene.render.resolution_x=1200;a.scene.render.resolution_y=1000
result=a.save()
(a.review/'height-samples.json').write_text(json.dumps({'center_surface_z_m':float(mesh.vertices[(n//2)*(n+1)+n//2].co.z),'boundary_z_m':0,'max_relief_m':.009},indent=2))
(a.review/'source-texture-verification.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'copied_albedo':str(target.relative_to(ROOT)),'byte_identical':source.read_bytes()==target.read_bytes(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'relief_policy':'Up to 0.9 cm shallow relief sampled from source luminance; this is an inferred height surface, not height data supplied by the reference.'},indent=2))
