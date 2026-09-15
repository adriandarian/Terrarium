"""Source-guided static maquettes; dimensions in cm, feet at Z=0, face -Y.

PNG references have no recoverable 3D topology or rigs. Hidden geometry is an
interpretation. Do not use these meshes as animated game characters.
Run build_all() inside the verified Terrarium Unreal editor, serially.
"""
import meshkit
from meshkit import Mesh

ROOT = '/Game/Terrarium/Migration'
SPECS = {
    'brambit': {'mesh': 'SM_Brambit', 'sources': ['brambit.png'], 'category': 'creature', 'notes': 'Three asymmetric leaf shoots; static maquette.'},
    'kindlehorn': {'mesh': 'SM_Kindlehorn', 'sources': ['kindlehorn.png'], 'category': 'creature', 'notes': 'Two pointed ears, cream muzzle and golden horn; static maquette.'},
    'rillip': {'mesh': 'SM_Rillip', 'sources': ['rillip.png'], 'category': 'creature', 'notes': 'Round stepped silhouette, fins and coral cheeks; static maquette.'},
    'player': {'mesh': 'SM_PlayerExplorer', 'sources': ['player_front.png', 'player_back.png'], 'category': 'character', 'notes': 'Single front/back interpretation; static maquette, no atlas animation.'},
    'ranger_sela': {'mesh': 'SM_RangerSela', 'sources': ['ranger_sela.png'], 'category': 'character', 'notes': 'Silver bob, teal long coat, cream scarf, ochre satchel; static maquette.'},
    'moss_tonic': {'mesh': 'SM_MossTonic', 'sources': ['moss_tonic.png'], 'category': 'item', 'notes': 'Physical prop interpretation of UI item icon; opaque palette.'},
    'trail_prism': {'mesh': 'SM_TrailPrism', 'sources': ['trail_prism.png'], 'category': 'item', 'notes': 'Physical prop interpretation of UI item icon; opaque faceted gold.'},
}
REFERENCE_ONLY = ['grove.png', 'ember.png', 'tide.png', 'storm.png', 'ember_crest.png', 'deep_delver_mark.png']


def b(m, pos, size, color, bevel=.6):
    m.box(pos, size, color, bevel)


def eyes(m, xs, y, z, size=4):
    for x in xs:
        b(m, (x, y, z), (size, 2, size*1.3), '20251f', .2)
        b(m, (x-size*.16, y-1.1, z+size*.3), (size*.28, .6, size*.28), 'f0e8ce', .08)


def brambit():
    m = Mesh(SPECS['brambit']['mesh'], 740)
    for x in [-20, 20]:
        for y in [-15, 16]:
            b(m, (x,y,4), (13,14,8), '353c26')
            b(m, (x,y,12), (13,14,12), '987036')
    b(m, (0,0,40), (60,48,49), '96622f', 4)
    b(m, (0,-25,40), (45,4,36), 'd5aa67', 2)
    b(m, (0,-27,25), (28,4,10), 'c39452')
    eyes(m, [-13,13], -28, 45, 5)
    b(m, (0,-31,39), (9,7,5), '342c1d')
    for x,z in [(-26,23),(25,27),(-28,53),(27,54),(-18,62),(18,62)]:
        b(m, (x,-23,z), (10,9,10), 'a16d34')
    for x,y,z,s in [(-22,-4,64,20),(0,4,67,26),(21,2,64,21),(-13,-16,66,17),(15,-15,65,18)]:
        b(m,(x,y,z),(s,s,12),'727d36')
    for x,y,z,height,width in [(-22,3,72,28,20),(2,9,76,43,25),(24,10,70,24,15)]:
        b(m,(x,y,z+height*.25),(6,7,height*.6),'8a8c36')
        for level,w in enumerate([width,width*.76,width*.40]):
            b(m,(x+level*1.6,y,z+height*.55+level*8),(w,12,10),'8d993e' if level%2 else '74862f')
    return m


