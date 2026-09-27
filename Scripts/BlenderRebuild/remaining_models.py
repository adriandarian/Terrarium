"""Bounded first-pass recipes for missing reference assets; front faces -Y."""
import bpy, math, json, random
from pathlib import Path
from palette_asset import PaletteAsset

ROOT=Path('C:/Users/hello/Projects/Terrarium')

class Model(PaletteAsset):
    def __init__(self,key,source,colors):
        super().__init__(key,source,[(c,.8,.7 if key=='Kindlehorn' and i in [7,8] else 0) for i,c in enumerate(colors)])
        self.material.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0
        self.material.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=1.7

    def block(self,label,p,size,color,grid=.12):
        # Small deterministic offsets stop coincident faces at overlapping voxel
        # assemblies from producing black depth/shading artifacts.
        n=len(self.parts)+1
        p=[v+.0004*math.sin(n*1.37+i*2.1) for i,v in enumerate(p)]
        counts=[max(1,round(s/grid)) for s in size] if grid else [1,1,1]
        # Closed, touching blocks preserve the reference's visible voxel seams.
        for x in range(counts[0]):
            for y in range(counts[1]):
                for z in range(counts[2]):
                    if all(0<i<n-1 for i,n in zip((x,y,z),counts)):continue
                    dims=[s/n for s,n in zip(size,counts)]
                    pos=[p[a]-size[a]/2+(i+.5)*dims[a] for a,i in enumerate((x,y,z))]
                    self.box(label,pos,dims,color,bevel=.002)

    def finish(self,focus,cam,scale):
        self.studio(focus,cam,scale)
        self.scene.render.resolution_x=720;self.scene.render.resolution_y=900
        self.scene.cycles.samples=24
        self.scene['limitations']='Static first pass; no rig or animation. Fidelity requires collection review and user acceptance.'
        self.save()

def kindlehorn():
    a=Model('Kindlehorn','kindlehorn.png',['A94712','C45A16','E67418','783712','E8BC78','F1D29A','291F16','F8B51C','FFE374','160F0A'])
    b=a.block
    b('barrel',(0,.08,.66),(.94,.8,1),0)
    b('chest',(0,-.37,.62),(.58,.14,.62),4)
    b('chest tip',(0,-.39,.29),(.34,.13,.17),5)
    for x in [-.38,.38]:
        for y in [-.29,.42]:
            b('leg',(x,y,.3),(.3,.32,.48),0)
            b('dark hoof',(x,y-.04,.075),(.32,.36,.15),6)
    b('head',(0,-.22,1.23),(1.22,.86,.69),1)
    b('brow',(0,-.28,1.59),(1.05,.72,.16),2)
    for sign in [-1,1]:
        x=sign*.58
        b('cheek',(x,-.17,1.15),(.24,.64,.4),0)
        b('cheek tuft',(sign*.68,-.02,1.31),(.12,.25,.21),2)
        b('lower cheek',(sign*.59,-.49,1.04),(.28,.22,.17),1)
        b('eye',(sign*.39,-.668,1.30),(.10,.06,.16),9,0)
        b('eye catchlight',(sign*.39-.012,-.701,1.35),(.045,.009,.033),5,0)
        # Upright ears: deep dark inset, orange stepped rim, cream inner tuft.
        for z,w in [(1.76,.4),(1.94,.43),(2.12,.32),(2.28,.22),(2.40,.12)]:
            b('ear backing',(sign*.49,.01,z),(w,.21,.22),0)
            if z<2.22:
                b('ear dark inset',(sign*.49,-.107,z),(w*.64,.035,.18),6,0)
                for side in [-1,1]:b('ear rim',(sign*.49+side*w*.43,-.14,z),(w*.18,.12,.19),1,0)
        b('ear cream',(sign*.49,-.158,1.84),(.14,.06,.22),4)
    b('muzzle',(0,-.71,1.08),(.65,.24,.25),5)
    for x in [-.22,.22]:b('muzzle lobe',(x,-.75,1.02),(.25,.24,.22),4)
    b('nose',(0,-.858,1.16),(.21,.1,.105),6,0)
    b('mouth',(0,-.846,1.02),(.24,.03,.032),6,0)
    for z,w,d,col in [(1.69,.27,.3,3),(1.85,.29,.29,7),(2.02,.36,.32,7),(2.18,.25,.25,8),(2.36,.17,.18,7),(2.5,.1,.12,8)]:
        ob=a.box('golden horn',(0,-.39,z),(w,d,.19),col,.002)
    # Small curled flame tail, physically attached to the rump.
    for y,z,w,col in [(.51,.66,.28,0),(.72,.76,.28,1),(.84,.94,.28,2),(.85,1.12,.22,7),(.78,1.29,.17,2)]:
        b('flame tail',(0,y,z),(w,.26,.24),col)
    a.finish((0,0,1.25),(3.6,-6,3.4),2.95)
    return a

