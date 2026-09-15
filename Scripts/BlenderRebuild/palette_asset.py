"""Linear-color packed atlases and closed-mesh helpers for physical item assets."""
import bpy,bmesh,math
from assetkit import Asset

def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4

class PaletteAsset(Asset):
    def make_material(self):
        self.images=[]
        for kind in ['BaseColor','Emission','Roughness']:
            im=bpy.data.images.new(self.key+'_'+kind,width=512,height=512,alpha=False,float_buffer=True)
            if kind=='Roughness':im.colorspace_settings.name='Non-Color'
            px=[]
            for y in range(512):
                for x in range(512):
                    idx=min(y//64*8+x//64,len(self.palette)-1);hx,rough,emissive=self.palette[idx]
                    rgb=[int(hx[j:j+2],16)/255 for j in [0,2,4]]
                    variation=1+.014*math.sin((x%64//16)*9+(y%64//16)*17+idx*4)
                    if kind=='BaseColor':rgb=[linear(min(1,c*variation)) for c in rgb]
                    elif kind=='Emission':rgb=[linear(c)*emissive for c in rgb]
                    else:rgb=[rough]*3
                    px.extend(rgb+[1])
            im.pixels.foreach_set(px);im.filepath_raw=str(self.out/(self.key+'_'+kind+'.png'));im.file_format='PNG';im.save();im.pack();self.images.append(im)
        self.material=self.shader('Frame',metallic=.82)

    def shader(self,role,metallic=0,transmission=0,ior=1.45,emission=0):
        mat=bpy.data.materials.new('M_'+self.key+'_'+role);mat.use_nodes=True
        nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
        bs.inputs['Metallic'].default_value=metallic;bs.inputs['Transmission Weight'].default_value=transmission;bs.inputs['IOR'].default_value=ior;bs.inputs['Emission Strength'].default_value=emission
        for im,pin in zip(self.images,['Base Color','Emission Color','Roughness']):
            node=nt.nodes.new('ShaderNodeTexImage');node.image=im;nt.links.new(node.outputs['Color'],bs.inputs[pin])
        return mat

    def solid(self,label,verts,faces,index,material=None,bevel=.0015,face_indices=None):
        me=bpy.data.meshes.new(label);me.from_pydata(verts,[],faces);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        me.materials.append(material or self.material);uv=me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            cell=face_indices[poly.index] if face_indices is not None else index
            ax=max(range(3),key=lambda j:abs(poly.normal[j]));axes=[j for j in range(3) if j!=ax]
            coords=[me.vertices[me.loops[li].vertex_index].co for li in poly.loop_indices]
            lo=[min(v[a] for v in coords) for a in axes];hi=[max(v[a] for v in coords) for a in axes]
            for li,v in zip(poly.loop_indices,coords):uv.data[li].uv=tuple((cell%8 if j==0 else cell//8)/8+.006+.113*(v[a]-lo[j])/max(hi[j]-lo[j],1e-6) for j,a in enumerate(axes))
        ob=bpy.data.objects.new(label,me);self.scene.collection.objects.link(ob);ob['part']=label;self.parts.append(ob)
        if bevel:
            mod=ob.modifiers.new('Polished facet edges','BEVEL');mod.width=bevel;mod.segments=2
            mod=ob.modifiers.new('Facet normals','WEIGHTED_NORMAL');mod.keep_sharp=True
        return ob
