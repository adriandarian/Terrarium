"""Small original modeling primitives, baked by Unreal Geometry Script.

Each asset owns its own recipe. Every component is a closed outward convex solid;
the mesh is tested before and after its StaticMesh round trip.
"""
import unreal
import math
import random
import json
from pathlib import Path
from collections import Counter

ROOT='/Game/Terrarium'
COLORS={
 'stone':'8d8268','stone_light':'aba082','stone_dark':'695f4b',
 'plaster':'d4bd8b','wood':'67452a','wood_light':'977043','wood_dark':'423123',
 'roof':'a6532d','roof_light':'bf6b38','roof_dark':'753c27',
 'teal':'327978','teal_light':'49958c','teal_dark':'255451',
 'moss':'70793a','grass':'7f8845','grass_light':'939b50','soil':'675339',
 'leaf':'677a34','leaf_light':'88953e','leaf_dark':'3d542b',
 'wheat':'c4a349','wheat_light':'dcc16a','stalk':'8e7a37',
 'water':'276f76','water_light':'408b8d','water_dark':'235861',
 'path':'b69b67','path_light':'c6b17d','crop':'49733c','crop_light':'729545',
 'fruit':'ad632f','dark':'282820','metal':'4b4940'}

def color(key,factor=1):
    h=COLORS.get(key,key)
    rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(max(.003,min(1,((v+.055)/1.055)**2.4*factor)) for v in rgb)

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(v):return mul(v,1/math.sqrt(dot(v,v)))
def rotate(v,rot):
    x,y,z=v
    for axis,angle in enumerate(rot):
        c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
        if axis==0:y,z=y*c-z*s,y*s+z*c
        elif axis==1:x,z=x*c+z*s,-x*s+z*c
        else:x,y=x*c-y*s,x*s+y*c
    return (x,y,z)