def rillip():
    a=Model('Rillip','rillip.png',['287994','368BA4','419AAF','ABD6CE','75BAB1','08767B','E77962','142E36','FFF0C5','247C88'])
    b=a.block
    for z,w,d in [(.27,.72,.57),(.40,.94,.7),(.58,1.10,.80),(.82,1.2,.86),(1.05,1.17,.82),(1.23,1.05,.73),(1.38,.87,.63),(1.51,.66,.49),(1.62,.4,.34)]:
        b('rounded water body',(0,0,z),(w,d,.25),0 if z<1.3 else 1)
    for sign in [-1,1]:
        b('foot',(sign*.28,-.10,.1),(.24,.4,.15),9)
        for x in [-.07,.07]:b('mint toe',(sign*.28+x,-.285,.08),(.11,.08,.11),4,0)
        for x,z,h in [(0,.84,.38),(.12,.83,.45),(.23,.78,.33),(.31,.76,.22)]:
            b('fin rim',(sign*(.64+x),0,z),(.17,.19,h),5)
        for x,z,h in [(0,.84,.25),(.13,.79,.30),(.22,.75,.15)]:
            b('fin mint inset',(sign*(.65+x),-.11,z),(.15,.07,h),3)
        b('eye',(sign*.28,-.442,1.04),(.12,.055,.21),7,0)
        b('eye light',(sign*.28+.015,-.475,1.095),(.061,.015,.086),8,0)
        b('blush',(sign*.43,-.448,.84),(.16,.048,.14),6,0)
        b('smile corner',(sign*.18,-.474,.88),(.10,.045,.12),3,0)
        for x,z in [(.36,.46),(.43,1.36),(.25,1.48)]:b('foam patch',(sign*x,-.36 if z<1 else -.26,z),(.15,.10,.09),3)
    b('smile',(0,-.479,.805),(.33,.043,.09),3,0)
    b('chin foam',(0,-.347,.34),(.32,.07,.11),4)
    for x,y,z in [(0,0,1.74),(-.12,-.04,1.68),(.12,.015,1.69)]:b('crown crest',(x,y,z),(.18,.19,.19),4,0)
    b('cream crown tip',(0,0,1.89),(.17,.18,.18),8,0)
    a.finish((0,0,.97),(3.1,-6,3),2.8)
    return a

