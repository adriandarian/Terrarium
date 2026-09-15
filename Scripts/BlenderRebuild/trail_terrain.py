"""Source-colored solid trail tile and clipped irregular placement variant."""
import sys,json,shutil,hashlib,math
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import bpy,bmesh
from mathutils import Vector
from assetkit import Asset,ROOT
from trail_stones import STONES

def clip(poly,normal,limit):
    out=[]
    for p,q in zip(poly[-1:]+poly[:-1],poly):
        dp=sum(p[k]*normal[k] for k in range(2))-limit
        dq=sum(q[k]*normal[k] for k in range(2))-limit
        if (dp<=0)!=(dq<=0):
            t=dp/(dp-dq);out.append(tuple(p[k]+t*(q[k]-p[k]) for k in range(2)))
        if dq<=0:out.append(tuple(q))
    return out

def area(poly):
    return sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1]))/2

def inside(p,poly):
    result=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result

def overlap(a,b):
    if any(inside(p,b) for p in a) or any(inside(p,a) for p in b):return True
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    for p,q in zip(a,a[1:]+a[:1]):
        for r,s in zip(b,b[1:]+b[:1]):
            if cross(p,q,r)*cross(p,q,s)<0 and cross(r,s,p)*cross(r,s,q)<0:return True
    return False

def outlines():
    # Where hand traces touch, divide only the overlapping pair at their joint.
    # A 1.5 pixel joint prevents coincident faces; no random shape generation.
    polys=[[tuple(p) for p in points] for points in STONES];pairs=[]
    centers=[tuple(sum(p[k] for p in points)/len(points) for k in range(2)) for points in STONES]
    for i,a in enumerate(STONES):
        for j in range(i+1,len(STONES)):
            b=STONES[j]
            if not overlap(a,b):continue
            delta=[centers[j][k]-centers[i][k] for k in range(2)];length=math.hypot(*delta)
            n=[d/length for d in delta]
            limit=(max(sum(p[k]*n[k] for k in range(2)) for p in a)+min(sum(p[k]*n[k] for k in range(2)) for p in b))/2
            polys[i]=clip(polys[i],n,limit-.75)
            polys[j]=clip(polys[j],[-v for v in n],-limit-.75)
            pairs.append([i+1,j+1])
    assert all(len(p)>=3 and abs(area(p))>5 for p in polys)
    assert not any(overlap(a,b) for i,a in enumerate(polys) for b in polys[i+1:])
    return polys,pairs

def build(key='TrailTerrain',patch=False):
    a=Asset(key,'terrain_trail_top_v8.png',[('c69c42','mineral')])
    source=ROOT/a.scene['concept'];target=a.out/(key+'_BaseColor.png');shutil.copyfile(source,target)
    im=bpy.data.images.load(str(target),check_existing=False);im.name=key+'_SourceAlbedo';im.pack()
    for node in a.material.node_tree.nodes:
        if node.type=='TEX_IMAGE' and 'BaseColor' in node.image.name:node.image=im;node.interpolation='Linear'
    period=2.4
    boundary=[(-1.16,-.67),(-.89,-.96),(.77,-1),(1.14,-.62),(1.16,.67),(.84,.98),(-.85,1),(-1.13,.66)] if patch else [(-1.2,-1.2),(1.2,-1.2),(1.2,1.2),(-1.2,1.2)]
    if patch:
        # The prior outline is in Unreal coordinates. FBX flips Y on import;
        # compensate here so the irregular footprint returns to its original side.
        boundary=[(x,-y) for x,y in reversed(boundary)]
    def solid(label,points,bottom,shoulder,top,bevel):
        if area(points)<0:points=list(reversed(points))
        cx=sum(p[0] for p in points)/len(points);cy=sum(p[1] for p in points)/len(points)
        # Contract the shallow top ring; hand traces are simple, star-shaped loops.
        inner=[(cx+(x-cx)*(1-bevel),cy+(y-cy)*(1-bevel)) for x,y in points]
        count=len(points);vs=[(x,y,z) for ring,z in [(points,bottom),(points,shoulder),(inner,top)] for x,y in ring]
        fs=[tuple(reversed(range(count))),tuple(range(count*2,count*3))]
        for r in range(2):
            for j in range(count):
                k=(j+1)%count;fs.append((r*count+j,r*count+k,(r+1)*count+k,(r+1)*count+j))
        me=bpy.data.meshes.new(label);me.from_pydata(vs,[],fs);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(label,me);a.scene.collection.objects.link(ob);ob['part']=label;a.parts.append(ob)
        me.materials.append(a.material);uv=me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            for li in poly.loop_indices:
                p=me.vertices[me.loops[li].vertex_index].co
                if label=='Continuous sandy soil' and abs(poly.normal.z)<.5:
                    # Inferred soil sides sample the source's bare lower-right soil;
                    # varying vertical UV avoids collapsing the full side to a stripe.
                    along=p.x if abs(poly.normal.y)>abs(poly.normal.x) else p.y
                    uv.data[li].uv=(.74+along*.045,.16+p.z*.45)
                else:uv.data[li].uv=(p.x/period+.5,p.y/period+.5)
        return ob
    # The soil volume extends down into terrain; its top remains almost flush.
    solid('Continuous sandy soil',boundary,-.14,-.003,-.002,0)
    traced,pairs=outlines();authored=[]
    for i,outline in enumerate(traced):
        points=[(period*(p[0]/1254-.5),period*(.5-p[1]/1254)) for p in outline]
        if patch:
            for p,q in zip(boundary,boundary[1:]+boundary[:1]):
                normal=(q[1]-p[1],p[0]-q[0]);points=clip(points,normal,sum(p[k]*normal[k] for k in range(2)))
                if not points:break
        if len(points)<3 or abs(area(points))<.00005:continue
        ob=solid('Source paver %03d'%(i+1),points,-.014,.004,.009,.045)
        ob['source_outline_px']=json.dumps(outline);authored.append({'source_stone':i+1,'outline_m':points})
    if patch:
        a.scene['variant_of']='TrailTerrain';a.scene['variant_purpose']='Clipped irregular outline for existing path segments, with the same 240 cm source scale.'
    a.scene['surface_policy']='Unmodified source albedo, hand-traced physical closed pavers, continuous closed soil base. No world remapping.'
    a.scene['inference']='Paver depth (0.9 cm), soil thickness and unseen sides are inferred from a single top view. Outlines are approximate manual traces.'
    a.studio(focus=(0,0,0),location=(2.7,-3.3,4.3),scale=3.8)
    a.scene.render.resolution_x=1200;a.scene.render.resolution_y=1200
    result=a.save()
    (a.review/'source-trace.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'albedo_byte_identical':source.read_bytes()==target.read_bytes(),'source_size_px':list(im.size),'manual_stone_count':len(STONES),'authored_pavers':authored,'touching_trace_pairs_separated':pairs,'boundary_m':boundary,'unreal_boundary_cm':[[x*100,-y*100] for x,y in boundary],'source_period_cm':240,'paver_top_cm':.9,'soil_top_cm':-.2,'inferred_depth':True,'fidelity_accepted':False,'automatic_chroma_trace_rejected':'Merged neighboring stones and missed dimmer stones.'},indent=2))
    return result

if __name__=='__main__':result=build()
