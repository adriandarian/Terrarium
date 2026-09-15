"""A source-style timber transition fitted to the measured south bridge joint.

Dimensions below are site adaptations; the ten-plank canonical bridge is intact.
X is across the bridge, Blender Y points toward the bank (FBX flips Y).
Place at bridge along-offset -371 cm, Z=280 cm, with bridge yaw and unit scale.
"""
import bpy,bmesh,json,shutil,sys,hashlib,math
from pathlib import Path
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
from assetkit import Asset,ROOT
from mathutils import Vector
a=Asset('BridgeThreshold','river_crossing.png',[('836022','bridgewood')])
source_folder=ROOT/'SourceAssets/Blender/RiverBridge';copied={}
for kind in ['BaseColor','Emission','Roughness']:
    source=source_folder/('RiverBridge_'+kind+'.png');target=a.out/('BridgeThreshold_'+kind+'.png');shutil.copyfile(source,target)
    image=bpy.data.images.load(str(target),check_existing=False);image.name='BridgeThreshold_'+kind
    if kind=='Roughness':image.colorspace_settings.name='Non-Color'
    image.pack()
    for n in a.material.node_tree.nodes:
        if n.type=='TEX_IMAGE' and kind in n.image.name:n.image=image
    copied[kind]={'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'byte_identical':source.read_bytes()==target.read_bytes()}

# Local Y=+0.39 is along=-410 at the bank; -0.39 is along=-332 at the deck.
def top(y):return .005+(.068-.005)*min(1,max(0,(y+.39)/.20))
def left(y):return -.8+(.8)*(y+.39)/.78
def right(y):return 1.0
def wood_piece(label,coords,index=0,bevel=.003):
    # coords is four ordered top corners with four matching lower corners.
    vs=coords;fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(label);me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(label,me);a.scene.collection.objects.link(ob);ob['part']=label;a.parts.append(ob)
    me.materials.append(a.material);uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        for li,(u,v) in zip(p.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=((index%8)/8+.006+u*.113,(index//8)/8+.006+v*.113)
    if bevel:
        m=ob.modifiers.new('Soft timber corners','BEVEL');m.width=bevel;m.segments=2
        n=ob.modifiers.new('Timber face normals','WEIGHTED_NORMAL');n.keep_sharp=True
    return ob

planks=[]
for i,(y0,y1) in enumerate([(-.39,-.19),(-.19,.10),(.10,.39)]):
    footprint=[(left(y0),y0),(right(y0),y0),(right(y1),y1),(left(y1),y1)]
    vs=[(x,y,top(y)+z) for z in [-.12,0] for x,y in footprint]
    ob=wood_piece('Threshold plank %d'%(i+1),vs,[0,1,0][i]);planks.append({'name':ob.name,'footprint_m':footprint})
    # Flush square-headed fasteners match the two-fastener motif on the bridge.
    for side in [.19,.81]:
        y=(y0+y1)/2;x=left(y)+(right(y)-left(y))*side
        nail=a.box('Threshold iron fastening',(x,y,top(y)+.001),(.025,.038,.004),4,bevel=.0007)
        # First plank follows the ramp; the other two lie on the bank plateau.
        if i==0:nail.rotation_euler.x=math.atan((.068-.005)/.20)

# Two skewed runners bear in the solid bank at the far end and onto a
# transverse beam that intersects the bridge's existing longitudinal beams.
for runner,(xb,xd) in enumerate([(.26,-.53),(.84,.74)]):
    def center(y):return xd+(xb-xd)*(y+.43)/.86
    for segment,(y0,y1) in enumerate([(-.43,-.19),(-.19,.43)]):
        footprint=[(center(y0)-.065,y0),(center(y0)+.065,y0),(center(y1)+.065,y1),(center(y1)-.065,y1)]
        vs=[(x,y,top(y)+z) for z in [-.26,-.118] for x,y in footprint]
        wood_piece('Bearing runner %d segment %d'%(runner+1,segment+1),vs,2,.002)
a.box('Bridge beam bearing crosspiece',(0,-.37,-.205),(2.34,.23,.15),2,bevel=.003)
a.scene['variant_of']='RiverCrossing'
a.scene['variant_purpose']='South bridge threshold: three tapered timber planks, two runners and a crosspiece fitted between the existing bank and bridge beams. Dimensions and shallow ramp are inferred site adaptations.'
a.scene['site_anchor_along_cm']=-371.;a.scene['site_anchor_z_cm']=280.
a.scene['surface_policy']='Reuses the existing RiverBridge packed material atlas unchanged, with physical planks, iron fastenings and bearing timbers.'
a.studio(focus=(.1,0,-.08),location=(2.5,-3.3,3.1),scale=2.9)
a.scene.render.resolution_x=1200;a.scene.render.resolution_y=1000
result=a.save()
(a.review/'source-adaptation.json').write_text(json.dumps({'asset':'BridgeThreshold','variant_of':'RiverCrossing','concept':'SourceAssets/Voxel/river_crossing.png','role':'Close the measured south joint using the bridge timber language; canonical reference is unchanged.','atlas_sources':copied,'planks':planks,'anchor_along_cm':-371,'anchor_z_cm':280,'bank_edge_along_cm':-410,'deck_edge_along_cm':-332,'bank_top_cm':286.8,'deck_top_cm':280.5,'support_design':'Two runners enter the bank around across 26 and 84 cm. The crosspiece seats into the existing under-deck beams at across approximately +/-99 cm.','fidelity_accepted':False},indent=2))