def humanoid(sela=False):
    key='RangerSela' if sela else 'Player'
    colors=['B7773E','D99650','22352E','1D2421','735026','9F722F','D9CCA0','225B58','32736E','ACB3A5','815126','F4E7C2','153E3A','D1A553'] if sela else ['CB8A45','EFAF60','272B24','292C25','62421F','947044','DACDA5','B74F26','CD632C','20231E','495A30','F4E7C2','243822','D9A12C']
    a=Model(key,'ranger_sela.png' if sela else 'player_front.png',colors);b=a.block
    # Shared standing anatomy; individually editable clothing, hands, face and equipment.
    for sign in [-1,1]:
        x=sign*.155
        b('boot sole',(x,-.045,.04),(.23,.38,.08),3,.08)
        b('boot toe',(x,-.13,.115),(.22,.25,.12),4,.08)
        b('boot shaft',(x,.015,.23),(.21,.23,.32),4,.08)
        b('boot cuff',(x,.015,.36),(.24,.25,.09),6 if sela else 5,.08)
        for z in [.16,.24,.31]:b('boot fastening',(x,-.12,z),(.13,.045,.035),5,0)
        b('trouser leg',(x,.025,.58),(.23,.24,.43),2,.09)
        b('knee patch',(x,-.11,.59),(.2,.035,.17),3,.085)
    b('hips',(0,0,.81),(.51,.28,.23),3,.085)
    b('shirt',(0,-.015,1.04),(.44,.3,.42),3 if sela else 6,.075)
    b('belt',(0,-.018,.875),(.52,.31,.08),4,.08)
    b('belt buckle',(0,-.182,.877),(.10,.025,.085),6,0)
    b('buckle inset',(0,-.200,.877),(.054,.015,.044),4,0)
    for sign in [-1,1]:
        b('coat front',(sign*.21,-.09,1.025),(.14,.22,.46),7,.075)
        b('shoulder',(sign*.31,0,1.18),(.22,.28,.24),8,.08)
        b('upper sleeve',(sign*.365,0,1.06),(.2,.245,.25),7,.08)
        if sela and sign==1:
            b('bent forearm',(sign*.345,-.145,1.00),(.2,.40,.18),7,.07)
            b('raised hand',(sign*.26,-.32,1.10),(.16,.14,.19),0,.065)
        else:
            b('lower sleeve',(sign*.405,-.02,.86),(.20,.24,.25),7,.08)
            b('cuff',(sign*.412,-.022,.75),(.225,.255,.10),8,.08)
            b('hand',(sign*.414,-.02,.63),(.155,.18,.18),1,.06)
            b('thumb',(sign*.325,-.12,.66),(.055,.08,.10),0,0)
        b('lapel',(sign*.17,-.215,1.20),(.12,.06,.24),8,.06)
        if sela:
            b('long coat skirt',(sign*.255,.0,.68),(.18,.34,.51),7,.085)
            b('coat hem',(sign*.26,0,.425),(.19,.35,.065),8,.085)
            b('ranger shoulder badge',(sign*.434,-.07,1.15),(.035,.14,.15),13,0)
        else:
            b('pack shoulder strap',(sign*.245,-.17,1.12),(.07,.075,.4),10,.07)
            b('jacket gold band',(sign*.215,-.214,1.015),(.15,.03,.075),13,0)
    b('neck',(0,0,1.36),(.19,.2,.17),0,.08)
    b('scarf collar',(0,0,1.315),(.54,.41,.105),6 if sela else 13,.075)
    b('scarf drape',(0,-.23,1.26),(.34,.08,.12),6 if sela else 13,.07)
    if sela:
        b('cream scarf tail',(.07,-.20,1.115),(.13,.07,.29),6,.06)
        # Diagonal satchel strap uses overlapping small blocks.
        for i in range(13):b('crossbody strap',(-.25+i*.044,-.254,1.26-i*.033),(.075,.045,.074),5,0)
        b('satchel',(.39,-.14,.72),(.24,.20,.27),13,.065)
        b('satchel flap',(.39,-.245,.78),(.25,.045,.16),5,.065)
        b('satchel clasp',(.39,-.276,.72),(.05,.025,.08),6,0)
    else:
        b('green backpack',(0,.235,1.08),(.47,.28,.46),10,.085)
        b('backpack flap',(0,.397,1.235),(.48,.07,.18),10,.08)
        for x in [-.125,.125]:
            b('pack pocket',(x,.405,.96),(.20,.075,.18),10,.07)
            b('pack pocket strap',(x,.447,.99),(.041,.025,.2),5,0)
            b('pack buckle',(x,.466,.99),(.07,.025,.05),13,0)
        b('pack flap clasp',(0,.442,1.20),(.075,.035,.09),13,0)
        b('hanging scarf',(-.27,.28,1.03),(.115,.08,.56),13,.06)
        for x in [-.3,-.26,-.22]:b('scarf fringe',(x,.28,.717),(.027,.075,.08),13,0)
    # Head, stepped jaw, ears and independent facial features.
    b('head',(0,-.012,1.60),(.47,.39,.43),1,.075)
    b('jaw',(0,-.042,1.402),(.35,.33,.09),1,.075)
    for sign in [-1,1]:
        b('ear',(sign*.256,-.005,1.55),(.08,.13,.14),0,.06)
        b('eye white',(sign*.113,-.214,1.60),(.102,.027,.096),11,0)
        b('iris',(sign*.11,-.232,1.595),(.048,.015,.071),12 if sela else 9,0)
        b('pupil',(sign*.11,-.242,1.597),(.023,.008,.045),9 if not sela else 3,0)
        b('eyebrow',(sign*.116,-.237,1.68),(.12,.025,.031),3,0)
    b('nose',(0,-.241,1.535),(.061,.067,.053),0,0)
    b('smile',(0,-.218,1.475),(.115,.019,.012),10 if sela else 4,0)
    # Irregular stepped hair cap and a rear volume visible in the player's back reference.
    for z,w,d in [(1.75,.50,.43),(1.81,.55,.45),(1.875,.45,.36),(1.925,.29,.25)]:b('hair crown',(0,.005,z),(w,d,.09),9,.075)
    b('back hair',(0,.178,1.62),(.48,.10,.34),9,.075)
    for sign in [-1,1]:
        for i in range(4 if sela else 2):
            b('side hair',(sign*(.245-.012*i),-.07 if i<2 else -.12,1.72-i*.075),(.082,.24,.10),9,.065)
        for i in range(3):b('fringe',(sign*(.08+i*.07),-.217,1.79-i*.036),(.11,.09,.09),9,.06)
    a.scene['reference_group']=json.dumps(['ranger_sela.png','ranger_sela_animation_atlas.png'] if sela else ['player_front.png','player_back.png','player_animation_atlas.png','player_back_animation_atlas.png'])
    a.finish((0,0,1),(3,-6,2.55),2.3)
    return a

