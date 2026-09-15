"""Physical moss cushions using the supplied color image and sampled, inferred relief."""
import sys,json,shutil,hashlib,math
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import bpy
from assetkit import Asset,ROOT

def build(key='MossCap',fringe=False):
    a=Asset(key,'terrain_moss_cap_v1.png',[('5b6820','mineral')])
    if fringe:
        a.scene['variant_of']='MossCap';a.scene['variant_purpose']='Cliff-lip cushion and connected hanging fingers using the source moss pattern; hanging silhouette and depth are inferred.'
    source=ROOT/a.scene['concept'];target=a.out/(key+'_BaseColor.png');shutil.copyfile(source,target)
    im=bpy.data.images.load(str(target),check_existing=False);im.name=key+'_SourceAlbedo';im.pack()
    for node in a.material.node_tree.nodes:
        if node.type=='TEX_IMAGE' and 'BaseColor' in node.image.name:node.image=im
    pixels=list(im.pixels);iw,ih=im.size
    def brightness(u,v):
        x=int((u%1)*(iw-1));y=int((v%1)*(ih-1));at=(y*iw+x)*4
        return pixels[at]*.2126+pixels[at+1]*.7152+pixels[at+2]*.0722
    values=sorted(brightness(x/96,y/96) for y in range(96) for x in range(96));lo=values[len(values)//10];hi=values[len(values)*9//10]
    def relief(u,v):
        lum=sum(brightness(u+dx/iw*5,v+dy/ih*5) for dx,dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1)])/5
        weight=max(0,min(1,(lum-lo)/(hi-lo)))
        return .002+.002*round(weight*5)
    vs=[];fs=[];uvs=[];cells=0
    def box(x0,x1,y0,y1,z0,z1,uvmode,orientation='top'):
        nonlocal cells
        start=len(vs)
        vv=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
        vs.extend(vv)
        for fi,face in enumerate([(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]):
            fs.append(tuple(start+i for i in face));face_uv=[]
            for i in face:
                x,y,z=vv[i];u,v=uvmode(x,y,z)
                if fringe and orientation=='top':
                    if fi in [2,4]:v+=(z-.006)/.422
                    elif fi in [3,5]:u+=(z-.006)/.493
                elif fringe and orientation=='front':
                    if fi in [2,4]:u+=(x-.184)/.422
                    elif fi in [0,1]:v+=(x-.184)/.422
                face_uv.append((u,v))
            uvs.append(face_uv)
        cells+=1
    if not fringe:
        n=96;size=.64;step=size/n
        for iy in range(n):
            for ix in range(n):
                x=-size/2+ix*step;y=-size/2+iy*step
                z=relief((ix+.5)/n,(iy+.5)/n)
                box(x,x+step,y,y+step,-.012,z,lambda x,y,z:(x/size+.5,y/size+.5))
        focus=(0,0,0);camera=(.7,-.9,1.2);scale=.97
    else:
        # L-shaped root cushion: +X grows out over the cliff edge.
        nx,ny=74,64;dx=.493/74;dy=.422/64
        for iy in range(ny):
            for ix in range(nx):
                x=-.26+ix*dx;y=-.215+iy*dy
                # Irregular rim, with every surviving cell joined into the cushion.
                islands=[(-.09,-.06,.17,.155),(.012,.075,.20,.12),(.095,-.11,.14,.095)]
                if not any(((x-cx)/rx)**2+((y-cy)/ry)**2 <= 1+.06*math.sin(x*49+y*61) for cx,cy,rx,ry in islands):continue
                u=x/.493+.53;v=y/.422+.51;z=relief(u,v)
                box(x,x+dx,y,y+dy,-.065,z,lambda x,y,z:(x/.493+.53,y/.422+.51))
        # Different finger lengths retain the existing cliff-fringe placement role.
        # Relief uses square source texels repeated down the vertical faces.
        dz=.0065;dy=.0065
        for iy in range(64):
            y=-.208+iy*dy
            for iz in range(177):
                z=-.0065*(iz+1)
                t=-z
                widths=[(-.116,.115,.54),(.012,.105,1.145),(.131,.123,.365)]
                active=False
                for center,width,length in widths:
                    taper=1-.48*min(1,t/length)
                    if t<=length and abs(y-center-.011*t/length)<width*taper/2:active=True
                if not active:continue
                u=y/.422+.51;v=(z/.422)%1
                # A thin moss coat avoids rigid, deeply layered hanging ribs.
                # Its root remains connected through the overlapping upper cushion.
                d=relief(u,v)*.25
                box(.170,.184+d,y,y+dy,max(-1.145,z),z+dz,lambda x,y,z:(y/.422+.51,z/.422),orientation='front')
        focus=(0,0,-.43);camera=(1.6,-1.8,1.1);scale=1.55
    mesh=bpy.data.meshes.new(key+' physical moss cells');mesh.from_pydata(vs,[],fs);mesh.update()
    ob=bpy.data.objects.new(key+' physical moss cushion',mesh);a.scene.collection.objects.link(ob);ob['part']='Source-patterned solid moss cells';a.parts.append(ob);mesh.materials.append(a.material)
    uv=mesh.uv_layers.new(name='UVMap')
    for poly,us in zip(mesh.polygons,uvs):
        for li,value in zip(poly.loop_indices,us):uv.data[li].uv=value
    a.scene['relief_policy']='Quantized 0.2-1.2 cm relief inferred from filtered source luminance; not measured height data.'
    a.scene['solid_cell_count']=cells
    if fringe:a.scene['hanging_relief_scale']=.25;a.scene['hanging_back_x_m']=.170
    a.studio(focus=focus,location=camera,scale=scale);a.scene.render.resolution_x=1100;a.scene.render.resolution_y=1100
    result=a.save()
    (a.review/'source-texture-verification.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'copied_albedo':str(target.relative_to(ROOT)),'byte_identical':source.read_bytes()==target.read_bytes(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'solid_cells':cells,'relief_inferred':True,'hanging_silhouette_inferred':fringe},indent=2))
    return result
if __name__=='__main__':result=build()
