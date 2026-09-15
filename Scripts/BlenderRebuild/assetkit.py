"""Small Blender authoring helpers; asset geometry stays in individual recipes."""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/hello/Projects/Terrarium')

class Asset:
    def __init__(self,key,source,palette):
        assert Path(bpy.context.scene.get('terrarium_project',''))==ROOT
        self.key=key;self.palette=palette;self.parts=[]
        self.out=ROOT/'SourceAssets/Blender'/key;self.out.mkdir(parents=True,exist_ok=True)
        self.review=ROOT/'Docs/BlenderRebuild'/key;self.review.mkdir(parents=True,exist_ok=True)
        name='Terrarium_'+key
        old=bpy.data.scenes.get(name)
        if old:
            assert Path(old.get('terrarium_project',''))==ROOT and old.get('asset_name')==key
        # A normally opened asset can be Blender's only scene. Create and
        # activate its replacement before removing the old authored scene.
        self.scene=bpy.data.scenes.new(name);bpy.context.window.scene=self.scene
        self.scene['terrarium_project']=str(ROOT);self.scene['asset_name']=key
        if old:
            # Batch removal avoids a dependency-graph rebuild for every tiny part.
            bpy.data.batch_remove(ids=list(old.objects))
            bpy.data.scenes.remove(old)
        self.scene.name=name
        self.scene['terrarium_project']=str(ROOT);self.scene['asset_name']=key;self.scene['concept']='SourceAssets/Voxel/'+source
        self.scene['fidelity_status']='authored_pending_visual_review'
        self.scene.unit_settings.system='METRIC'
        self.make_material()

    def make_material(self):
        size=512;cell=64;rng=random.Random(76)
        images=[]
        # Albedo contains broad wood grain blocks and restrained mineral variation.
        for kind in ['BaseColor','Emission','Roughness']:
            im=bpy.data.images.new(self.key+'_'+kind,width=size,height=size,alpha=False)
            px=[]
            for y in range(size):
                for x in range(size):
                    idx=min(y//cell*8+x//cell,len(self.palette)-1)
                    entry=self.palette[idx];rgb=[int(entry[0][i:i+2],16)/255 for i in [0,2,4]]
                    typ=entry[1];u=(x%cell)/cell;v=(y%cell)/cell
                    if kind=='BaseColor':
                        f=1
                        if typ=='wood':f=.92+.06*math.sin((int(u*7)+2)*13.7)+.045*math.sin((int(v*9)+int(u*7)*3)*9.1)
                        elif typ=='bridgewood':f=.87+.075*math.sin(int(v*6)*13.7)+.055*math.sin((int(u*9)+int(v*6)*3)*9.1)
                        elif typ in ['timber','clay']:f=.98+.015*math.sin(int(u*3)*13.2+int(v*3)*7.1)
                        elif typ=='foliage':
                            fu=u*3;fv=v*3;tri=int(fu%1+fv%1>1)
                            f=.75+.30*(.5+.5*math.sin(int(fu)*17.1+int(fv)*8.3+tri*5.7+idx))
                        elif typ=='canopy':
                            fu=u*3;fv=v*3
                            tri=int(fu%1+fv%1>1)
                            f=.86+.14*math.sin(math.floor(fu)*17.1+math.floor(fv)*8.3+tri*5.7+idx)+.012*math.sin(u*31+v*19)
                        elif typ=='bankleaf':f=.94+(.07 if u+v>1 else 0)+.016*math.sin(int(u*2)*7+int(v*2)*11+idx)
                        elif typ=='mineral':f=.96+.025*math.sin(int(u*4)*11.7+int(v*4)*6.3)+.012*math.sin(u*17-v*11)
                        elif typ=='endgrain':f=.80+.16*(int(max(abs(u-.5),abs(v-.5))*15)%2)
                        elif typ=='pane':
                            qu=(int(u*6)+.5)/6;qv=(int(v*8)+.5)/8
                            weight=max(0,1-max(abs(qu-.5)*2,abs(qv-.46)*1.7))**1.3
                            rgb=[rgb[i]*(1-weight)+[1,.94,.67][i]*weight for i in range(3)]
                        else:f=.93+.065*math.sin(int(u*4)*13.2+int(v*5)*7.1)
                        rgb=[min(1,c*f) for c in rgb]
                    elif kind=='Emission':
                        if typ=='pane':
                            qu=(int(u*6)+.5)/6;qv=(int(v*8)+.5)/8
                            weight=max(0,1-max(abs(qu-.5)*2,abs(qv-.46)*1.7))**1.3
                            rgb=[rgb[i]*(1-weight)+[1,.94,.67][i]*weight for i in range(3)]
                        else:rgb=[0,0,0]
                    else:rgb=[.55 if typ=='metal' else .8]*3
                    px.extend(rgb+[1])
            im.pixels.foreach_set(px);im.filepath_raw=str(self.out/(self.key+'_'+kind+'.png'));im.file_format='PNG';im.save();im.pack();images.append(im)
        mat=bpy.data.materials.new('M_'+self.key);mat.use_nodes=True;self.material=mat
        nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Specular IOR Level'].default_value=.25
        for image,input_name in zip(images,['Base Color','Emission Color','Roughness']):
            tx=nt.nodes.new('ShaderNodeTexImage');tx.image=image
            if input_name=='Roughness':image.colorspace_settings.name='Non-Color'
            nt.links.new(tx.outputs['Color'],bs.inputs[input_name])
        bs.inputs['Emission Strength'].default_value=1.7

    def box(self,label,p,size,index,bevel=.006,rotation=(0,0,0),top_index=None):
        w,d,h=[v/2 for v in size]
        vs=[(-w,-d,-h),(w,-d,-h),(w,d,-h),(-w,d,-h),(-w,-d,h),(w,-d,h),(w,d,h),(-w,d,h)]
        fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        mesh=bpy.data.meshes.new(label);mesh.from_pydata(vs,[],fs);mesh.update()
        ob=bpy.data.objects.new(label,mesh);self.scene.collection.objects.link(ob);ob.location=p;ob.rotation_euler=[math.radians(v) for v in rotation]
        mesh.materials.append(self.material);uv=mesh.uv_layers.new(name='UVMap')
        for poly in mesh.polygons:
            i=top_index if poly.index==1 and top_index is not None else index
            for li,(u,v) in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=((i%8)/8+.006+u*.113,(i//8)/8+.006+v*.113)
        if bevel:
            m=ob.modifiers.new('Crafted bevel','BEVEL');m.width=min(bevel,min(size)*.1);m.segments=2
            m=ob.modifiers.new('Face normals','WEIGHTED_NORMAL');m.keep_sharp=True
        ob['part']=label;self.parts.append(ob);return ob

    def studio(self,focus,location,scale):
        s=self.scene
        for name,pos,power,sz,color in [('Key',(-3,-5,7),650,4,(1,.90,.78)),('Fill',(4,-1,5),300,4,(.80,.91,1)),('Rim',(0,4,6),400,3,(1,.97,.89))]:
            light=bpy.data.lights.new(name,'AREA');light.energy=power;light.size=sz;light.color=color
            ob=bpy.data.objects.new(name,light);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(focus)-ob.location).to_track_quat('-Z','Y').to_euler()
        world=bpy.data.worlds.new(self.key+' studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.23,.26,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=world
        data=bpy.data.cameras.new('Reference camera');cam=bpy.data.objects.new('Reference camera',data);s.collection.objects.link(cam);cam.location=location;cam.rotation_euler=(Vector(focus)-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;s.camera=cam
        s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
        s.render.resolution_x=900;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.film_transparent=True
        s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.3
        s.render.image_settings.file_format='PNG';s.render.filepath=str(self.review/'front.png')
        for o in s.objects:o.select_set(False)
        for o in self.parts:o.select_set(True)
        bpy.context.view_layer.objects.active=self.parts[0];bpy.context.view_layer.update()

    def save(self):
        # Only this asset's scene and referenced data enter its authoring file.
        bpy.data.libraries.write(str(self.out/(self.key+'.blend')),{self.scene},path_remap='RELATIVE',fake_user=True,compress=True)
        r={'asset':self.key,'scene':self.scene.name,'parts':len(self.parts),'source':self.scene['concept'],'status':'authored_pending_visual_review'}
        (self.review/'build.json').write_text(json.dumps(r,indent=2));return r
