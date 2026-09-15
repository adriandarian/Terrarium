"""Four-sided placement module made from the traced CliffFace stone layout."""
import sys,math,json,shutil
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import bpy,bmesh
from assetkit import Asset,ROOT
a=Asset('CliffColumn','terrain_cliff_face_v7.png',[('56543b','mineral')])
a.scene['variant_of']='CliffFace';a.scene['variant_purpose']='Four-sided 100 x 100 x 323.5 cm terrain module with clipped/repeated traced stone courses and a source-grass cap.'
shutil.copyfile(a.out/'CliffColumn_SourceAtlas.png',a.out/'CliffColumn_BaseColor.png')
im=bpy.data.images.load(str(a.out/'CliffColumn_BaseColor.png'),check_existing=False);im.name='CliffColumn_SourceAlbedo';im.pack()
for node in a.material.node_tree.nodes:
    if node.type=='TEX_IMAGE' and 'BaseColor' in node.image.name:node.image=im
rects=json.loads((ROOT/'Docs/BlenderRebuild/CliffFace/source-trace.json').read_text())['stone_rectangles_px']
def outline(rect,inset=0):
    x0,y0,x1,y1=rect;x0+=inset;y0+=inset;x1-=inset;y1-=inset
    c=min(8,(x1-x0)*.15,(y1-y0)*.15)
    return [(x0+c,y1),(x1-c,y1),(x1,y1-c),(x1,y0+c),(x1-c,y0),(x0+c,y0),(x0,y0+c),(x0,y1-c)]
count=0
for side in range(4):
    angle=side*math.pi/2;cs=round(math.cos(angle));sn=round(math.sin(angle));offset=(side%2)*627
    for repeat in range(2):
        # Crop the upper repeat at the underside of the grass cap.
        ylow=max(0,(1-(3.20-repeat*2)/2)*1254)
        for i,r in enumerate(rects):
            clipped=[max(r[0],offset),max(r[1],ylow),min(r[2],offset+627),r[3]]
            width=clipped[2]-clipped[0];height=clipped[3]-clipped[1]
            if width<3 or height<3:continue
            inset=min(4,width*.08,height*.08);front=-.494+.006*((i*7)%5)/4
            rings=[(outline(clipped),-.450),(outline(clipped),front+.007),(outline(clipped,inset),front)]
            vs=[];source_uv=[]
            for points,y in rings:
                for px,py in points:
                    x=(px-offset)/627-.5;z=2*(1-py/1254)+2*repeat
                    vs.append((x*cs-y*sn,x*sn+y*cs,z));source_uv.append((px/2508,1-py/1254))
            fs=[tuple(reversed(range(8))),tuple(range(16,24))]
            for ring in [0,1]:
                for j in range(8):
                    k=(j+1)%8;fs.append((ring*8+j,ring*8+k,(ring+1)*8+k,(ring+1)*8+j))
            label='Cliff side %d course %d stone %02d'%(side,repeat,i)
            me=bpy.data.meshes.new(label);me.from_pydata(vs,[],fs);me.update()
            bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
            ob=bpy.data.objects.new(label,me);a.scene.collection.objects.link(ob);ob['part']=label;a.parts.append(ob);me.materials.append(a.material)
            uv=me.uv_layers.new(name='UVMap')
            for p in me.polygons:
                for li in p.loop_indices:uv.data[li].uv=source_uv[me.loops[li].vertex_index]
            count+=1
core=a.box('Solid cliff core',(0,0,1.60),(.95,.95,3.20),0,bevel=0)
for p in core.data.polygons:
    for li in p.loop_indices:
        v=core.data.vertices[core.data.loops[li].vertex_index].co+core.location
        u=(v.x+1)/2 if abs(p.normal.y)>.5 else (v.y+1)/2
        core.data.uv_layers.active.data[li].uv=(u*.5,(v.z/2)%1)
cap=a.box('Source grass cap',(0,0,3.2175),(1,1,.035),0,bevel=0)
for p in cap.data.polygons:
    for li in p.loop_indices:
        v=cap.data.vertices[cap.data.loops[li].vertex_index].co+cap.location
        cap.data.uv_layers.active.data[li].uv=(.5+(v.x/2+.5)*.5,v.y/2+.5)
a.scene['additional_concept']='SourceAssets/Voxel/terrain_grass_top_v9.png'
a.scene['stone_count']=count;a.scene['nominal_bounds_m']=[1,1,3.235]
a.studio(focus=(0,0,1.6),location=(3,-5,3.8),scale=3.9)
a.scene.render.resolution_x=1000;a.scene.render.resolution_y=1200
result=a.save()
