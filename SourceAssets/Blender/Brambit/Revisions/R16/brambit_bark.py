"""Solid bark regions that follow the actual stepped body envelope."""
import bpy
from box_union import box_union


def make_patch(a,label,regions,index):
    cells=[]
    for lo,hi in regions:
        if any(hi[i]-lo[i]<1e-6 for i in range(3)):continue
        ob=a.box(label+' cell',[(lo[i]+hi[i])/2 for i in range(3)],[hi[i]-lo[i] for i in range(3)],index,bevel=0)
        ob['palette_index']=index;cells.append(ob)
    assert cells,label
    joined=box_union(label,cells,a.scene,a.material)
    for ob in cells:a.parts.remove(ob)
    bpy.data.batch_remove(ids=cells)
    joined['part']=label;joined['palette_index']=index
    joined['surface_following_bark']=True;joined['envelope_cells']=len(regions)
    a.parts.append(joined)
    return joined


def side_patch(a,xc,side,y,z,width,height,index,sections,profile,surface):
    ymin,ymax=y-width/2,y+width/2;zmin,zmax=z-height/2,z+height/2
    ys=sorted({ymin,ymax}|{v for near,far,_,_ in sections for v in (near,far) if ymin<v<ymax})
    zs=sorted({zmin,zmax}|{.42+(v-.42)*sz for _,_,_,sz in sections for _,v in profile if zmin<.42+(v-.42)*sz<zmax})
    relief=.002+.001*(index==1);regions=[]
    for ya,yb in zip(ys,ys[1:]):
        for za,zb in zip(zs,zs[1:]):
            half=surface((ya+yb)/2,(za+zb)/2)
            if not half:continue
            outer=xc+side*(half+relief)
            regions.append(((min(xc,outer),ya,za),(max(xc,outer),yb,zb)))
    ob=make_patch(a,'Broad side bark',regions,index)
    ob['bark_side']=side;ob['bark_relief_m']=relief
    return ob


def rear_patch(a,xc,x,z,width,height,index,sections,profile,surface):
    xmin,xmax=x-width/2,x+width/2;zmin,zmax=z-height/2,z+height/2
    xs=sorted({xmin,xmax}|{v*sx for _,_,sx,_ in sections for v,_ in profile if xmin<v*sx<xmax})
    zs=sorted({zmin,zmax}|{.42+(v-.42)*sz for _,_,_,sz in sections for _,v in profile if zmin<.42+(v-.42)*sz<zmax})
    relief=.0025;regions=[]
    for xa,xb in zip(xs,xs[1:]):
        for za,zb in zip(zs,zs[1:]):
            back=surface((xa+xb)/2,(za+zb)/2)
            if not back:continue
            regions.append(((xc+xa,-.20,za),(xc+xb,back+relief,zb)))
    ob=make_patch(a,'Broad back bark',regions,index);ob['bark_relief_m']=relief
    return ob


def dissolve_line_faces(bm):
    """Merge nanometre-width Boolean faces into an adjacent full surface."""
    import bmesh
    def thin(face):
        return sum(max(v.co[i] for v in face.verts)-min(v.co[i] for v in face.verts)<1e-7 for i in range(3))>=2
    bad=[face for face in bm.faces if thin(face)];edges=[]
    for face in bad:
        candidates=[edge for edge in face.edges if len(edge.link_faces)==2 and any(not thin(other) for other in edge.link_faces)]
        assert candidates,'No full neighboring surface for Boolean line face'
        edges.append(max(candidates,key=lambda edge:edge.calc_length()))
    if edges:bmesh.ops.dissolve_edges(bm,edges=list(set(edges)),use_verts=False,use_face_split=False)
    assert not any(thin(face) for face in bm.faces)
    return len(bad)