def compound():
    a=Model('HomesteadCompound','homestead_compound.png',['70512D','96602D','BA792E','6D7462','969A7C','278C82','14625D','496529','738B2E','C5AA59','EBD49D','4B3A22','9B521F'])
    b=a.block
    # Reuse the detailed cottage authoring geometry, preserving original UVs/materials.
    with bpy.data.libraries.load(str(ROOT/'SourceAssets/Blender/Cottage/Cottage.blend'),link=False) as (src,dst):
        dst.scenes=['Terrarium_Cottage']
    template=dst.scenes[0]
    import shutil
    shutil.copy2(ROOT/'SourceAssets/Blender/Cottage/Cottage_BaseColor.png',a.out/'Cottage_BaseColor.png')
    for ob in list(template.objects):
        if ob.get('part'):
            new=ob.copy();new.data=ob.data.copy();a.scene.collection.objects.link(new)
            new.location.x-=.65;new.location.y+=1.5;a.parts.append(new)
    bpy.data.scenes.remove(template)
    # Compact teal-roofed timber shed.
    b('shed foundation',(-3.4,-.6,.14),(1.65,1.5,.28),3,.25)
    b('shed walls',(-3.4,-.6,.76),(1.44,1.27,1.12),0,.18)
    for x in [-4.10,-2.70]:b('shed post',(x,-1.26,.83),(.14,.16,1.35),1,.18)
    b('shed door',(-3.4,-1.265,.76),(.77,.09,1.12),11,.13)
    for z in [.3,1.15]:b('shed door brace',(-3.4,-1.325,z),(.87,.08,.11),1,.17)
    for row in range(4):
        for side in [-1,1]:b('teal shed roof',(-3.4+side*(.15+row*.23),-.6,1.85-row*.18),(.31,1.62,.21),5 if row%2 else 6,.24)
    # Two-rail fenced boundary with a broad open foreground approach.
    for x in [-4.5,-3,-1.5,0,1.5,3,4.5]:b('rear fence post',(x,3.6,.62),(.18,.19,1.24),0,.21)
    for z in [.36,.83]:b('rear fence rail',(0,3.6,z),(9,.12,.13),1,.3)
    for y in [-3,-1.5,0,1.5,3]:b('side fence post',(4.5,y,.62),(.19,.18,1.24),0,.21)
    for z in [.36,.83]:b('side fence rail',(4.5,.3,z),(.12,6.6,.13),1,.3)
    # Raised vegetable bed: soil, timber rim, three rows of separate leaf crowns.
    b('garden soil',(1.75,-2.15,.12),(2.45,1.6,.24),11,.25)
    for x in [.48,3.02]:b('garden edge',(x,-2.15,.23),(.12,1.84,.32),1,.22)
    for y in [-3.03,-1.27]:b('garden edge',(1.75,y,.23),(2.65,.12,.32),1,.22)
    for i in range(4):
        for j in range(3):
            x=.8+i*.6;y=-2.73+j*.6
            b('vegetable crown',(x,y,.39),(.35,.31,.24),7,.12)
            b('vegetable crown top',(x-.03,y,.54),(.20,.20,.12),8,.10)
    # Stone and timber lantern shrine, plus freestanding lamppost.
    for z,w,col in [(.15,.95,3),(.4,.80,4),(.67,.64,3),(.91,.51,0),(1.2,.56,0),(1.55,.62,0)]:b('shrine',(3,1,z),(w,w,.29),col,.19)
    b('shrine glowing window',(3,.66,1.48),(.36,.05,.3),10,.12)
    for z,w in [(1.76,.78),(1.92,.56),(2.07,.30)]:b('shrine cap',(3,1,z),(w,w,.17),3,.18)
    b('lamp stone foot',(-.2,-1.7,.12),(.48,.48,.24),3,.18)
    b('lamp post',(-.2,-1.7,.84),(.09,.09,1.35),0,.2)
    b('lamp glass',(-.2,-1.7,1.53),(.24,.24,.31),10,.1)
    for x in [-.35,-.05]:
        for y in [-1.85,-1.55]:b('lamp frame',(x,y,1.55),(.04,.04,.43),11,0)
    b('lamp lid',(-.2,-1.7,1.79),(.39,.39,.13),3,.15)
    for i in range(6):
        b('flowerbed foliage',(3.62,-.70+i*.4,.26),(.38,.40,.34),7,.13)
        b('amber blossom',(3.62,-.70+i*.4,.48),(.15,.17,.12),12,0)
    a.scene['reused_asset']='Cottage; original mesh UVs and material retained'
    a.finish((0,.5,1.3),(10,-16,12),13.6)
    a.scene.render.resolution_x=1000;a.scene.render.resolution_y=900
    return a

def build(key):
    return {'Kindlehorn':kindlehorn,'Rillip':rillip,'Player':humanoid,'RangerSela':lambda:humanoid(True),'HomesteadCompound':compound}[key]()