def kindlehorn():
    m = Mesh(SPECS['kindlehorn']['mesh'], 741)
    for x in [-21,21]:
        for y in [-18,20]:
            b(m,(x,y,4),(15,19,8),'30281d')
            b(m,(x,y,15),(16,18,18),'b95420')
    b(m,(0,3,38),(59,53,48),'c3531a',5)
    b(m,(0,-9,61),(64,47,40),'d0601d',5)
    b(m,(0,-26,36),(32,7,30),'d6b681',3)
    b(m,(0,-35,53),(37,10,17),'e7c991',2)
    b(m,(0,-42,56),(11,6,7),'56402a')
    eyes(m,[-21,21],-34,65,5)
    for x in [-24,24]:
        for z,w in [(82,23),(94,19),(105,13),(115,7)]:
            b(m,(x,1,z),(w,15,13),'be5019')
        b(m,(x,-8,93),(11,3,24),'56351d')
        b(m,(x,-10,86),(9,3,13),'dcc08b')
        b(m,(x*.99,-27,47),(15,9,9),'c15620')
    # Faceted horn with stepped warm-gold collar, no implied emission material.
    b(m,(0,-18,82),(19,19,7),'bf7418')
    m.solid([(-8,-8,0),(8,-8,0),(8,8,0),(-8,8,0),(-3,-3,30),(3,-3,30),(3,3,30),(-3,3,30)],
            [[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],'f6c33a',pos=(0,-18,85))
    for y,z,w in [(29,37,21),(38,46,18),(42,58,13),(43,68,8)]:
        b(m,(0,y,z),(w,15,16),'c6571a')
    b(m,(0,49,54),(9,3,14),'f3a324')
    return m


def rillip():
    m = Mesh(SPECS['rillip']['mesh'], 742)
    for x in [-17,17]:
        b(m,(x,-9,4),(17,26,8),'2c8390')
        for dx in [-4,4]: b(m,(x+dx,-23,4),(7,8,7),'79bcb0')
    for z,w,d,h in [(15,40,31,12),(27,60,45,16),(47,68,50,28),(67,59,44,14),(78,46,36,10),(86,31,25,8)]:
        b(m,(0,0,z),(w,d,h),'398aaa',2)
    b(m,(0,0,93),(18,18,10),'429d9e')
    b(m,(0,0,102),(10,11,9),'e8d8a2')
    for x in [-43,43]:
        b(m,(x,0,39),(22,20,26),'127484',2)
        b(m,(x,-11,39),(16,4,21),'98c9bb')
        b(m,(x*1.15,0,38),(9,17,17),'186875')
    eyes(m,[-19,19],-26,55,6)
    for x in [-27,27]: b(m,(x,-27,43),(10,4,9),'ed846f')
    b(m,(0,-28,35),(23,4,6),'a6d0cc')
    for x in [-14,14]: b(m,(x,-28,40),(6,4,10),'a6d0cc')
    for x,z in [(-21,21),(21,21),(-11,16),(11,16),(0,13)]: b(m,(x,-22,z),(11,4,7),'89bdb5')
    for x,z in [(-20,78),(20,78),(-12,86),(12,86)]: b(m,(x,-16,z),(10,8,5),'aad2c9')
    return m


def humanoid(sela=False):
    key='ranger_sela' if sela else 'player'
    m=Mesh(SPECS[key]['mesh'], 744 if sela else 743)
    coat='285d5a' if sela else 'ba582e'
    skin='bf8645' if sela else 'd89b56'
    scarf='ded0a5' if sela else 'd6a137'
    hair='b7b9a9' if sela else '292923'
    for x in [-13,13]:
        b(m,(x,-5,2),(17,28,4),'343122')
        b(m,(x,-5,9),(17,26,12),'6d502c',2)
        b(m,(x,0,20),(15,18,15),'604828')
        b(m,(x,0,28),(17,19,6),'ac9770')
        b(m,(x,0,49),(16,18,37),'34382e',2)
        b(m,(x,-10,11),(10,2,3),'a48347')
        b(m,(x,-10,20),(10,2,3),'a48347')
    b(m,(0,0,69),(36,23,14),'34382e',2)
    b(m,(0,0,95),(42,28,44),coat,3)
    b(m,(0,-16,95),(20,4,39),'33392f' if sela else 'd9c99f')
    b(m,(0,-18,76),(37,3,6),'665035')
    b(m,(0,-20,76),(8,3,7),'c4b385')
    b(m,(0,-22,76),(4,1,3),'544734')
    for x in [-16,16]:
        b(m,(x,-17,94),(10,6,42),coat)
        if not sela: b(m,(x,-21,97),(10,2,7),scarf)
    # Arms, cuffs, hands. Sela's bent hand rests by the cross-body strap.
    for side in [-1,1]:
        x=side*28
        m.beam((side*22,0,109),(x,-1,91),15,coat)
        end=(side*20,-17,92) if sela and side==1 else (side*30,-4,73)
        m.beam((x,-1,91),end,13,coat)
        b(m,end,(15,15,8),coat)
        b(m,(end[0],end[1]-1,end[2]-8),(11,12,13),skin,2)
    b(m,(0,0,120),(13,14,12),skin,2)
    # Chunky scarf collar and a single long trailing end.
    b(m,(0,0,117),(40,31,8),scarf,2)
    b(m,(0,-18,113),(31,9,11),scarf,2)
    if sela:
        b(m,(8,-20,101),(9,5,24),scarf)
        for x in [-19,19]: b(m,(x,1,64),(12,31,35),coat,2)
        b(m,(0,13,64),(33,6,35),coat,2)
        m.beam((-16,-23,109),(23,-23,72),6,'a27a39',3)
        b(m,(27,-9,66),(19,15,22),'af842f',2)
        b(m,(27,-18,72),(20,3,11),'c19435')
        b(m,(27,-20,67),(5,2,6),'d8c48e')
        b(m,(-30,-7,101),(8,2,11),'b8a168')
    else:
        b(m,(-23,12,93),(8,5,40),scarf)
        for x in [-25,-21]: b(m,(x,12,70),(3,5,8),scarf)
        b(m,(0,22,96),(37,18,38),'354e2b',2)
        b(m,(0,32,109),(39,7,14),'49633c')
        for x in [-10,10]:
            b(m,(x,33,86),(15,5,15),'435e35')
            b(m,(x,37,86),(4,3,14),'796b37')
            b(m,(x,39,86),(6,2,5),'c79b3b')
            b(m,(x*1.7,-18,108),(6,5,18),'3b5430')
    b(m,(0,-1,136),(33,28,31),skin,3)
    for x in [-18,18]: b(m,(x,-1,135),(6,10,11),skin)
    # Head cap, side/back locks, offset block fringe retain source hairstyle.
    b(m,(0,2,151),(38,33,12),hair,2)
    b(m,(0,3,158),(28,25,5),hair)
    for x,z in [(-16,145),(16,144),(-18,137),(18,138)]:
        b(m,(x,4,z),(8,25,14),hair)
    b(m,(0,14,139),(31,7,25),hair)
    for x,z in [(-13,149),(-6,153),(3,151),(12,148)]:
        b(m,(x,-16,z),(9,7,8),hair)
    if sela:
        for x in [-17,17]: b(m,(x,-8,132),(6,14,15),hair)
    for x in [-8,8]:
        b(m,(x,-16,139),(8,2,8),'e9dec1',.2)
        b(m,(x,-17.5,138),(4,1.5,6),'357475' if sela else '3c3425',.2)
        b(m,(x,-17,146),(9,2,2),'555445' if sela else '292923',.2)
    b(m,(0,-18,134),(4,4,4),skin)
    b(m,(0,-16,129),(10,1,1.5),'86552e',.1)
    return m


def moss_tonic():
    m=Mesh(SPECS['moss_tonic']['mesh'],745)
    b(m,(0,0,14),(24,21,28),'21695b',2)
    for x in [-11,11]:
        for y in [-9,9]: b(m,(x,y,14),(3,3,25),'559f87')
    b(m,(0,0,29),(19,17,5),'397f68')
    b(m,(0,0,34),(13,13,7),'28644e')
    b(m,(0,0,38),(17,17,4),'79b894')
    b(m,(0,0,43),(12,12,7),'aa8038')
    b(m,(0,-11,16),(15,2,15),'e5cd8c')
    b(m,(0,0,34),(15,15,2),'bf974b')
    m.beam((8,0,34),(15,-1,26),2,'b79349')
    for z,w in [(29,5),(26,8),(23,9),(20,6),(17,3)]:
        b(m,(15,-3,z),(w,2,4),'849744')
    b(m,(15,-4,24),(1,1,13),'c3b95f',.1)
    return m


def trail_prism():
    m=Mesh(SPECS['trail_prism']['mesh'],746)
    # Convex bicone with square equator; asymmetric face palette from stepped
    # nested smaller solids reads as gold facets without fake translucency.
    m.solid([(0,0,0),(-17,-17,25),(17,-17,25),(17,17,25),(-17,17,25),(0,0,60)],
            [[0,2,1],[0,3,2],[0,4,3],[0,1,4],[5,1,2],[5,2,3],[5,3,4],[5,4,1]],'d7ab30')
    for z,w in [(8,8),(15,15),(22,23),(34,23),(42,16),(49,10),(56,4)]:
        b(m,(0,0,z),(w,w,6),'e4c044')
    for y in [-18,18]: b(m,(0,y,27),(38,4,6),'71612c')
    for x in [-18,18]: b(m,(x,0,27),(4,38,6),'455641')
    for x in [-18,18]:
        for y in [-18,18]:
            b(m,(x,y,27),(8,8,11),'74602b')
            b(m,(x,y-4.2 if y<0 else y+4.2,27),(4,1,5),'f1c846')
    return m


BUILDERS={'brambit':brambit,'kindlehorn':kindlehorn,'rillip':rillip,
          'player':lambda:humanoid(False),'ranger_sela':lambda:humanoid(True),
          'moss_tonic':moss_tonic,'trail_prism':trail_prism}


def build_all():
    """Preserve existing content; bake only missing assets through Unreal APIs."""
    import unreal
    assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
    previous=meshkit.ROOT
    result=[]
    try:
        meshkit.ROOT=ROOT
        for key,builder in BUILDERS.items():
            path=ROOT+'/Meshes/'+SPECS[key]['mesh']
            reused=unreal.EditorAssetLibrary.does_asset_exist(path)
            asset=unreal.load_asset(path) if reused else builder().save()
            assert asset, path
            result.append({'source':SPECS[key]['sources'][0], 'asset':path,
                           'name':SPECS[key]['mesh'], 'status':'reused' if reused else 'built'})
    finally:
        meshkit.ROOT=previous
    return result