class Mesh:
    def __init__(self,name,seed=1):
        self.name=name;self.rng=random.Random(seed)
        self.vertices=[];self.triangles=[];self.colors=[];self.parts=[]

    def solid(self,vertices,faces,key,rot=(0,0,0),pos=(0,0,0),variation=.035):
        vs=[add(rotate(v,rot),pos) for v in vertices]
        center=mul(tuple(map(sum,zip(*vs))),1/len(vs))
        offset=len(self.vertices)
        self.vertices+=vs
        self.colors += [color(key,self.rng.uniform(1-variation,1+variation))]*len(vs)
        start=len(self.triangles);volume=0
        for face in faces:
            face=list(face)
            a,b,c=(vs[i] for i in face[:3])
            n=cross(sub(b,a),sub(c,a))
            assert dot(n,n)>1e-10,(self.name,'degenerate face')
            if dot(n,sub(a,center))<0:face.reverse()
            for i in range(1,len(face)-1):
                local=(face[0],face[i],face[i+1])
                a,b,c=(vs[k] for k in local)
                n=cross(sub(b,a),sub(c,a))
                assert dot(n,sub(mul(add(add(a,b),c),1/3),center))>0,(self.name,'inward')
                volume+=dot(sub(a,center),cross(sub(b,center),sub(c,center)))/6
                self.triangles.append(tuple(offset+k for k in local))
        edges=Counter(tuple(sorted((tri[i],tri[(i+1)%3]))) for tri in self.triangles[start:] for i in range(3))
        assert all(n==2 for n in edges.values()),(self.name,'open component')
        assert volume>0
        self.parts.append({'first':start,'end':len(self.triangles),'center':center,'volume':volume})

    def box(self,pos,size,key,bevel=3,rot=(0,0,0),variation=.035):
        h=[s/2 for s in size];b=min(bevel,min(h)*.4)
        verts=[];lookup={}
        # Three inset coordinate pairs meet each original cube corner.
        for axis in range(3):
            for sx in (-1,1):
                for sy in (-1,1):
                    for sz in (-1,1):
                        signs=(sx,sy,sz)
                        v=tuple(signs[j]*(h[j] if j==axis else h[j]-b) for j in range(3))
                        lookup[(axis,signs)]=len(verts);verts.append(v)
        faces=[]
        for axis in range(3):
            other=[j for j in range(3) if j!=axis]
            for sign in (-1,1):
                face=[]
                for a,c in [(-1,-1),(1,-1),(1,1),(-1,1)]:
                    s=[0,0,0];s[axis]=sign;s[other[0]]=a;s[other[1]]=c
                    face.append(lookup[(axis,tuple(s))])
                faces.append(face)
        for a,c in [(0,1),(0,2),(1,2)]:
            other=3-a-c
            for sa in (-1,1):
                for sc in (-1,1):
                    p=[0,0,0];p[a]=sa;p[c]=sc;p[other]=-1
                    q=p.copy();q[other]=1
                    faces.append([lookup[(a,tuple(p))],lookup[(a,tuple(q))],lookup[(c,tuple(q))],lookup[(c,tuple(p))]])
        for sx in (-1,1):
            for sy in (-1,1):
                for sz in (-1,1):faces.append([lookup[(a,(sx,sy,sz))] for a in range(3)])
        self.solid(verts,faces,key,rot,pos,variation)

    def ellipsoid(self,pos,size,key,segments=7,rings=4,rot=(0,0,0)):
        verts=[(0,0,-size[2]/2)]
        for r in range(1,rings):
            phi=-math.pi/2+math.pi*r/rings
            for s in range(segments):
                a=2*math.pi*s/segments
                verts.append((size[0]/2*math.cos(phi)*math.cos(a),size[1]/2*math.cos(phi)*math.sin(a),size[2]/2*math.sin(phi)))
        top=len(verts);verts.append((0,0,size[2]/2));faces=[]
        for s in range(segments):
            n=(s+1)%segments
            faces.append([0,1+n,1+s])
            for r in range(rings-2):
                a=1+r*segments
                faces.append([a+s,a+n,a+segments+n,a+segments+s])
            a=1+(rings-2)*segments
            faces.append([top,a+s,a+n])
        self.solid(verts,faces,key,rot,pos,.065)

    def beam(self,start,end,width,key,depth=None):
        direction=norm(sub(end,start));center=mul(add(start,end),.5)
        length=math.sqrt(dot(sub(end,start),sub(end,start)))
        yaw=math.degrees(math.atan2(direction[1],direction[0]))
        pitch=-math.degrees(math.asin(direction[2]))
        self.box(center,(length,width,depth or width),key,min(width*.15,3),rot=(0,pitch,yaw))

    def gable(self,pos,width,depth,height,key):
        vs=[(-width/2,-depth/2,0),(width/2,-depth/2,0),(0,-depth/2,height),(-width/2,depth/2,0),(width/2,depth/2,0),(0,depth/2,height)]
        self.solid(vs,[[0,2,1],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],key,pos=pos)

    def save(self):
        assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
        out=ROOT+'/Meshes/'+self.name
        assert not unreal.EditorAssetLibrary.does_asset_exist(out),'Inspect existing asset before replacing'
        d=unreal.DynamicMesh()
        buf=unreal.GeometryScriptSimpleMeshBuffers()
        buf.vertices=[unreal.Vector(*v) for v in self.vertices]
        # Unreal Geometry Script's face-normal convention uses clockwise
        # triangles. Convert our outward cross-product construction explicitly.
        buf.triangles=[unreal.IntVector(t[0],t[2],t[1]) for t in self.triangles]
        alphas=getattr(self,'vertex_alphas',None)
        assert alphas is None or len(alphas)==len(self.colors)
        buf.vertex_colors=[unreal.LinearColor(*c,alphas[i] if alphas is not None else 1) for i,c in enumerate(self.colors)]
        buf.uv0=[unreal.Vector2D(v[0]/100,v[1]/100) for v in self.vertices]
        d.append_buffers_to_mesh(buf)
        unreal.GeometryScript_Normals.set_per_face_normals(d)
        assert unreal.GeometryScript_MeshQueries.get_is_closed_mesh(d)
        # Verify every face against the center of its own closed component.
        worst=1
        for part in self.parts:
            for i in range(part['first'],part['end']):
                n,valid=d.get_triangle_face_normal(i)
                assert valid
                a,b,c=[self.vertices[k] for k in self.triangles[i]]
                expected=norm(cross(sub(b,a),sub(c,a)))
                alignment=dot((n.x,n.y,n.z),expected)
                worst=min(worst,alignment)
                assert alignment>.999,'Geometry Script face winding mismatch'
        opts=unreal.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=False,enable_recompute_normals=False,enable_recompute_tangents=False)
        sm,outcome=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(d,out,opts)
        assert sm and outcome==unreal.GeometryScriptOutcomePins.SUCCESS
        sm.set_material(0,vertex_material())
        unreal.EditorAssetLibrary.save_loaded_asset(sm)
        check=unreal.DynamicMesh()
        _,outcome=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(sm,check,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD())
        assert outcome==unreal.GeometryScriptOutcomePins.SUCCESS
        assert check.get_triangle_count()==len(self.triangles)
        # Round-trip source data may split vertices at color/normal seams; normal
        # agreement is checked on the actual saved triangle positions.
        invalid=0
        for i in range(check.get_triangle_count()):
            valid,a,b,c=check.get_triangle_positions(i)
            face=norm(cross(sub((c.x,c.y,c.z),(a.x,a.y,a.z)),sub((b.x,b.y,b.z),(a.x,a.y,a.z))))
            _,n1,n2,n3,validnormals=check.get_triangle_normals(i)
            if not valid or not validnormals or any(dot(face,(n.x,n.y,n.z))<.99 for n in [n1,n2,n3]):invalid+=1
        assert invalid==0,(self.name,'saved normal errors',invalid)
        report={'asset':out,'triangles':len(self.triangles),'vertices':len(self.vertices),'closed_components':len(self.parts),
            'all_components_closed':True,'all_component_volumes_positive':True,'geometry_script_closed':True,
            'minimum_normal_alignment':worst,'saved_normal_errors':invalid,'refinement_pass':getattr(self,'refinement_pass',1),'visual_review':'pending'}
        if hasattr(self,'revises'):report['revises']=self.revises
        p=Path(unreal.Paths.project_dir(),'Docs/Phase1/Validation');p.mkdir(parents=True,exist_ok=True)
        (p/(self.name+'.json')).write_text(json.dumps(report,indent=2))
        unreal.log('ASSET_VALIDATED '+self.name)
        return sm

def vertex_material():
    path=ROOT+'/Materials/M_SculptedPalette'
    if unreal.EditorAssetLibrary.does_asset_exist(path):return unreal.load_asset(path)
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_SculptedPalette',ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib=unreal.MaterialEditingLibrary
    node=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-300,0)
    assert lib.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,v,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.93,150),(unreal.MaterialProperty.MP_SPECULAR,.1,260)]:
        node=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,y);node.set_editor_property('r',v)
        lib.connect_material_property(node,'',prop)
    lib.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
