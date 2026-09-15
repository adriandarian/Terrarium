"""Trace the supplied six-course cliff texture as individual solid stone reliefs."""
import sys,json,shutil,hashlib
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import bpy,bmesh
from assetkit import Asset,ROOT
a=Asset('CliffFace','terrain_cliff_face_v7.png',[('56543b','mineral')])
source=ROOT/a.scene['concept'];target=a.out/'CliffFace_BaseColor.png'
shutil.copyfile(source,target)
im=bpy.data.images.load(str(target),check_existing=False);im.name='CliffFace_SourceAlbedo';im.pack()
for node in a.material.node_tree.nodes:
    if node.type=='TEX_IMAGE' and 'BaseColor' in node.image.name:
        node.image=im;node.interpolation='Linear'
# Pixel-space outlines follow the visible joints, including split small stones.
# Coordinates are observations of this source, not randomized masonry courses.
rects=[
 (0,0,207,211),(215,0,469,129),(217,137,326,212),(334,137,469,212),
 (480,0,697,212),(708,0,830,63),(708,75,830,149),(708,158,830,211),
 (843,0,1106,211),(1116,0,1220,128),(1116,136,1220,211),(1232,0,1254,211),
 (0,225,90,444),(103,225,610,444),(625,225,729,342),(740,225,991,342),
 (625,354,801,445),(812,354,932,445),(944,354,991,445),(1004,225,1254,445),
 (0,458,310,644),(322,458,440,546),(322,556,440,644),(451,458,824,644),
 (838,458,1194,644),(1207,458,1254,644),
 (0,658,133,830),(146,658,601,830),(615,658,750,830),(762,658,1008,830),(1022,658,1254,830),
 (0,845,354,1047),(368,845,557,940),(368,952,557,1047),(570,845,754,1047),
 (769,845,913,940),(769,952,913,1047),(927,845,1236,1047),(1246,845,1254,1047),
 (0,1062,111,1241),(124,1062,178,1132),(124,1142,178,1241),(192,1062,535,1241),
 (549,1062,717,1145),(549,1157,717,1241),(731,1062,878,1241),(892,1062,1254,1241),
]
def outline(rect,inset=0):
    x0,y0,x1,y1=rect;x0+=inset;y0+=inset;x1-=inset;y1-=inset
    c=min(11,(x1-x0)*.15,(y1-y0)*.15)
    return [(x0+c,y1),(x1-c,y1),(x1,y1-c),(x1,y0+c),(x1-c,y0),(x0+c,y0),(x0,y0+c),(x0,y1-c)]
def solid(label,vs,fs):
    me=bpy.data.meshes.new(label);me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(label,me);a.scene.collection.objects.link(ob);ob['part']=label;a.parts.append(ob)
    me.materials.append(a.material);uv=me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        for li in poly.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=((v.x+1)/2,v.z/2)
    return ob
# An actual supporting volume closes all joints and the inferred back.
core=a.box('Continuous stone backing',(0,.0485,1),(2,.103,2),0,bevel=0)
for poly in core.data.polygons:
    for li in poly.loop_indices:
        # Use the known local translation before dependency-graph evaluation.
        v=core.data.vertices[core.data.loops[li].vertex_index].co+core.location
        core.data.uv_layers.active.data[li].uv=((v.x+1)/2,v.z/2)
for i,rect in enumerate(rects):
    width=rect[2]-rect[0];height=rect[3]-rect[1]
    inset=min(5,width*.08,height*.08)
    front=-.016-.008*((i*7)%5)/4
    rings=[(outline(rect),.030),(outline(rect),front+.007),(outline(rect,inset),front)]
    vs=[(2*x/1254-1,y,2*(1-py/1254)) for points,y in rings for x,py in points]
    fs=[tuple(reversed(range(8))),tuple(range(16,24))]
    for r in [0,1]:
        for j in range(8):
            k=(j+1)%8;fs.append((r*8+j,r*8+k,(r+1)*8+k,(r+1)*8+j))
    ob=solid('Traced cliff stone %02d'%(i+1),vs,fs);ob['source_rectangle_px']=list(rect)
a.scene['surface_policy']='Individual closed stones traced from visible source joints; colors use the unmodified full PNG.'
a.scene['inference']='Depth, unseen back and beveled edge profile are inferred from one flat reference.'
a.studio(focus=(0,.04,1),location=(2,-5,2.6),scale=2.7)
a.scene.render.resolution_x=1200;a.scene.render.resolution_y=1200
result=a.save()
(a.review/'source-trace.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'albedo_byte_identical':source.read_bytes()==target.read_bytes(),'source_size_px':list(im.size),'stone_rectangles_px':rects,'stone_count':len(rects),'nominal_face_m':[2,2],'depth_inferred':True,'unseen_back_inferred':True,'fidelity_accepted':False},indent=2))
